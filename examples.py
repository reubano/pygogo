# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab

"""
examples
~~~~~~~~

README examples

Examples:
    Redirect stderr to stdout

        >>> import sys
        >>> sys.stderr = sys.stdout


    A reimplementation of `Using LoggerAdapters to impart contextual information <https://docs.python.org/2/howto/logging-cookbook.html#using-loggeradapters-to-impart-contextual-information>`_.::

        >>> import pygogo as gogo

        >>> logger = gogo.Gogo(__name__).get_structured_logger(connid='1234')
        >>> logger.info('log message')
        {"message": "log message", "connid": "1234"}


    A reimplementation of `Implementing structured logging <https://docs.python.org/2/howto/logging-cookbook.html#implementing-structured-logging>`_.::

        >>> import pygogo as gogo

        >>> formatter = gogo.formatters.structured_formatter
        >>> kwargs = {'low_level': 'info', 'low_formatter': formatter}
        >>> logger = gogo.Gogo('examples.three', **kwargs).logger
        >>> extra = {'set_value': set([1, 2, 3]), 'snowman': '☃'}
        >>> logger.info('log message', extra=extra)  # doctest: +ELLIPSIS
        ... # doctest: +NORMALIZE_WHITESPACE
        {"snowman": "\\u2603", "name": "examples.three.base", "level": "INFO",
        "message": "log message", "time": "2015...", "msecs": ...,
        "set_value": [1, 2, 3]}


    A reimplementation of `Multiple handlers and formatters <https://docs.python.org/2/howto/logging-cookbook.html#multiple-handlers-and-formatters>`_.::

        >>> import logging
        >>> import pygogo as gogo

        >>> log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        >>> formatter = logging.Formatter(log_format, datefmt='%Y')

        >>> logger = gogo.Gogo(
        ...     'examples.two',
        ...     low_hdlr=gogo.handlers.file_hdlr('example2.log', mode='w'),
        ...     low_formatter=formatter,
        ...     high_level='error',
        ...     high_formatter=formatter).logger

        >>> logger.debug('debug message')
        >>> logger.info('info message')
        >>> logger.warn('warn message')
        >>> logger.error('error message')
        2015 - examples.two.base - ERROR - error message
        >>> logger.critical('critical message')
        2015 - examples.two.base - CRITICAL - critical message

        >>> with open('example2.log') as f:
        ...     [line.strip() for line in f]  # doctest: +NORMALIZE_WHITESPACE
        ['2015 - examples.two.base - DEBUG - debug message',
        '2015 - examples.two.base - INFO - info message',
        '2015 - examples.two.base - WARNING - warn message',
        '2015 - examples.two.base - ERROR - error message',
        '2015 - examples.two.base - CRITICAL - critical message']


    A reimplementation of `Logging to multiple destinations <https://docs.python.org/2/howto/logging-cookbook.html#logging-to-multiple-destinations>`_.::

        >>> import pygogo as gogo

        >>> going = gogo.Gogo(
        ...     'examples.one',
        ...     low_hdlr=gogo.handlers.file_hdlr('example1.log', mode='w'),
        ...     low_formatter=gogo.formatters.fixed_formatter,
        ...     high_level='info',
        ...     high_formatter=gogo.formatters.console_formatter)

        >>> logger1 = going.get_logger('area1')
        >>> logger2 = going.get_logger('area2')
        >>> root = going.logger

        >>> root.info('Jackdaws love my big sphinx.')
        examples.one.base: INFO     Jackdaws love my big sphinx.
        >>> logger1.debug('Quick zephyrs blow, daft Jim.')
        >>> logger1.info('How daft jumping zebras vex.')
        examples.one.area1: INFO     How daft jumping zebras vex.
        >>> logger2.warning('Jail zesty vixen who grabbed pay.')
        examples.one.area2: WARNING  Jail zesty vixen who grabbed pay.
        >>> logger2.error('The five boxing wizards jump.')
        examples.one.area2: ERROR    The five boxing wizards jump.

        >>> with open('example1.log') as f:
        ...     [line.strip() for line in f]  # doctest: +NORMALIZE_WHITESPACE
        ...     # doctest: +ELLIPSIS
        ['2015... examples.one.base INFO     Jackdaws love my big sphinx.',
        '2015... examples.one.area1 DEBUG    Quick zephyrs blow, daft Jim.',
        '2015... examples.one.area1 INFO     How daft jumping zebras vex.',
        '2015... examples.one.area2 WARNING  Jail zesty vixen who grabbed pay.',
        '2015... examples.one.area2 ERROR    The five boxing wizards jump.']


    Reset stderr so logs aren't printed twice

        >>> sys.stderr = sys.__stderr__


    A reimplementation of `Using Filters to impart contextual information <https://docs.python.org/2/howto/logging-cookbook.html#using-filters-to-impart-contextual-information>`_.::

        >>> import logging
        >>> import pygogo as gogo

        >>> levels = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        >>> log_frmt = (
        ...    '%(asctime)-4s %(name)-5s %(levelname)-8s IP: %(ip)-15s User: '
        ...    '%(user)-8s %(message)s')

        >>> formatter = logging.Formatter(log_frmt, datefmt='%Y')
        >>> going = gogo.Gogo('a', low_formatter=formatter)
        >>> a1 = going.get_logger('b.c', ip='123.231.231.123', user='fred')
        >>>
        >>> a2 = going.get_logger('e.f', ip='192.168.0.1', user='sheila')

        >>> a1.debug('A debug message')
        2015 a.b.c DEBUG    IP: 123.231.231.123 User: fred     A debug message
        >>> a1.info('An info %s', 'message')
        2015 a.b.c INFO     IP: 123.231.231.123 User: fred     An info message

        >>> for level in [getattr(logging, l) for l in levels]:
        ...    name = logging.getLevelName(level)
        ...    a2.log(level, 'A %s msg', name)
        2015 a.e.f DEBUG    IP: 192.168.0.1     User: sheila   A DEBUG msg
        2015 a.e.f INFO     IP: 192.168.0.1     User: sheila   A INFO msg
        2015 a.e.f WARNING  IP: 192.168.0.1     User: sheila   A WARNING msg
        2015 a.e.f ERROR    IP: 192.168.0.1     User: sheila   A ERROR msg
        2015 a.e.f CRITICAL IP: 192.168.0.1     User: sheila   A CRITICAL msg
"""

from __future__ import (
    absolute_import, division, print_function, with_statement,
    unicode_literals)
