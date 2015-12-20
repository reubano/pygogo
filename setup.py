#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (
    absolute_import, division, print_function, with_statement,
    unicode_literals)

import sys

from os import path as p
from builtins import *

import pygogo
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
license = pygogo.__license__
version = pygogo.__version__
title = pygogo.__title__
description = pkutils.__description__
gh = 'https://github.com/reubano'

if sys.version_info.major == 2:
    requirements.append('future==0.15.2')

setup(
    name=title,
    version=version,
    description=description,
    long_description='%s\n\n%s' % (readme, changes),
    author=pygogo.__author__,
    author_email=pygogo.__email__,
    url='%s/%s' % (gh, title),
    download_url='%s/%s/downloads/%s*.tgz' % (gh, title, title),
    packages=find_packages(exclude=['docs', 'tests']),
    include_package_data=True,
    install_requires=requirements,
    tests_require=dev_requirements,
    test_suite='nose.collector',
    license=license,
    zip_safe=False,
    keywords=[title] + description.split(' '),
    package_data={},
    classifiers=[
        pkutils.LICENSES[license],
        'Development Status :: 3 - Alpha',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
    ],
    platforms=['MacOS X', 'Windows', 'Linux'],
    scripts=[p.join('bin', 'gogo')],
)
