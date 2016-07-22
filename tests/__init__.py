# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab

"""
tests
~~~~~

Provides application unit tests
"""

from __future__ import (
    absolute_import, division, print_function, unicode_literals)

import unittest
import re

from builtins import *

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


class BaseTest(unittest.TestCase):
    def runTest(self, *args, **kwargs):
        pass

    def assertEqualEllipsis(self, expected, actual, marker='...', msg=None):
        """Checks whether actual is equal to expected while ignoring ellipsis
        content.

        # https://gist.github.com/harobed/5845674

        Args:
            expected (scalar): The expected value
            actual (scalar): The actual value

        Example:
            >>> BaseTest().assertEqualEllipsis('foo...bar', 'foo123bar')
        """
        if marker not in expected:
            self.assertEqual(expected, actual, msg)

        replaced = re.escape(expected).replace(re.escape(marker), '(.*?)')

        if re.match(replaced, actual, re.M | re.S) is None:
            self.assertMultiLineEqual(expected, actual, msg)

    def assertIsSubset(self, expected, actual):
        """Checks whether actual is a superset of expected.

        Args:
            expected (scalar): The expected value
            actual (scalar): The actual value

        Example:
            >>> BaseTest().assertIsSubset([1,2], range(5))
        """
        self.assertTrue(set(expected).issubset(actual))

    def assertIsNotSubset(self, expected, actual):
        """Checks whether actual is a superset of expected.

        Args:
            expected (scalar): The expected value
            actual (scalar): The actual value

        Example:
            >>> BaseTest().assertIsNotSubset([11,12], range(5))
        """
        self.assertFalse(set(expected).issubset(actual))
