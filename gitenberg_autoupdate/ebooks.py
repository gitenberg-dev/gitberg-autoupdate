import glob
import logging
import subprocess
import uuid
import os

from pyepub import EPUB
from jinja2 import FileSystemLoader, Environment
from github3.exceptions import UnprocessableEntity, NotFoundError

from gitenberg.metadata.pandata import Pandata

ABOUT = 'about_gitenberg.html'

BUILD_EPUB_SCRIPT = """
#!/bin/sh

function build_epub_from_asciidoc {

    asciidoctor -a toc,idprefix=xx_,version=$1 -b xhtml5 -T ./asciidoctor-htmlbook/htmlbook-autogen/ -d book book.asciidoc -o book.html
    git clone https://github.com/gitenberg-dev/HTMLBook

    # don't risk icluding sample in the product epub
    rm -r ./HTMLBook/samples/

    # make book.html available to jinja2 environment by putting it into templates
    cp book.html asciidoctor-htmlbook/gitberg-machine/templates/

    /usr/bin/python asciidoctor-htmlbook/gitberg-machine/machine.py -o . -m metadata.yaml book.html
    xsltproc -stringparam external.assets.list " " ./HTMLBook/htmlbook-xsl/epub.xsl book.html
    cp ./HTMLBook/stylesheets/epub/epub.css OEBPS
    if [ -e cover.jpg ]; then cp cover.jpg OEBPS/cover.jpg; elif [ -e cover.png ]; then cp cover.png OEBPS/cover.png; fi

    # look for first images directory and one found, copy over to ./OEBPS
    find . -name images -type d | head -n 1 | xargs -I {} mv {} ./OEBPS/
    zip -rX book.epub mimetype
    zip -rX book.epub OEBPS/ META-INF/
    if test -d "OEBPS/images/"; then zip -rX book.epub OEBPS/images/ ;fi
    if [ "$2" != "book" ]; then mv book.epub $2.epub; fi

}

build_epub_from_asciidoc $1 $2
"""

FORMAT_TO_MIMETYPE = {
    'pdf':"application/pdf",
    'epub':"application/epub+zip",
    'mobi':"application/x-mobipocket-ebook",
    'html':"text/html",
    'text':"text/html"
}

logger = logging.getLogger(__name__)

def mimetype(filename):
    ext = filename.split('.')[-1]
    return FORMAT_TO_MIMETYPE.get(ext, '')

def repo_metadata():
    md = Pandata("metadata.yaml")
    cover = None
    for cover in md.covers:
        cover = cover.get('image_path', None)
    return {
        'repo_name': md._repo,
        'version': md._version,
        'title': md.title,
        'author': "; ".join(md.authnames()),
        'author_for_calibre': " & ".join(md.authnames()),
        'cover': cover,
        'book_id': md.identifiers.get('gutenberg', '0')
    }



def source_book(repo_name):

    """
    return the path of document to use as the source for building epub
    """

    repo_id = repo_name.split("_")[-1]
    repo_htm_path = "{repo_id}-h/{repo_id}-h.htm".format(repo_id=repo_id)

    possible_paths = ["book.asciidoc",
                      repo_htm_path,
                      "{}-0.txt".format(repo_id),
                      "{}-8.txt".format(repo_id),
                      "{}.txt".format(repo_id),
                      "{}-pdf.pdf".format(repo_id),
                     ]

    # return the first match

    for path in possible_paths:
        if os.path.exists(path):
            return path

    return None


def build_epub_from_asciidoc(version, epub_title='book'):
    """
    build for asciidoctor input
    """

    fname = "{}.sh".format(uuid.uuid4())

    try:
        f = open(fname, "wb")
        f.write(BUILD_EPUB_SCRIPT.encode('utf-8'))
        f.close()
        os.chmod(fname, 0o0755)

        output = subprocess.check_output("./{fname} {version} {epub_title}".format(
            fname=fname,
            version=version, epub_title=epub_title,
        ), shell=True)
        logger.info(output)
    except Exception as e:
        logger.error(e)
    finally:
        os.remove(fname)

class BuildEpubError(Exception):
    pass

def dequote(text):
    text = text.replace('"', r'\"')
    text = text.replace("'", r"\'")
    text = text.replace('`', r'\`')   
    return text

def build_epub(epub_title='book'):
    logger.info('building epub for %s' % epub_title)
    md = repo_metadata()
    source_path = source_book(md['repo_name'])
    logger.info('using source path %s' % source_path)
    if source_path == 'book.asciidoc':
        return build_epub_from_asciidoc(md['version'], epub_title)
    elif source_path and source_path.endswith('.pdf'):
        os.rename(source_path, 'book.pdf')
        return
    elif source_path:
        cover_option = ' --cover {}'.format(md['cover']) if  md['cover'] else '--generate-cover'
        cmd = u"""ebookmaker --max-depth=3 --make=epub.images --ebook {book_id} --title "{title}" --author "{author}"{cover_option} {source_path}""".format(
            title=dequote(md['title']),
            author=dequote(md['author']),
            cover_option=cover_option,
            source_path=source_path,
            book_id=md['book_id'],
        )
        cmd = cmd.encode('ascii', 'xmlcharrefreplace')
        logger.info('build command: %s' % cmd)

        output = subprocess.check_output(cmd, shell=True)

        # rename epub to book.epub
        epubs = glob.glob("*.epub")
        if not epubs:
            logger.error("no epubs generated")
            raise BuildEpubError('epub build failed')

        # get largest epub file
        epub_file = sorted(epubs, key=os.path.getsize, reverse=True)[0]
        add_gitberg_info(epub_file)

        if epub_file != u"{title}-epub.epub".format(title=md['title']):
            logger.info("actual epub_file: {}".format(epub_file))
    else:
        raise BuildEpubError('no suitable book found')

def add_release(book, version, book_files):
    try:
        release = book.repo().create_release(version)
    except UnprocessableEntity:
        # can't create the release because it already exists
        try:
            release = book.repo().release_from_tag(version)
        except (UnprocessableEntity, NotFoundError):
            logger.error("couldn't make or get release: {}".format(version))
            return

    for book_fn in book_files:
        if os.path.exists(book_fn):
            with open(book_fn, 'rb') as book_file:
                try:
                    release.upload_asset(mimetype(book_fn), book_fn, book_file)
                except UnprocessableEntity:
                    # asset already exists
                    logger.info("asset {} already exists".format(book_fn))
        else:
            logger.info("file does not exist: {}".format(book_fn))

def add_gitberg_info(epub_file_name):
    with open(epub_file_name, 'r+b') as epub_from_file:
        epub = EPUB(epub_from_file, mode='a')
        epub.addpart(make_gitberg_info(), ABOUT, "application/xhtml+xml", 1) #after title, we hope
        epub.writetodisk('book.epub')

def make_gitberg_info():
    metadata = Pandata("metadata.yaml")
    tempdir = os.path.join(os.path.dirname(__file__), 'templates/')
    env = Environment(loader=FileSystemLoader([tempdir, '/',]))
    template = env.get_template(ABOUT)
    return template.render(metadata=metadata)

