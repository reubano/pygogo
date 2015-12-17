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
