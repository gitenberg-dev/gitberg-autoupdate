import gitenberg
from gitenberg import actions
from gitenberg import book

import requests

# amazon SQS says a repo has updates
# prerequisite: repo_name is valid, i.e. Book(repo_name) succeeds
# prerequisite: need config library_path
# prerequisite: need git credentials of some sort?
# processQueuedUpdate("Chatterbox-1906_24324")
def processQueuedUpdate(repo_name, recursed=0):
    # intialize book
    # b = actions.get_cloned_book(repo_name)
    b = actions.get_book(repo_name)
    b.clone_from_github() # if no local version, clones

    # if it previously existed as a local repo, need to pull
    repo = b.local_repo.git
    if not repo.remote('origin'): # must exist
        print "Error no origin for " + str(repo_name)
        return
    repo.remote('origin').pull()
    b.parse_book_metadata() # in case this changed

    # b.fetch() # bad, this fetches from PG, not from git
    # b.make() # bad idea, doesn't check if files already exist

    b.add_covers() # checks for covers, if none, makes one, adds to metadata
    # todo make this cover accessible to website? how?

    b.save_meta() # save the new metadata in yaml format
    # todo send metadata to website
    # response = requests.post(GITENSITE_YAML_URL, unicode(b.meta)) # convert to json?

    # todo build ebook?

    b.local_repo.add_all_files() # untracked only
    repo.git.add(update=True) # tracked ones too

    if(repo.git.status("--porcelain")!=''):
        # made stuff here, need to push
        repo.index.commit("Machine generated yaml, cover")

        # returns a list, one PushInfo per head. We have one head
        ret = repo.remote('origin').push(repo.refs.master)[0]
        if ret.flags & 1024 != 0: #1024 is error
            # todo figure out what errors are what and see if we should push again
            if ret.flags & 128 !=0: # access rights or doesn't exist
                pass
            if False: # change condition to the particular flag which means 'not fast forward'
                if recursed==3:
                    print("cannot handle book: " + str(repo_name))
                else:
                    # possibly there was another repo update? try again
                    b.remove() # removes the book from local storage
                    processQueuedUpdate(repo_name, recursed+1)

            print(ret.summary)
