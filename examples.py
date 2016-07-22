# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab

"""
examples
~~~~~~~~

README examples

Examples:
    Setup

        >>> import sys
        >>> from json import loads
        >>> from io import StringIO
        >>>
        >>> sys.stderr = sys.stdout


    Hello World

        >>> from pygogo import logger
        >>>
        >>> logger.debug('hello world')
        hello world
        >>> logger.error('hello error')
        hello error
        hello error


    Log based debugging

        >>> import pygogo as gogo
        >>>
        >>> def main(name, verbose=False):
        ...     logger = gogo.Gogo(name, verbose=verbose).logger
        ...     logger.debug('I will log to `stdout` if `verbose` is True')
        ...     logger.info('I will log to `stdout` always')
        ...     logger.warning('I will log to both `stdout` and `stderr`')
        >>>
        >>> main('quite')
        I will log to `stdout` always
        I will log to both `stdout` and `stderr`
        I will log to both `stdout` and `stderr`
        >>> main('verbose', True)
        I will log to `stdout` if `verbose` is True
        I will log to `stdout` always
        I will log to both `stdout` and `stderr`
        I will log to both `stdout` and `stderr`


    Disabled dual logging

        >>> import pygogo as gogo
        >>>
        >>> logger = gogo.Gogo('monolog', monolog=True).logger
        >>> logger.debug('debug message')
        debug message
        >>> logger.info('info message')
        info message
        >>> logger.warning('warning message')
        warning message
        >>> logger.error('error message')
        error message
        >>> logger.critical('critical message')
        critical message


    Using LoggerAdapters to impart contextual information

        >>> import pygogo as gogo
        >>>
        >>> s = StringIO()
        >>> going = gogo.Gogo('context', low_hdlr=gogo.handlers.fileobj_hdlr(s))
        >>> logger = going.get_structured_logger(connid='1234')
        >>> logger.info('log message')
        >>> loads(s.getvalue()) == {'message': 'log message', 'connid': '1234'}
        True


    Implementing structured logging

        >>> import pygogo as gogo
        >>>
        >>> s = StringIO()
        >>> hdlr = gogo.handlers.fileobj_hdlr(s)
        >>> formatter = gogo.formatters.structured_formatter
        >>> kwargs = {
        ...     'low_level': 'info', 'low_formatter': formatter,
        ...     'low_hdlr': hdlr}
        >>> logger = gogo.Gogo('ex.one', **kwargs).logger
        >>> extra = {'set_value': set([1, 2, 3]), 'snowman': '☃'}
        >>> logger.info('log message', extra=extra)
        >>> result = loads(s.getvalue())
        >>> keys = sorted(result.keys())
        >>> keys == [
        ...     'level', 'message', 'msecs', 'name', 'set_value', 'snowman',
        ...     'time']
        True
        >>> blacklist = {'snowman', 'msecs', 'time'}
        >>> [result[k] for k in keys if k not in blacklist] == [
        ...     'INFO', 'log message', 'ex.one.base', [1, 2, 3]]
        True


    Multiple handlers and formatters

        >>> import logging
        >>> import pygogo as gogo
        >>>
        >>> log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        >>> formatter = logging.Formatter(log_format, datefmt='%Y')
        >>>
        >>> logger = gogo.Gogo(
        ...     'ex.two',
        ...     low_hdlr=gogo.handlers.file_hdlr('example2.log', mode='w'),
        ...     low_formatter=formatter,
        ...     high_level='error',
        ...     high_formatter=formatter).logger
        >>>
        >>> logger.debug('debug message')
        >>> logger.info('info message')
        >>> logger.warning('warn message')
        >>> logger.error('error message')  # doctest: +ELLIPSIS
        20... - ex.two.base - ERROR - error message
        >>> logger.critical('critical message')  # doctest: +ELLIPSIS
        20... - ex.two.base - CRITICAL - critical message

        >>> with open('example2.log', encoding='utf-8') as f:
        ...     [line.strip()[5:] for line in f] == [
        ...         '- ex.two.base - DEBUG - debug message',
        ...         '- ex.two.base - INFO - info message',
        ...         '- ex.two.base - WARNING - warn message',
        ...         '- ex.two.base - ERROR - error message',
        ...         '- ex.two.base - CRITICAL - critical message']
        True


    Logging to multiple destinations

        >>> import pygogo as gogo
        >>>
        >>> going = gogo.Gogo(
        ...     'ex.three',
        ...     low_hdlr=gogo.handlers.file_hdlr('example1.log', mode='w'),
        ...     low_formatter=gogo.formatters.fixed_formatter,
        ...     high_level='info',
        ...     high_formatter=gogo.formatters.console_formatter)
        >>>
        >>> logger1 = going.get_logger('area1')
        >>> logger2 = going.get_logger('area2')
        >>> root = going.logger
        >>>
        >>> root.info('Jackdaws love my big sphinx.')
        ex.three.base: INFO     Jackdaws love my big sphinx.
        >>> logger1.debug('Quick zephyrs blow, daft Jim.')
        >>> logger1.info('How daft jumping zebras vex.')
        ex.three.area1: INFO     How daft jumping zebras vex.
        >>> logger2.warning('Jail zesty vixen who pay.')
        ex.three.area2: WARNING  Jail zesty vixen who pay.
        >>> logger2.error('The five boxing wizards jump.')
        ex.three.area2: ERROR    The five boxing wizards jump.
        >>>
        >>> with open('example1.log', encoding='utf-8') as f:
        ...     [line.strip()[24:] for line in f] == [
        ...         'ex.three.base INFO     Jackdaws love my big sphinx.',
        ...         'ex.three.area1 DEBUG    Quick zephyrs blow, daft Jim.',
        ...         'ex.three.area1 INFO     How daft jumping zebras vex.',
        ...         'ex.three.area2 WARNING  Jail zesty vixen who pay.',
        ...         'ex.three.area2 ERROR    The five boxing wizards jump.']
        True


    Reset stderr so logs aren't printed twice

        >>> sys.stderr = sys.__stderr__


    Using Filters to impart contextual information

        >>> import logging
        >>> import pygogo as gogo
        >>>
        >>> levels = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        >>> log_frmt = (
        ...     '%(asctime)-4s %(name)-5s %(levelname)-8s IP: %(ip)-15s User: '
        ...     '%(user)-8s %(message)s')
        >>>
        >>> formatter = logging.Formatter(log_frmt, datefmt='%Y')
        >>> going = gogo.Gogo('a', low_formatter=formatter)
        >>> a1 = going.get_logger('b.c', ip='123.231.231.123', user='fred')
        >>> a2 = going.get_logger('e.f', ip='192.168.0.1', user='sheila')
        >>>
        >>> a1.debug('A debug message')  # doctest: +ELLIPSIS
        20... a.b.c DEBUG    IP: 123.231.231.123 User: fred     A debug message
        >>> a1.info('An info %s', 'message')  # doctest: +ELLIPSIS
        20... a.b.c INFO     IP: 123.231.231.123 User: fred     An info message
        >>>
        >>> for level in [getattr(logging, l) for l in levels]:
        ...     name = logging.getLevelName(level)
        ...     pronoun = 'AN' if name[0] in 'AEIOU' else 'A'
        ...     a2.log(level, '%s %s msg', pronoun, name)  # doctest: +ELLIPSIS
        20... a.e.f DEBUG    IP: 192.168.0.1     User: sheila   A DEBUG msg
        20... a.e.f INFO     IP: 192.168.0.1     User: sheila   AN INFO msg
        20... a.e.f WARNING  IP: 192.168.0.1     User: sheila   A WARNING msg
        20... a.e.f ERROR    IP: 192.168.0.1     User: sheila   AN ERROR msg
        20... a.e.f CRITICAL IP: 192.168.0.1     User: sheila   A CRITICAL msg
"""

from __future__ import (
    absolute_import, division, print_function, unicode_literals)

from builtins import *
