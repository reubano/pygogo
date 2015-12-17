# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab

"""
tests.test_main
~~~~~~~~~~~~~~~

Provides unit tests for the website.
"""

from __future__ import (
    absolute_import, division, print_function, with_statement,
    unicode_literals)

import nose.tools as nt
import logging
import sys
import pygogo as gogo

from StringIO import StringIO

module_logger = gogo.Gogo(__name__).logger


def setup_module():
    """site initialization"""
    global initialized
    initialized = True
    module_logger.debug('Main module setup\n')


class TestMain:
    """Main unit tests"""
    def __init__(self):
        self.cls_initialized = False

    def setUp(self):
        nt.assert_false(self.cls_initialized)
        self.cls_initialized = True
        module_logger.debug('TestMain class setup\n')

    def tearDown(self):
        nt.ok_(self.cls_initialized)
        module_logger.debug('TestMain class teardown\n')

    def test_handlers(self):
        f = StringIO()
        hdlr = gogo.handlers.fileobj_hdlr(f)
        lggr = gogo.Gogo('test_handlers', high_hdlr=hdlr).logger

        msg1 = 'stdout hdlr only'
        lggr.debug(msg1)
        f.seek(0)
        nt.assert_equal(sys.stdout.getvalue().strip(), msg1)
        nt.assert_false(f.read())

        msg2 = 'both hdlrs'
        lggr.error(msg2)
        f.seek(0)
        nt.assert_equal(sys.stdout.getvalue().strip(), '%s\n%s' % (msg1, msg2))
        nt.assert_equal(f.read().strip(), msg2)
