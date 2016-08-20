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

        >>> from io import StringIO
        >>> from json import loads
        >>>
        >>> high = StringIO()
        >>> low = StringIO()
        >>> kwargs = {
        ...     'monolog': True, 'high_hdlr': handlers.fileobj_hdlr(high),
        ...     'low_hdlr': handlers.fileobj_hdlr(low)}
        >>> logger = Gogo('adv', **kwargs).get_structured_logger(ip='1.1.1.1')
        >>> logger.debug('debug')
        >>> logger.error('error')
        >>> loads(low.getvalue()) == {'ip': '1.1.1.1', 'message': 'debug'}
        True
        >>> loads(high.getvalue()) == {'ip': '1.1.1.1', 'message': 'error'}
        True
"""

from __future__ import (
    absolute_import, division, print_function, unicode_literals)

import logging
import hashlib
import sys

from copy import copy
from builtins import *
from . import formatters, handlers, utils

__version__ = '0.9.1'

__all__ = ['formatters', 'handlers', 'utils']
__title__ = 'pygogo'
__author__ = 'Reuben Cummings'
__description__ = 'A Python logging library with super powers'
__email__ = 'reubano@gmail.com'
__license__ = 'MIT'
__copyright__ = 'Copyright 2015 Reuben Cummings'

module_hdlr = logging.StreamHandler(sys.stdout)
module_fltr = logging.Filter(name='%s.init' % __name__)

# prevent handler from logging `pygogo.main` events
module_hdlr.addFilter(module_fltr)
module_logger = logging.getLogger(__name__)
module_logger.addHandler(module_hdlr)


class Gogo(object):
    """A logging class that logs events via different handlers depending on the
    severity

    http://stackoverflow.com/a/28743317/408556

    Attributes:
        loggers (set[str]): Set of existing loggers

        monolog (bool): Log high level events only to high pass handler.

        name (string): The logger name.

        levels (dict): The min levels to log to handlers.

        handlers (dict): The high/low pass log handlers.

        formatters (dict): The high/low pass log formatter.

        +------------------------------------+-----------------+
        | messages level                     | message handler |
        +====================================+=================+
        | < levels['low']                    | none            |
        +------------------------------------+-----------------+
        | >= levels['low'], < levels['high'] | low handler     |
        +------------------------------------+-----------------+
        | >= levels['high']                  | both handlers * |
        +------------------------------------+-----------------+

        * This is the case when :attr:`monolog` is `False`. If :attr:`monolog`
          is True, then :attr:`handlers['high']` will be the only
          message handler

    Args:
        name (string): The logger name.

        high_level (string): The min level to log to high_hdlr
            (default: warning).

        low_level (string): The min level to log to low_hdlr
            (default: debug).

        kwargs (dict): Keyword arguments.

    Kwargs:
        high_hdlr (obj): The high pass log handler (a :class:`logging.handlers`
            instance, default: `stderr` StreamHandler).

        low_hdlr (obj): The low pass log handler (a :class:`logging.handlers`
            instance, default: `stdout` StreamHandler).

        high_formatter (obj): The high pass log formatter (a
            :class:`logging.Formatter` instance, default:
            :data:`pygogo.formatters.basic_formatter`).

        low_formatter (obj): The low pass log formatter (a
            :class:`logging.Formatter` instance, default:
            :data:`pygogo.formatters.basic_formatter`).

        verbose (bool): If False, set low level to `info`, if True, set low
            level to `debug`, overrides `levels['low']` if specified
            (default: None).

        monolog (bool): Log high level events only to high pass handler (
            default: False)

    Returns:
        New instance of :class:`pygogo.Gogo`

    Examples:
        >>> Gogo('name').logger.debug('message')
        message
    """

    def __init__(self, name='root', high_level=None, low_level=None, **kwargs):
        """Initialization method.

        Examples:
            >>> Gogo('name') # doctest: +ELLIPSIS
            <pygogo.Gogo object at 0x...>
        """
        verbose = kwargs.get('verbose')
        high_level = high_level or 'warning'

        if verbose is None:
            low_level = low_level or 'debug'
        elif verbose:
            low_level = 'debug'
        else:
            low_level = 'info'

        self.levels = {
            'high': getattr(logging, high_level.upper(), None),
            'low': getattr(logging, low_level.upper(), None)}

        if not isinstance(self.levels['high'], int):
            raise ValueError('Invalid high_level: %s' % self.levels['high'])
        elif not isinstance(self.levels['low'], int):
            raise ValueError('Invalid low_level: %s' % self.levels['low'])
        elif self.levels['high'] < self.levels['low']:
            raise ValueError('high_level must be >= low_level')

        self.loggers = set()
        self.name = name
        self.handlers = {
            'high': kwargs.get('high_hdlr', handlers.stderr_hdlr()),
            'low': kwargs.get('low_hdlr', handlers.stdout_hdlr())}

        self.formatters = {
            'high': kwargs.get('high_formatter', formatters.basic_formatter),
            'low': kwargs.get('low_formatter', formatters.basic_formatter)}

        self.monolog = kwargs.get('monolog')

    @property
    def logger(self):
        """The logger property.

        Returns:
            New instance of :class:`logging.Logger`

        Examples:
            >>> from io import StringIO

            >>> s = StringIO()
            >>> sys.stderr = s
            >>> logger = Gogo('default').logger
            >>> logger  # doctest: +ELLIPSIS
            <logging.Logger object at 0x...>
            >>> logger.debug('stdout')
            stdout
            >>> kwargs = {'low_level': 'info', 'monolog': True}
            >>> logger = Gogo('ignore_if_lt_info', **kwargs).logger
            >>> logger.debug('ignored')
            >>> logger.info('stdout')
            stdout
            >>> logger.warning('stderr')
            >>> s.getvalue().strip() == 'stderr'
            True
        """
        return self.get_logger()

    def update_hdlr(self, hdlr, level, formatter=None, monolog=False, **kwargs):
        """Update a handler with a formatter, level, and filters.

        Args:
            hdlr (obj): A :class:`logging.handlers` instance.

            level (int): The min level to log to to `hdlr`.

            formatter (obj): The log formatter (a :class:`logging.Formatter`
                instance, default: :data:`pygogo.formatters.basic_formatter`)

            monolog (bool): Log high level events only to high pass handler (
                default: False)

            kwargs (dict): Keyword arguemnts passed to
                `pygogo.utils.get_structured_filter`

        See also:
            :meth:`pygogo.Gogo.get_logger`

            :meth:`pygogo.Gogo.get_structured_logger`

            :func:`pygogo.utils.LogFilter`

            :func:`pygogo.utils.get_structured_filter`

        Examples:
            >>> low_hdlr = logging.StreamHandler(sys.stdout)
            >>> going = Gogo(low_hdlr=low_hdlr, monolog=True)
            >>> hdlr = going.handlers['low']
            >>> [hdlr.formatter, hdlr.filters, hdlr.level]
            [None, [], 0]
            >>> fmtr = going.formatters['low']
            >>> kwargs = {'formatter': fmtr, 'monolog': going.monolog}
            >>> going.update_hdlr(hdlr, going.levels['low'], **kwargs)
            >>> [hdlr.formatter, hdlr.filters, hdlr.level]
            ...  # doctest: +ELLIPSIS
            [<logging.Formatter obj...>, [<pygogo.utils.LogFilter obj...>], 10]
        """
        hdlr.setLevel(level)

        if monolog:
            log_filter = utils.LogFilter(self.levels['high'])
            hdlr.addFilter(log_filter)

        if kwargs:
            structured_filter = utils.get_structured_filter(**kwargs)
            hdlr.addFilter(structured_filter)

        hdlr.setFormatter(formatter)

    def zip(self, *fmtrs):
        """Format high/low handler properties so that they can be conveniently
            passed to `update_hdlr`.

        Args:
            fmtrs (seq[obj]): A sequence of :class:`logging.Formatter`
                instances.

        See also:
            :meth:`pygogo.Gogo.update_hdlr`

            :meth:`pygogo.Gogo.get_logger`

            :meth:`pygogo.Gogo.get_structured_logger`

        Returns:
            New instance of :class:`logging.handlers`

        Examples:
            >>> hdlr = logging.StreamHandler(sys.stdout)
            >>> copy_hdlr(hdlr) # doctest: +ELLIPSIS
            <logging.StreamHandler object at 0x...>
        """
        hdlrs = [self.handlers['high'], self.handlers['low']]
        levels = [self.levels['high'], self.levels['low']]
        monologs = [False, self.monolog]
        return zip(hdlrs, levels, fmtrs, monologs)

    def get_logger(self, name='base', **kwargs):
        """Retrieve a named logger.

        Args:
            name (string): The logger name.

        See also:
            :func:`pygogo.copy_hdlr`

            :meth:`pygogo.Gogo.update_hdlr`

            :meth:`pygogo.Gogo.zip`

        Returns:
            New instance of :class:`logging.Logger`

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
        lggr_name = '%s.%s' % (self.name, name)
        logger = logging.getLogger(lggr_name)

        if lggr_name not in self.loggers:
            self.loggers.add(lggr_name)

            if kwargs:
                kwargs['name'] = lggr_name

            fmtrs = [self.formatters['high'], self.formatters['low']]

            for zipped in self.zip(*fmtrs):
                hdlr, level, fmtr, monolog = zipped
                copied_hdlr = copy_hdlr(hdlr)
                self.update_hdlr(copied_hdlr, level, fmtr, monolog, **kwargs)
                logger.addHandler(copied_hdlr)

            logger.setLevel(self.levels['low'])

        return logger

    def get_structured_logger(self, name=None, **kwargs):
        """Retrieve a structured data logger

        Args:
            name (string): The logger name.

            kwargs (dict): Keyword arguments to include in every log message.

        See also:
            :func:`pygogo.copy_hdlr`

            :meth:`pygogo.Gogo.update_hdlr`

            :meth:`pygogo.Gogo.zip`

            :class:`pygogo.utils.StructuredAdapter`

        Returns:
            New instance of :class:`pygogo.utils.StructuredAdapter`

        Examples
            >>> from io import StringIO
            >>> from json import loads

            >>> s = StringIO()
            >>> going = Gogo('structured', low_hdlr=handlers.fileobj_hdlr(s))
            >>> logger = going.get_structured_logger(all='true')
            >>> logger  # doctest: +ELLIPSIS
            <pygogo.utils.StructuredAdapter object at 0x...>
            >>> logger.debug('hello')
            >>> logger.debug('extra', extra={'key': 'value'})
            >>> s.seek(0) or 0
            0
            >>> loads(next(s)) == {'all': 'true', 'message': 'hello'}
            True
            >>> loads(next(s)) == {
            ...     'all': 'true', 'message': 'extra', 'key': 'value'}
            True
        """
        values = frozenset(kwargs.items())
        name = name or hashlib.md5(str(values).encode('utf-8')).hexdigest()
        lggr_name = '%s.structured.%s' % (self.name, name)
        logger = logging.getLogger(lggr_name)

        if lggr_name not in self.loggers:
            self.loggers.add(lggr_name)
            formatter = formatters.basic_formatter

            for zipped in self.zip(formatter, formatter):
                hdlr, level, fmtr, monolog = zipped
                copied_hdlr = copy_hdlr(hdlr)
                self.update_hdlr(copied_hdlr, level, fmtr, monolog)
                logger.addHandler(copied_hdlr)

            logger.setLevel(self.levels['low'])

        return utils.StructuredAdapter(logger, kwargs)


def copy_hdlr(hdlr):
    """Safely copy a handler and its associated filters.

    Args:
        hdlr (obj): A :class:`logging.handlers` instance.

    See also:
        :meth:`pygogo.Gogo.get_logger`

        :meth:`pygogo.Gogo.get_structured_logger`

    Returns:
        New instance of :class:`logging.handlers`

    Examples:
        >>> hdlr = logging.StreamHandler(sys.stdout)
        >>> copy_hdlr(hdlr) # doctest: +ELLIPSIS
        <logging.StreamHandler object at 0x...>
    """
    copied_hdlr = copy(hdlr)
    copied_hdlr.filters = [copy(f) for f in hdlr.filters]
    return copied_hdlr

logger = Gogo().logger
