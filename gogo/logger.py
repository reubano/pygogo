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

import sys
import logging


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
    def __init__(self, level, filterfalse=False):
        """Initialization method.

        Args:
            level (int): The logging level.

        Returns:
            New instance of :class:`LogFilter`

        Examples:
            >>> LogFilter(40)  # doctest: +ELLIPSIS
            <gogo.LogFilter object at 0x...>
        """
        self.prim_level = level
        self.filterfalse = filterfalse

    def filter(self, record):
        """Double argument.

        Args:
            record (obj): The event to (potentially) log

        Returns:
            bool: True if the event level is lower than self.prim_level

        Examples:
            >>> LogFilter('piki').filter()
            True
        """
        lessthan = record.levelno < self.prim_level
        return not lessthan if self.filterfalse else lessthan


class Logger(object):
    """A logging class that logs events via different handlers depending on the
    severity

    http://stackoverflow.com/a/28743317/408556

    Attributes:
        name (string): The logger name.
        prim_level (string): The min level to log to primary_hdlr.
        sec_level (string): The min level to log to secondary_hdlr.
        # messages < sec_level          -> ignore
        # sec_level <= messages < prim_level -> secondary_hdlr
        # prim_level <= messages             -> primary_hdlr
    """
    def __init__(self, name, **kwargs):
        """Initialization method.

        Args:
            name (string): The logger name.
            prim_level (string): The min level to log to primary_hdlr.
            sec_level (string): The min level to log to secondary_hdlr.

        Returns:
            New instance of :class:`Logger`

        Examples:
            >>> Logger('name', 'DEBUG') # doctest: +ELLIPSIS
            <gogo.Logger object at 0x...>
        """
        primary_hdlr = logging.StreamHandler(sys.stderr)
        secondary_hdlr = logging.StreamHandler(sys.stdout)

        self.name = name
        self.prim_level = getattr(logging, kwargs.get('level', 'WARNING'))
        self.sec_level = getattr(logging, kwargs.get('sec_level', 'DEBUG'))
        self.multilog = kwargs.get('multilog')
        self.primary_hdlr = kwargs.get('primary_hdlr', primary_hdlr)
        self.secondary_hdlr = kwargs.get('secondary_hdlr', secondary_hdlr)
        assert self.prim_level >= self.sec_level

    @property
    def logger(self):
        """The logger property.

        Returns:
            New instance of :class:`Logger.logger`

        Examples:
            >>> logger = Logger('name').logger
            >>> logger # doctest: +ELLIPSIS
            <gogo.Logger.logger object at 0x...>
            >>> logger.debug('stdout')
            >>> logger.info('stdout')
            >>> logger.warning('stderr')
            >>> logger = Logger('name', 'ERROR', 'INFO').logger
            >>> logger.debug('ignored')
            >>> logger.warning('stdout')
            >>> logger.error('stderr')
        """
        log_filter = LogFilter(self.prim_level, self.multilog)
        fltr_hdlr = self.primary_hdlr if self.multilog else self.secondary_hdlr
        fltr_hdlr.addFilter(log_filter)
        self.secondary_hdlr.setLevel(self.sec_level)
        self.primary_hdlr.setLevel(self.prim_level)

        logger = logging.getLogger(self.name)
        logger.addHandler(self.secondary_hdlr)
        logger.addHandler(self.primary_hdlr)
        return logger
