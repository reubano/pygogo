#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab

"""
tests.test
~~~~~~~~~~

Provides scripttests pygogo CLI functionality.
"""

from __future__ import (
    absolute_import, division, print_function, with_statement,
    unicode_literals)

import sys
import pygogo as gogo

from difflib import unified_diff
from os import path as p
from StringIO import StringIO
from scripttest import TestFileEnvironment
from timeit import default_timer as timer


def main(script, tests, verbose=False, stop=True):
    """ Main method
    Returns 0 on success, 1 on failure
    """
    failures = 0
    level = 'DEBUG' if verbose else 'INFO'
    logger = gogo.Gogo(__name__, low_level=level).logger
    short_script = p.basename(script)
    env = TestFileEnvironment('.scripttest')

    start = timer()

    for pos, test in enumerate(tests):
        num = pos + 1
        opts, arguments, expected = test
        joined_opts = ' '.join(opts)
        joined_args = '"%s"' % '" "'.join(arguments)
        command = "%s %s%s" % (script, joined_opts, joined_args)
        short_command = "%s %s%s" % (short_script, joined_opts, joined_args)
        result = env.run(command, cwd=p.abspath(p.dirname(p.dirname(__file__))))
        output = result.stdout

        try:
            check = open(expected)
        except IOError:
            check = StringIO(expected)
        except TypeError:
            check = StringIO(expected)
            output = bool(output)

        args = [check.readlines(), StringIO(output).readlines()]
        kwargs = {'fromfile': 'expected', 'tofile': 'got'}
        diffs = ''.join(unified_diff(*args, **kwargs))
        passed = not diffs

        if not passed:
            failures += 1
            msg = "ERROR! Output from test #%i:\n  %s\n" % (num, short_command)
            msg += "doesn't match:\n  %s\n" % expected
            msg += diffs if diffs else ''
        else:
            logger.debug(output)
            msg = 'Scripttest #%i: %s ... ok' % (num, short_command)

        logger.info(msg)

        if stop and failures:
            break

    time = timer() - start
    logger.info('%s' % '-' * 70)
    end = 'FAILED (failures=%i)' % failures if failures else 'OK'
    logger.info('Ran %i scripttests in %0.3fs\n\n%s' % (num, time, end))
    sys.exit(failures)

if __name__ == '__main__':
    parent_dir = p.abspath(p.dirname(p.dirname(__file__)))
    script = p.join(parent_dir, 'bin', 'gogo')

    tests = [
        (['--help'], [''], True),
        (['--version'], [''], 'gogo v%s\n' % gogo.__version__),
        ([], ['hello world'], 'hello world\n'),
    ]

    main(script, tests)
