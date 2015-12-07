# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab

"""
gogo.logger
~~~~~~~~~~~

Loggers

Examples:
    literal blocks::

        python example_google.py

Attributes:
    ENCODING (str): The module encoding
"""

from __future__ import (
    absolute_import, division, print_function, with_statement,
    unicode_literals)

import logging
import hashlib

from gogo import handlers, formatters


class LogFilter(logging.Filter):
    """Filters log messages depending on level
    http://stackoverflow.com/a/28743317/408556

    Attributes:
        level (int): The logging level.
            CRITICAL -> 50
            ERROR    -> 40
            WARNING  -> 30
            INFO     -> 20
            DEBUG    -> 10
            NOTSET   ->  0
    """
    def __init__(self, level):
        """Initialization method.

        Args:
            level (int): The logging level.

        Returns:
            New instance of :class:`LogFilter`

        Examples:
            >>> LogFilter(40)  # doctest: +ELLIPSIS
            <gogo.logger.LogFilter object at 0x...>
        """
        self.prim_level = level

    def filter(self, record):
        """Double argument.

        Args:
            record (obj): The event to (potentially) log

        Returns:
            bool: True if the event level is lower than self.prim_level

        Examples:
            >>> attrs = {'levelno': logging.INFO}
            >>> record = logging.makeLogRecord(attrs)
            >>> LogFilter(40).filter(record)
            True
        """
        return record.levelno < self.prim_level


class Logger(object):
    """A logging class that logs events via different handlers depending on the
    severity

    http://stackoverflow.com/a/28743317/408556

    Attributes:
        name (string): The logger name.
        prim_level (string): The min level to log to primary_hdlr.
        sec_level (string): The min level to log to secondary_hdlr.
            messages < sec_level               -> ignore
            sec_level <= messages < prim_level -> secondary_hdlr
            prim_level <= messages             -> primary_hdlr
    """
    def __init__(self, name, prim_level='warning', sec_level='debug', **kwargs):
        """Initialization method.

        Args:
            name (string): The logger name.
            prim_level (string): The min level to log to primary_hdlr.
            sec_level (string): The min level to log to secondary_hdlr.

        Returns:
            New instance of :class:`Logger`

        Examples:
            >>> Logger('name') # doctest: +ELLIPSIS
            <gogo.logger.Logger object at 0x...>
        """
        self.prim_level = getattr(logging, prim_level.upper(), None)
        self.sec_level = getattr(logging, sec_level.upper(), None)

        if not isinstance(self.prim_level, int):
            raise ValueError('Invalid prim_level: %s' % self.prim_level)
        elif not isinstance(self.sec_level, int):
            raise ValueError('Invalid sec_level: %s' % self.sec_level)
        elif not self.prim_level >= self.sec_level:
            raise ValueError('prim_level must be >= sec_level')

        primary_hdlr = handlers.stderr_hdlr()
        secondary_hdlr = handlers.stdout_hdlr()
        self.name = name
        self.primary_hdlr = kwargs.get('primary_hdlr', primary_hdlr)
        self.secondary_hdlr = kwargs.get('secondary_hdlr', secondary_hdlr)
        self.primary_hdlr.setLevel(self.prim_level)
        self.secondary_hdlr.setLevel(self.sec_level)

        if not kwargs.get('multilog'):
            log_filter = LogFilter(self.prim_level)
            self.secondary_hdlr.addFilter(log_filter)

    @property
    def logger(self):
        """The logger property.

        Returns:
            New instance of :class:`Logger.logger`

        Examples:
            >>> from testfixtures import LogCapture
            >>> logger = Logger('default').logger
            >>> logger # doctest: +ELLIPSIS
            <logging.Logger object at 0x...>
            >>> logger.debug('stdout')
            stdout
            >>> kwargs = {'sec_level': 'info'}
            >>> logger = Logger('ignore_if_less_than_info', **kwargs).logger
            >>> logger.debug('ignored')
            >>> logger.info('stdout')
            stdout
            >>> with LogCapture() as l:
            ...     logger.warning('sdterr')
            ...     print(l)
            ignore_if_less_than_info WARNING
              sdterr
            >>> logger = Logger('stdout_if_less_than_error', 'error').logger
            >>> logger.warning('stdout')
            stdout
            >>> with LogCapture() as l:
            ...     logger.error('sdterr')
            ...     print(l)
            stdout_if_less_than_error ERROR
              sdterr
        """
        logger = logging.getLogger(self.name)
        logger.setLevel(self.sec_level)
        logger.addHandler(self.secondary_hdlr)
        logger.addHandler(self.primary_hdlr)
        return logger

    def hash(self, content):
        return hashlib.md5(str(content)).hexdigest()

    def structured_logger(self, name=None, **kwargs):
        """

        Examples
            >>> logger = Logger('default').structured_logger(key2='value2')
            >>> logger.debug('hello', extra={'key': 'value'})
            {"key2": "value2", "message": "hello", "key": "value"}
        """
        values = frozenset(kwargs.iteritems())
        name = name or self.hash(values)
        logger = logging.getLogger('%s.structured.%s' % (self.name, name))
        logger.setLevel(self.sec_level)

        self.secondary_hdlr.setFormatter(formatters.basic_formatter)
        self.primary_hdlr.setFormatter(formatters.basic_formatter)
        logger.addHandler(self.secondary_hdlr)
        logger.addHandler(self.primary_hdlr)
        structured_logger = formatters.StructuredAdapter(logger, kwargs)
        return structured_logger

    def formatted_logger(self, formatter, name=None):
        """

        Examples
            >>> formatter = formatters.json_formatter
            >>> json_logger = Logger('default').formatted_logger(formatter)
            >>> json_logger.debug('hello')  # doctest: +ELLIPSIS
            {"time": "2015...", "name": "default.formatted.22db55...", \
"level": "DEBUG", "message": "hello"}
            >>>
            >>> formatter = formatters.csv_formatter
            >>> csv_logger = Logger('default').formatted_logger(formatter)
            >>> csv_logger.debug('hello')  # doctest: +ELLIPSIS
            2015...,default.formatted.bde4c...,DEBUG,"hello"
            >>>
            >>> args = (formatters.console_formatter, 'console')
            >>> console_logger = Logger('default').formatted_logger(*args)
            >>> console_logger.debug('hello')
            default.formatted.console: DEBUG    hello
        """
        values = frozenset(formatter.__dict__.iteritems())
        name = name or self.hash(values)
        logger = logging.getLogger('%s.formatted.%s' % (self.name, name))
        logger.setLevel(self.sec_level)

        self.secondary_hdlr.setFormatter(formatter)
        self.primary_hdlr.setFormatter(formatter)
        logger.addHandler(self.secondary_hdlr)
        logger.addHandler(self.primary_hdlr)
        return logger
