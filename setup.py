#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from distutils.core import setup

NAME = 'nose2-gae'
VERSION = '0.1.7'
PACKAGES = ['nose2gae']
DESCRIPTION = 'nose2 plugin to run the tests in the Google App Engine environment'
URL = 'https://github.com/udacity/nose2-gae'
LONG_DESCRIPTION = open(
    os.path.join(os.path.dirname(__file__), 'README.rst')).read()

CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: Implementation :: CPython',
    'Operating System :: OS Independent',
    'Topic :: Software Development :: Libraries',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Software Development :: Testing',
]

AUTHOR = 'Attila-Mihály Balázs'
AUTHOR_EMAIL = 'dify.ltd+nose2gae@gmail.com'
KEYWORDS = ['unittest', 'testing', 'tests', 'nose2', 'gae']

params = dict(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=PACKAGES,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    classifiers=CLASSIFIERS,
    keywords=KEYWORDS,
)
setup(**params)

