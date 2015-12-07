# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab

"""
pygogo.logger
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

from pygogo import handlers, formatters


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
            <pygogo.logger.LogFilter object at 0x...>
        """
        self.high_level = level

    def filter(self, record):
        """Double argument.

        Args:
            record (obj): The event to (potentially) log

        Returns:
            bool: True if the event level is lower than self.high_level

        Examples:
            >>> attrs = {'levelno': logging.INFO}
            >>> record = logging.makeLogRecord(attrs)
            >>> LogFilter(40).filter(record)
            True
        """
        return record.levelno < self.high_level


class Logger(object):
    """A logging class that logs events via different handlers depending on the
    severity

    http://stackoverflow.com/a/28743317/408556

    Attributes:
        name (string): The logger name.
        high_level (string): The min level to log to high_pass_hdlr.
        low_level (string): The min level to log to low_pass_hdlr.
            messages < low_level               -> ignore
            low_level <= messages < high_level -> low_pass_hdlr
            high_level <= messages             -> high_pass_hdlr
    """
    def __init__(self, name, high_level='warning', low_level='debug', **kwargs):
        """Initialization method.

        Args:
            name (string): The logger name.
            high_level (string): The min level to log to high_pass_hdlr.
            low_level (string): The min level to log to low_pass_hdlr.
            kwargs (dict): Keyword arguments.

        Kwargs:
            high_pass_hdlr (obj): The high pass log handler (a
                `logging.handlers` instance, default: stderr StreamHandler)

            low_pass_hdlr (obj): The low pass log handler (a
                `logging.handlers` instance, default: stdout StreamHandler).

            monolog (bool): Log high level events only to high pass handler (
                default: False)

        Returns:
            New instance of :class:`Logger`

        Examples:
            >>> Logger('name') # doctest: +ELLIPSIS
            <pygogo.logger.Logger object at 0x...>
        """
        self.high_level = getattr(logging, high_level.upper(), None)
        self.low_level = getattr(logging, low_level.upper(), None)

        if not isinstance(self.high_level, int):
            raise ValueError('Invalid high_level: %s' % self.high_level)
        elif not isinstance(self.low_level, int):
            raise ValueError('Invalid low_level: %s' % self.low_level)
        elif not self.high_level >= self.low_level:
            raise ValueError('high_level must be >= low_level')

        high_pass_hdlr = handlers.stderr_hdlr()
        low_pass_hdlr = handlers.stdout_hdlr()
        self.name = name
        self.high_pass_hdlr = kwargs.get('high_pass_hdlr', high_pass_hdlr)
        self.low_pass_hdlr = kwargs.get('low_pass_hdlr', low_pass_hdlr)
        self.high_pass_hdlr.setLevel(self.high_level)
        self.low_pass_hdlr.setLevel(self.low_level)

        if kwargs.get('monolog'):
            log_filter = LogFilter(self.high_level)
            self.low_pass_hdlr.addFilter(log_filter)

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
            >>> kwargs = {'low_level': 'info', 'monolog': True}
            >>> logger = Logger('ignore_if_lt_info', **kwargs).logger
            >>> logger.debug('ignored')
            >>> logger.info('stdout')
            stdout
            >>> with LogCapture() as l:
            ...     logger.warning('sdterr')
            ...     print(l)
            ignore_if_lt_info WARNING
              sdterr
            >>> logger = Logger('stderr_if_gt_error', 'error').logger
            >>> logger.warning('stdout')
            stdout
            >>> with LogCapture() as l:
            ...     logger.error('sdterr')
            ...     print(l)
            sdterr
            stderr_if_gt_error ERROR
              sdterr
        """
        logger = logging.getLogger(self.name)
        logger.setLevel(self.low_level)
        logger.addHandler(self.low_pass_hdlr)
        logger.addHandler(self.high_pass_hdlr)
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
        logger.setLevel(self.low_level)

        self.low_pass_hdlr.setFormatter(formatters.basic_formatter)
        self.high_pass_hdlr.setFormatter(formatters.basic_formatter)
        logger.addHandler(self.low_pass_hdlr)
        logger.addHandler(self.high_pass_hdlr)
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
        logger.setLevel(self.low_level)

        self.low_pass_hdlr.setFormatter(formatter)
        self.high_pass_hdlr.setFormatter(formatter)
        logger.addHandler(self.low_pass_hdlr)
        logger.addHandler(self.high_pass_hdlr)
        return logger
