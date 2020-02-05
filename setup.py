#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

from setuptools import setup


with open('gitenberg_autoupdate/__init__.py', 'r') as fd:
    reg = re.compile(r'__version__ = [\'"]([^\'"]*)[\'"]')
    for line in fd:
        m = reg.match(line)
        if m:
            __version__ = m.group(1)
            break

setup(name='gitberg.autoupdate',
      version=__version__,
      description="A program for updating information within the GITenberg books project",
      long_description=open('README.md').read(),
      license='GPLv3',
      author='Brian Silverman and Marc Gotliboym',
      author_email='bsilver16384@gmail.com and mgotliboym@gmail.com',
      url='https://github.com/gitenberg-dev/gitberg-autoupdate',
      packages=['gitenberg_autoupdate'],
      include_package_data=True,
      scripts=['bin/webhook_server', 'bin/autoupdate_worker', 'bin/queue_manager'],
      setup_requires=[
        'sh>=1',
      ],
      install_requires=[
          'requests>=2.7',
          'github3.py>=0.9.0',
          'GitPython>=2.0.0',
          'docopt>=0.6',
          'six>=1.10.0',
          'PyYAML>=5.1',
          'boto3',
          'gitberg>=0.7.0',
          'pyepub>=0.5.0',
          'jinja2',
      ],
      test_suite='nose.collector',
      tests_require=[
          'nose',
      ],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Programming Language :: Python :: 3.6',
      ],
      keywords="books ebooks gitenberg gutenberg epub metadata",
      )
