#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab

"""
tests.test
~~~~~~~~~~

Provides scripttests gogo CLI functionality.
"""

from __future__ import (
    absolute_import, division, print_function, with_statement,
    unicode_literals)

import sys

from difflib import unified_diff
from os import path as p
from StringIO import StringIO
from scripttest import TestFileEnvironment
from timeit import default_timer as timer

from gogo import __version__ as version

parent_dir = p.abspath(p.dirname(p.dirname(__file__)))
data_dir = p.join(parent_dir, 'data')
script = p.join(parent_dir, 'bin', 'gogo')
short_script = 'gogo'


def main(verbose=False, stop=True):
    """ Main method
    Returns 0 on success, 1 on failure
    """
    ok = True
    start = timer()
    env = TestFileEnvironment('.scripttest')
    usage = 'usage: gogo <command> [<args>]'

    tests = [
        (2, ['--help'], usage),
        (3, ['--version'], 'gogo v%s' % version),
        (4, ['gogo', p.join(data_dir, 'input')], p.join(data_dir, 'output')),
    ]

    for test_num, args, expected in tests:
        command = '%s %s' % (script, ' '.join(args))
        short_command = '%s %s' % (short_script, ' '.join(args))
        result = env.run(command, cwd=parent_dir)
        output = result.stdout

        try:
            check = open(expected)
        except IOError:
            diffs = False
            passed = output == expected
        else:
            args = [check.readlines(), StringIO(output).readlines()]
            kwargs = {'fromfile': 'expected', 'tofile': 'got'}
            diffs = list(unified_diff(*args, **kwargs))
            passed = not diffs

        if not passed:
            ok = False
            msg = "ERROR from test #%i! Output from:\n\t%s\n" % (
                test_num, short_command)
            msg += "doesn't match \n\t%s\n" % result
            msg += diffs if diffs else ''
            pfunc = sys.exit if stop else sys.stderr.write
        else:
            if verbose:
                print(output)

            msg = 'Scripttest #%i: %s ... ok' % (test_num, short_command)
            pfunc = sys.stdout.write

        pfunc(msg)

    time = timer() - start
    print('%s' % '-' * 70)
    end = 'OK' if ok else 'ERRORS'
    print('Ran %i scripttests in %0.3fs\n\n%s' % (test_num, time, end))
    sys.exit(0)

if __name__ == '__main__':
    main()
