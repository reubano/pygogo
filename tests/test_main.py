# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab

"""
tests.test_main
~~~~~~~~~~~~~~~

Provides unit tests for the website.
"""

from __future__ import (
    absolute_import, division, print_function, unicode_literals)

import nose.tools as nt
import logging
import sys
import pygogo as gogo

from io import StringIO
from json import loads
from builtins import *
from . import BaseTest

module_logger = gogo.Gogo(__name__).logger
nt.assert_equal_ellipsis = BaseTest().assertEqualEllipsis
nt.assert_is_subset = BaseTest().assertIsSubset
nt.assert_is_not_subset = BaseTest().assertIsNotSubset


def setup_module():
    """site initialization"""
    global initialized
    initialized = True
    module_logger.debug('Main module setup\n')


class TestMain(BaseTest):
    """Main unit tests"""
    cls_initialized = False

    def setUp(self):
        nt.assert_false(self.cls_initialized)
        self.cls_initialized = True
        module_logger.debug('TestMain class setup\n')

    def tearDown(self):
        nt.ok_(self.cls_initialized)
        module_logger.debug('TestMain class teardown\n')

    def test_formatters(self):
        # basic
        sys.stderr = StringIO()
        logger = gogo.Gogo('stderr_if_gt_error', 'error').logger
        logger.warning('stdout')
        logger.error('stderr')

        # json_formatter
        formatter = gogo.formatters.json_formatter
        json_logger = gogo.Gogo('json', low_formatter=formatter).logger
        json_logger.debug('hello')

        # csv_formatter
        formatter = gogo.formatters.csv_formatter
        csv_logger = gogo.Gogo('csv', low_formatter=formatter).logger
        csv_logger.debug('hello')

        # console_formatter
        formatter = gogo.formatters.console_formatter
        console_lggr = gogo.Gogo('console', low_formatter=formatter).logger
        console_lggr.debug('hello')

        console_msg = (
            'stdout\nstderr\n{"time": "20...", "name": "json.base", "level": '
            '"DEBUG", "message": "hello"}\n20...,csv.base,DEBUG,"hello"\n'
            'console.base: DEBUG    hello')

        results = sys.stdout.getvalue().strip()
        nt.assert_equal_ellipsis(console_msg, results)
        nt.assert_equal('stderr', sys.stderr.getvalue().strip())

    def test_handlers(self):
        f = StringIO()
        hdlr = gogo.handlers.fileobj_hdlr(f)
        lggr = gogo.Gogo('test_handlers', high_hdlr=hdlr).logger

        msg1 = 'stdout hdlr only'
        lggr.debug(msg1)
        f.seek(0)
        nt.assert_equal(msg1, sys.stdout.getvalue().strip())
        nt.assert_false(f.read())

        msg2 = 'both hdlrs'
        lggr.error(msg2)
        f.seek(0)
        nt.assert_equal('%s\n%s' % (msg1, msg2), sys.stdout.getvalue().strip())
        nt.assert_equal(f.read().strip(), msg2)

    def test_multiple_loggers(self):
        f = StringIO()

        going = gogo.Gogo(
            'myapp',
            low_hdlr=gogo.handlers.fileobj_hdlr(f),
            low_formatter=gogo.formatters.fixed_formatter,
            high_hdlr=gogo.handlers.stdout_hdlr(),
            high_level='info',
            high_formatter=gogo.formatters.console_formatter)

        root = going.logger
        logger1 = going.get_logger('area1')
        logger2 = going.get_logger('area2')

        root.info('Jackdaws love my big sphinx of quartz.')
        logger1.debug('Quick zephyrs blow, vexing daft Jim.')
        logger1.info('How quickly daft jumping zebras vex.')
        logger2.warning('Jail zesty vixen who grabbed pay.')
        logger2.error('The five boxing wizards jump quickly.')

        console_msg = (
            "myapp.base  : INFO     Jackdaws love my big sphinx of quartz."
            "\nmyapp.area1 : INFO     How quickly daft jumping zebras vex."
            "\nmyapp.area2 : WARNING  Jail zesty vixen who grabbed pay."
            "\nmyapp.area2 : ERROR    The five boxing wizards jump quickly.")

        file_msg = [
            "myapp.base   INFO     Jackdaws love my big sphinx of quartz.\n",
            "myapp.area1  DEBUG    Quick zephyrs blow, vexing daft Jim.\n",
            "myapp.area1  INFO     How quickly daft jumping zebras vex.\n",
            "myapp.area2  WARNING  Jail zesty vixen who grabbed pay.\n",
            "myapp.area2  ERROR    The five boxing wizards jump quickly.\n"]

        f.seek(0)
        nt.assert_equal(console_msg, sys.stdout.getvalue().strip())
        nt.assert_equal([line[24:] for line in f], file_msg)

    def test_params_and_looping(self):
        levels = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        f = StringIO()
        going = gogo.Gogo(low_hdlr=gogo.handlers.fileobj_hdlr(f))
        logger1 = going.get_logger('area1')
        logger2 = gogo.Gogo().get_logger('area2')

        logger1_msg = 'A debug message\nAn info message'
        logger1.debug('A debug message')
        logger1.info('An info %s', 'message')
        f.seek(0)
        nt.assert_equal(f.read().strip(), logger1_msg)
        logger2_msg = ''

        for level in [getattr(logging, l) for l in levels]:
            name = logging.getLevelName(level)
            logger2_msg += '%s message\n' % name
            logger2.log(level, '%s %s', name, 'message')
            # TODO: lookup yielding from a nose test

        nt.assert_equal(logger2_msg.strip(), sys.stdout.getvalue().strip())

    def test_debugging(self):
        console_msg = (
            'This should log\nSo should this\nAnd this too\nThis should log '
            'also\nSo should this\nAnd this too\nBut this one should\nAnd this'
            ' one too')

        logger = gogo.Gogo('debug.none').logger
        logger.debug('This should log')
        logger.info('So should this')
        logger.warning('And this too')

        logger = gogo.Gogo('debug.on', verbose=True).logger
        logger.debug('This should log also')
        logger.info('So should this')
        logger.warning('And this too')

        logger = gogo.Gogo('debug.off', verbose=False).logger
        logger.debug("This shouldn't log")
        logger.info('But this one should')
        logger.warning('And this one too')

        results = sys.stdout.getvalue().strip()
        nt.assert_in("This should log", results)
        nt.assert_not_in("This shouldn't log", results)
        nt.assert_equal(console_msg, results)

    def test_structured_formatter(self):
        console_msg = {
            'snowman': '\u2603', 'name': 'structured_formatter.base',
            'level': 'INFO', 'message': 'log message', 'time': '20...',
            'msecs': '...', 'set_value': [1, 2, 3]}

        log_format = gogo.formatters.BASIC_FORMAT
        skwargs = {'datefmt': '%Y'}
        formatter = gogo.formatters.StructuredFormatter(log_format, **skwargs)

        kwargs = {'low_level': 'info', 'low_formatter': formatter}
        logger = gogo.Gogo('structured_formatter', **kwargs).logger
        extra = {'set_value': set([1, 2, 3]), 'snowman': '\u2603'}
        logger.info('log message', extra=extra)
        result = loads(sys.stdout.getvalue())
        result['msecs'] = str(result['msecs'])
        keys = sorted(result.keys())
        nt.assert_equal(sorted(console_msg.keys()), keys)
        whitelist = {'msecs', 'time'}

        for k in keys:
            f = nt.assert_equal_ellipsis if k in whitelist else nt.assert_equal
            f(console_msg[k], result[k])

    def test_structured_logging(self):
        kwargs = {'persist': True}
        extra = {'additional': True}
        meta = set(['level', 'name', 'time'])

        # Basic structured logger
        logger0 = gogo.Gogo('logger0').get_structured_logger('base', **kwargs)

        # Structured formatter
        formatter = gogo.formatters.structured_formatter
        logger1 = gogo.Gogo('logger1', low_formatter=formatter).logger

        # JSON formatter
        formatter = gogo.formatters.json_formatter
        logger2 = gogo.Gogo('logger2', low_formatter=formatter).logger

        # Custom logger
        logfmt = (
            '{"time": "%(asctime)s.%(msecs)d", "name": "%(name)s", "level":'
            ' "%(levelname)s", "message": "%(message)s", '
            '"persist": "%(persist)s", "additional": "%(additional)s"}')

        fmtr = logging.Formatter(logfmt, datefmt=gogo.formatters.DATEFMT)
        logger3 = gogo.Gogo('logger3', low_formatter=fmtr).get_logger(**kwargs)

        # Now log some messages
        for logger in [logger0, logger1, logger2, logger3]:
            logger.debug('message', extra=extra)

        lines = sys.stdout.getvalue().strip().split('\n')
        results = [loads(l) for l in lines]

        # Assert the following loggers provide the log event meta data
        nt.assert_is_not_subset(meta, results[0])
        nt.assert_is_subset(meta, results[1])
        nt.assert_is_subset(meta, results[2])
        nt.assert_is_subset(meta, results[3])

        # Assert the following loggers provide the `extra` information
        nt.assert_in('additional', results[0])
        nt.assert_in('additional', results[1])
        nt.assert_not_in('additional', results[2])
        nt.assert_in('additional', results[3])

        # Assert the following loggers provide the `persist` information
        nt.assert_in('persist', results[0])
        nt.assert_in('persist', results[1])
        nt.assert_not_in('persist', results[2])
        nt.assert_in('persist', results[3])

        # Assert the following loggers provide the `msecs` in the time
        nt.assert_false(len(results[0].get('time', [])))
        nt.assert_false(len(results[1]['time'][20:]))
        nt.ok_(len(results[2]['time'][20:]))
        nt.ok_(len(results[3]['time'][20:]))

    def test_named_loggers(self):
        sys.stderr = sys.stdout
        logger1 = gogo.Gogo('named').logger
        logger2 = gogo.Gogo('named').logger
        nt.assert_equal(logger1, logger2)

        formatter = gogo.formatters.structured_formatter

        going = gogo.Gogo('named2', low_formatter=formatter)
        logger1 = going.get_logger('foo', test='foo')
        logger2 = going.get_logger('bar', test='bar')
        logger1.debug('message')
        logger2.debug('message')

        for h1, h2 in zip(logger1.handlers, logger2.handlers):
            nt.assert_not_equal(h1, h2)

            for f1, f2 in zip(h1.filters, h2.filters):
                nt.assert_not_equal(f1, f2)

        hdlr = gogo.handlers.stdout_hdlr()
        going = gogo.Gogo('named3', low_hdlr=hdlr, low_formatter=formatter)
        logger1 = going.get_logger('baz', test='baz')
        logger2 = going.get_logger('buzz', test='buzz')

        logger1.debug('message')
        logger2.debug('message')

        for h1, h2 in zip(logger1.handlers, logger2.handlers):
            nt.assert_not_equal(h1, h2)

            for f1, f2 in zip(h1.filters, h2.filters):
                nt.assert_not_equal(f1, f2)

        lines = sys.stdout.getvalue().strip().split('\n')
        nt.assert_not_equal(*(loads(l)['test'] for l in lines[0:2]))
        nt.assert_not_equal(*(loads(l)['test'] for l in lines[2:4]))
