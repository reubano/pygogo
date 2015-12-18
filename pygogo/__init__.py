# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab

"""
pygogo
~~~~~~

A Python logging library with super powers

Examples:
    basic usage::

        >>> logger = Gogo('basic').logger
        >>> logger.debug('hello world')
        hello world

    intermediate usage::
        >>> formatter = logging.Formatter('IP: %(ip)s - %(message)s')
        >>> kwargs = {'low_formatter': formatter}
        >>> logger = Gogo('intermediate', **kwargs).get_logger(ip='1.1.1.1')
        >>> logger.debug('hello world')
        IP: 1.1.1.1 - hello world

    advanced usage::

        >>> kwargs = {'monolog': True, 'high_hdlr': handlers.stdout_hdlr()}
        >>> logger = Gogo('adv', **kwargs).get_structured_logger(ip='1.1.1.1')
        >>> logger.debug('hello world')
        {"ip": "1.1.1.1", "message": "hello world"}
        >>> logger.error('hello world')
        {"ip": "1.1.1.1", "message": "hello world"}
"""

from __future__ import (
    absolute_import, division, print_function, with_statement,
    unicode_literals)

import logging
import hashlib

from . import formatters, handlers, utils

__version__ = '0.3.0'

__title__ = 'pygogo'
__author__ = 'Reuben Cummings'
__description__ = 'A Python logging library with super powers'
__email__ = 'reubano@gmail.com'
__license__ = 'MIT'
__copyright__ = 'Copyright 2015 Reuben Cummings'


class Gogo(object):
    """A logging class that logs events via different handlers depending on the
    severity

    http://stackoverflow.com/a/28743317/408556

    Attributes:
        name (string): The logger name.
        high_level (string): The min level to log to high_hdlr.
        low_level (string): The min level to log to low_hdlr.
            messages < low_level               -> ignore
            low_level <= messages < high_level -> low_hdlr
            high_level <= messages             -> high_hdlr
    """
    def __init__(self, name='root', high_level=None, low_level=None, **kwargs):
        """Initialization method.

        Args:
            name (string): The logger name.
            high_level (string): The min level to log to high_hdlr
                (default: warning).

            low_level (string): The min level to log to low_hdlr
                (default: debug).

            kwargs (dict): Keyword arguments.

        Kwargs:
            high_hdlr (obj): The high pass log handler (a
                `logging.handlers` instance, default: stderr StreamHandler)

            low_hdlr (obj): The low pass log handler (a
                `logging.handlers` instance, default: stdout StreamHandler).

            high_formatter (obj): The high pass log handler (a
                `logging.handlers` instance, default: stderr StreamHandler)

            low_formatter (obj): The low pass log handler (a
                `logging.handlers` instance, default: stdout StreamHandler).

            monolog (bool): Log high level events only to high pass handler (
                default: False)

        Returns:
            New instance of :class:`Gogo`

        Examples:
            >>> Gogo('name') # doctest: +ELLIPSIS
            <pygogo.Gogo object at 0x...>
        """
        high_level = high_level or 'warning'
        low_level = low_level or 'debug'
        self.high_level = getattr(logging, high_level.upper(), None)
        self.low_level = getattr(logging, low_level.upper(), None)

        if not isinstance(self.high_level, int):
            raise ValueError('Invalid high_level: %s' % self.high_level)
        elif not isinstance(self.low_level, int):
            raise ValueError('Invalid low_level: %s' % self.low_level)
        elif not self.high_level >= self.low_level:
            raise ValueError('high_level must be >= low_level')

        high_hdlr = handlers.stderr_hdlr()
        low_hdlr = handlers.stdout_hdlr()
        formatter = formatters.basic_formatter

        self.name = name
        self.high_hdlr = kwargs.get('high_hdlr', high_hdlr)
        self.low_hdlr = kwargs.get('low_hdlr', low_hdlr)
        self.high_hdlr.setLevel(self.high_level)
        self.low_hdlr.setLevel(self.low_level)
        self.high_formatter = kwargs.get('high_formatter', formatter)
        self.low_formatter = kwargs.get('low_formatter', formatter)

        if kwargs.get('monolog'):
            log_filter = utils.LogFilter(self.high_level)
            self.low_hdlr.addFilter(log_filter)

        self.high_hdlr.setFormatter(self.high_formatter)
        self.low_hdlr.setFormatter(self.low_formatter)

    @property
    def logger(self):
        """The logger property.

        Returns:
            New instance of :class:`Gogo.logger`

        Examples:
            >>> from testfixtures import LogCapture
            >>> logger = Gogo('default').logger
            >>> logger # doctest: +ELLIPSIS
            <logging.Logger object at 0x...>
            >>> logger.debug('stdout')
            stdout
            >>> kwargs = {'low_level': 'info', 'monolog': True}
            >>> logger = Gogo('ignore_if_lt_info', **kwargs).logger
            >>> logger.debug('ignored')
            >>> logger.info('stdout')
            stdout
            >>> logger.info('stdout', extra={'key': 'value'})
            stdout
            >>> with LogCapture() as l:
            ...     logger.warning('sdterr')
            ...     print(l)
            ignore_if_lt_info.base WARNING
              sdterr
            >>> logger = Gogo('stderr_if_gt_error', 'error').logger
            >>> logger.warning('stdout')
            stdout
            >>> with LogCapture() as l:
            ...     logger.error('sdterr')
            ...     print(l)
            sdterr
            stderr_if_gt_error.base ERROR
              sdterr
            >>> formatter = formatters.json_formatter
            >>> json_logger = Gogo('json', low_formatter=formatter).logger
            >>> json_logger.debug('hello')  # doctest: +ELLIPSIS
            ... # doctest: +NORMALIZE_WHITESPACE
            {"time": "20...", "name": "json.base", "level": "DEBUG", "message":
            "hello"}
            >>>
            >>> formatter = formatters.csv_formatter
            >>> csv_logger = Gogo('csv', low_formatter=formatter).logger
            >>> csv_logger.debug('hello')  # doctest: +ELLIPSIS
            20...,csv.base,DEBUG,"hello"
            >>>
            >>> formatter = formatters.console_formatter
            >>> console_lggr = Gogo('console', low_formatter=formatter).logger
            >>> console_lggr.debug('hello')
            console.base: DEBUG    hello
        """
        return self.get_logger('base')

    def get_logger(self, name='logger', **kwargs):
        """Retrieve a named logger.

        Args:
            name (string): The logger name.

        Returns:
            New instance of :class:`Gogo.logger`

        Examples:
            >>> going = Gogo()
            >>> logger = going.get_logger('default')
            >>> logger # doctest: +ELLIPSIS
            <logging.Logger object at 0x...>
            >>> logger.info('from default')
            from default
            >>> going.get_logger('new').info('from new')
            from new
        """
        logger = logging.getLogger('%s.%s' % (self.name, name))

        if kwargs:
            structured_filter = utils.get_structured_filter(**kwargs)
            self.low_hdlr.addFilter(structured_filter)
            self.high_hdlr.addFilter(structured_filter)

        logger.setLevel(self.low_level)
        logger.addHandler(self.low_hdlr)
        logger.addHandler(self.high_hdlr)
        return logger

    def get_structured_logger(self, name=None, **kwargs):
        """Retrieve a structured data logger

        Args:
            name (string): The logger name.
            kwargs (dict): Keyword arguments to include in every log message.

        Returns:
            New instance of :class:`Gogo.formatters.StructuredAdapter`

        Examples
            >>> logger = Gogo('structured').get_structured_logger(all='true')
            >>> logger.debug('hello')
            {"all": "true", "message": "hello"}
            >>> logger.debug('hello', extra={'key': 'value'})
            {"all": "true", "message": "hello", "key": "value"}
        """
        values = frozenset(kwargs.iteritems())
        name = name or hashlib.md5(str(values)).hexdigest()
        logger = logging.getLogger('%s.structured.%s' % (self.name, name))
        logger.setLevel(self.low_level)

        self.low_hdlr.setFormatter(formatters.basic_formatter)
        self.high_hdlr.setFormatter(formatters.basic_formatter)
        logger.addHandler(self.low_hdlr)
        logger.addHandler(self.high_hdlr)
        structured_logger = utils.StructuredAdapter(logger, kwargs)
        return structured_logger
