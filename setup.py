#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (
    absolute_import, division, print_function, with_statement,
    unicode_literals)

import sys

from os import path as p
from builtins import *

import pygogo as module
import pkutils

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

sys.dont_write_bytecode = True
requirements = list(pkutils.parse_requirements('requirements.txt'))
dev_requirements = list(pkutils.parse_requirements('dev-requirements.txt'))
readme = pkutils.read('README.rst')
changes = pkutils.read('CHANGES.rst').replace('.. :changelog:', '')
license = module.__license__
version = module.__version__
project = module.__title__
description = module.__description__
user = 'reubano'

if sys.version_info.major == 2:
    requirements.append('future==0.15.2')

setup(
    name=project,
    version=version,
    description=description,
    long_description='%s\n\n%s' % (readme, changes),
    author=module.__author__,
    author_email=module.__email__,
    url=pkutils.get_url(project, user),
    download_url=pkutils.get_dl_url(project, user, version),
    packages=find_packages(exclude=['docs', 'tests']),
    include_package_data=True,
    package_data={},
    install_requires=requirements,
    test_suite='nose.collector',
    tests_require=dev_requirements,
    license=license,
    zip_safe=False,
    keywords=[project] + description.split(' '),
    classifiers=[
        pkutils.LICENSES[license],
        'Development Status :: 3 - Alpha',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Environment :: Console',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
    ],
    platforms=['MacOS X', 'Windows', 'Linux'],
    scripts=[p.join('bin', 'gogo')],
)
