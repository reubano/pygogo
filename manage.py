#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab

""" A script to manage development tasks """

from __future__ import (
    absolute_import, division, print_function, with_statement,
    unicode_literals)

from os import path as p
from manager import Manager
from subprocess import call

manager = Manager()
_basedir = p.dirname(__file__)


@manager.command
def clean():
    """Remove Python file and build artifacts"""
    call(p.join(_basedir, 'helpers', 'clean'))


@manager.command
def check():
    """Check staged changes for lint errors"""
    call(p.join(_basedir, 'helpers', 'check-stage'))


@manager.arg('where', 'w', help='Modules to check')
@manager.arg('strict', 's', help='Check with pylint')
@manager.command
def lint(where=None, strict=False):
    """Check style with linters"""
    call(['flake8', where] if where else 'flake8')

    if strict:
        args = 'pylint --rcfile=tests/standard.rc -rn -fparseable pygogo'
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
@manager.command
def test(where=None, stop=False):
    """Run nose and script tests"""
    opts = '-xv' if stop else '-v'
    opts += 'w %s' % where if where else ''
    call([p.join(_basedir, 'helpers', 'test'), opts])


@manager.command
def tox():
    """Run tests on every Python version with tox"""
    call('tox')


@manager.command
def docs():
    """Generate Sphinx HTML documentation, including API docs"""
    call(p.join(_basedir, 'helpers', 'docs'))


@manager.command
def register():
    """Register package with PyPI"""
    call('python %s register' % p.join(_basedir, 'setup.py'), shell=True)


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
    call('twine upload %s' % p.join(_basedir, 'dist', '*'), shell=True)


@manager.command
def sdist():
    """Create a source distribution package"""
    call(p.join(_basedir, 'helpers', 'srcdist'))


@manager.command
def wheel():
    """Create a wheel package"""
    call(p.join(_basedir, 'helpers', 'wheel'))


if __name__ == '__main__':
    manager.main()
