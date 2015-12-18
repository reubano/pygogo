# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab

"""
tests
~~~~~

Provides application unit tests
"""

from __future__ import (
    absolute_import, division, print_function, with_statement,
    unicode_literals)

import unittest
import re
import pygogo as gogo

module_logger = gogo.Gogo(__name__).logger
initialized = False


def setup_package():
    """database context creation"""
    global initialized
    initialized = True
    module_logger.debug('Package Setup\n')


def teardown_package():
    """database context removal"""
    global initialized
    initialized = False
    module_logger.debug('Package Teardown\n')


# https://gist.github.com/harobed/5845674
class BaseTest(unittest.TestCase):
    def runTest(self, *args, **kwargs):
        pass

    def assertEqualEllipsis(self, first, second, marker='...', msg=None):
        """
        Example :
            >>> BaseTest().assertEqualEllipsis('foo123bar', 'foo...bar')
        """
        if marker not in second:
            self.assertEqual(first, second, msg)

        replaced = re.escape(second).replace(re.escape(marker), '(.*?)')
        if re.match(replaced, first, re.M | re.S) is None:
            self.assertMultiLineEqual(first, second, msg)

    def assertIsSubset(self, expected, actual):
        """Checks whether actual is a superset of expected.

        Example :
            >>> BaseTest().assertIsSubset([1,2], range(5))
        """
        self.assertTrue(set(expected).issubset(actual))

    def assertIsNotSubset(self, expected, actual):
        """Checks whether actual is a superset of expected.

        Example :
            >>> BaseTest().assertIsNotSubset([11,12], range(5))
        """
        self.assertFalse(set(expected).issubset(actual))
