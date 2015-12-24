#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab

""" A script to manage development tasks """

from __future__ import (
    absolute_import, division, print_function, with_statement,
    unicode_literals)

from os import path as p
from subprocess import call

from builtins import *
from manager import Manager

manager = Manager()
BASEDIR = p.dirname(__file__)


@manager.command
def clean():
    """Remove Python file and build artifacts"""
    call(p.join(BASEDIR, 'helpers', 'clean'))


@manager.command
def check():
    """Check staged changes for lint errors"""
    call(p.join(BASEDIR, 'helpers', 'check-stage'))


@manager.arg('where', 'w', help='Modules to check')
@manager.arg('strict', 's', help='Check with pylint')
@manager.command
def lint(where=None, strict=False):
    """Check style with linters"""
    call(['flake8', where] if where else 'flake8')
    args = 'pylint --rcfile=tests/standard.rc -rn -fparseable pygogo'
    call(args.split(' ') + ['--py3k'])

    if strict:
        call(args.split(' '))


@manager.command
def pipme():
    """Install requirements.txt"""
    call('pip install -r requirements.txt'.split(' '))


@manager.command
def require():
    """Create requirements.txt"""
    cmd = 'pip freeze -l | grep -vxFf dev-requirements.txt > requirements.txt'
    call(cmd, shell=True)


@manager.arg('where', 'w', help='test path', default=None)
@manager.arg(
    'stop', 'x', help='Stop after first error', type=bool, default=False)
@manager.arg('tox', 't', help='Run tox tests')
@manager.command
def test(where=None, stop=False, tox=False):
    """Run nose, tox, and script tests"""
    if tox:
        call('tox')
    else:
        opts = '-xv' if stop else '-v'
        opts += 'w %s' % where if where else ''
        call(('nosetests %s' % opts).split(' '))
        call(['python', p.join(BASEDIR, 'tests', 'test.py')])


@manager.command
def docs():
    """Generate Sphinx HTML documentation, including API docs"""
    call(p.join(BASEDIR, 'helpers', 'docs'))


@manager.command
def register():
    """Register package with PyPI"""
    call('python %s register' % p.join(BASEDIR, 'setup.py'), shell=True)


@manager.command
def release():
    """Package and upload a release"""
    sdist()
    wheel()
    upload()


@manager.command
def build():
    """Create a source distribution and wheel package"""
    sdist()
    wheel()


@manager.command
def upload():
    """Upload distribution files"""
    call('twine upload %s' % p.join(BASEDIR, 'dist', '*'), shell=True)


@manager.command
def sdist():
    """Create a source distribution package"""
    call(p.join(BASEDIR, 'helpers', 'srcdist'))


@manager.command
def wheel():
    """Create a wheel package"""
    call(p.join(BASEDIR, 'helpers', 'wheel'))


if __name__ == '__main__':
    manager.main()
