#!/usr/bin/python

from __future__ import print_function

import os
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile

if len(sys.argv) < 1:
  print('Need an argument saying which image', file=sys.stderr)
  sys.exit(1)

image = sys.argv[1]
print('Making deploy zip for %s' % image)

class TemporaryDirectory(object):
  """Simplified version of Python 3's tempfile.TemporaryDirectory."""
  def __init__(self):
    self._closed = False
    self.name = None
    self.name = tempfile.mkdtemp()

  def __enter__(self):
    return self.name

  def __exit__(self, exc, value, tb):
    shutil.rmtree(self.name)

with TemporaryDirectory() as temp:
  git_archive_name = os.path.join(temp, 'git_archive.zip')
  subprocess.check_call(('git', 'archive', '--format=zip',
                         '-o', git_archive_name, 'HEAD'))
  deploy_archive_name = os.path.join(temp, 'deploy.zip')
  deploy_image_path = os.path.join('deploy', image)
  with zipfile.ZipFile(git_archive_name, 'r') as git_archive:
    with zipfile.ZipFile(deploy_archive_name, 'w') as deploy_archive:
      for info in git_archive.infolist():
        if info.filename.startswith(deploy_image_path):
          if info.filename == deploy_image_path + '/':
            output_path = None
          else:
            # No need to preserve permissions on these, so just use the name.
            output_path = info.filename[len(deploy_image_path) + 1:]
        else:
          # Use the whole ZipInfo object to preserve executable permissions etc.
          output_path = info
        if output_path is not None:
          with git_archive.open(info) as f:
            contents = f.read()
          deploy_archive.writestr(output_path, contents)
  output_name = 'deploy-%s-%d.zip' % (image, time.time())
  shutil.copyfile(deploy_archive_name, output_name)
  print('Created %s' % output_name)
