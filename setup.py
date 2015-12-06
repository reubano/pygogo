#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import gogo
import pkutils

from os import p

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

sys.dont_write_bytecode = True
requirements = list(pkutils.parse_requirements('requirements.txt'))
dependencies = list(pkutils.parse_requirements('requirements.txt', dep=True))
dev_requirements = list(pkutils.parse_requirements('dev-requirements.txt'))
readme = pkutils.read('README.rst')
changes = pkutils.read('CHANGES.rst').replace('.. :changelog:', '')
license = gogo.__license__
version = gogo.__version__
title = gogo.__title__
gh = 'https://github.com/reubano'

setup(
    name=title,
    version=version,
    description=gogo.__description__,
    long_description=readme + '\n\n' + changes,
    author=gogo.__author__,
    author_email=gogo.__email__,
    url='%s/%s' % (gh, title),
    download_url='%s/%s/downloads/%s*.tgz' % (gh, title, title),
    packages=find_packages(exclude=['docs', 'tests']),
    include_package_data=True,
    install_requires=requirements,
    dependency_links=dependencies,
    tests_require=dev_requirements,
    license=license,
    zip_safe=False,
    keywords=[title],
    package_data={},
    classifiers=[
        pkutils.LICENSES[license],
        'Development Status :: 2 - Pre-Alpha',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
    ],
    platforms=['MacOS X', 'Windows', 'Linux'],
    scripts=[p.join('bin', 'gogo')],
)
