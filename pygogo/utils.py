# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab

"""
pygogo.utils
~~~~~~~~~~~~

Misc classes and functions that don't warrant their own module

Examples:
    basic usage::

        >>> CustomEncoder().encode(range(5))
        '[0, 1, 2, 3, 4]'

"""

from __future__ import (
    absolute_import, division, print_function, unicode_literals)

import logging
import sys

from json import JSONEncoder
from builtins import *

module_hdlr = logging.StreamHandler(sys.stdout)
module_logger = logging.getLogger(__name__)
module_logger.addHandler(module_hdlr)


class CustomEncoder(JSONEncoder):
    """A unicode aware JSON encoder that can handle iterators, dates, and times

    Examples:
        >>> CustomEncoder().encode(range(5))
        '[0, 1, 2, 3, 4]'
        >>> from json import dumps
        >>> dumps(range(5), cls=CustomEncoder)
        '[0, 1, 2, 3, 4]'
    """
    def default(self, obj):
        """ Encodes a given object

        Args:
            obj (scalar): The object to encode.

        Returns:
            The encoded object

        Examples:
            >>> CustomEncoder().default(range(5))
            [0, 1, 2, 3, 4]
        """
        if hasattr(obj, 'real'):
            encoded = float(obj)
        elif hasattr(obj, 'union'):
            encoded = tuple(obj)
        elif set(['next', 'union', '__iter__']).intersection(dir(obj)):
            encoded = list(obj)
        else:
            encoded = str(obj)

        return encoded


class StructuredMessage(object):
    """Converts a message and kwargs to a json string

    Attributes:
        kwargs (dict): Keyword arguments passed to
            :class:`~pygogo.utils.CustomEncoder`.

    Args:
        message (string): The message to log.

        kwargs (dict): Keyword arguments passed to
            :class:`~pygogo.utils.CustomEncoder`.

    Returns:
        New instance of :class:`StructuredMessage`

    See also:
        :class:`pygogo.utils.StructuredAdapter`

    Examples:
        >>> from json import loads

        >>> msg = StructuredMessage('hello world', key='value')
        >>> loads(str(msg)) == {'message': 'hello world', 'key': 'value'}
        True
    """
    def __init__(self, message=None, **kwargs):
        """Initialization method.

        Args:
            message (string): The message to log.

            kwargs (dict): Keyword arguments passed to
                :class:`~pygogo.utils.CustomEncoder`.

        Returns:
            New instance of :class:`StructuredMessage`

        Examples:
            >>> StructuredMessage('message')  # doctest: +ELLIPSIS
            <pygogo.utils.StructuredMessage object at 0x...>
        """
        kwargs['message'] = message
        self.kwargs = kwargs

    def __str__(self):
        """ String method

        Returns:
            str: The encoded object

        Examples
            >>> from json import loads

            >>> msg = str(StructuredMessage('hello world', key='value'))
            >>> loads(msg) == {'message': 'hello world', 'key': 'value'}
            True

        """
        return str(CustomEncoder().encode(self.kwargs))


class StructuredAdapter(logging.LoggerAdapter):
    """A logging adapter that creates a json string from a log message and the
    `extra` kwarg

    See also:
        :class:`pygogo.utils.StructuredMessage`

        :meth:`pygogo.Gogo.get_structured_logger`

    Examples:
        >>> from io import StringIO
        >>> from json import loads

        >>> s = StringIO()
        >>> logger = logging.getLogger()
        >>> hdlr = logging.StreamHandler(s)
        >>> logger.addHandler(hdlr)
        >>> structured_logger = StructuredAdapter(logger, {'all': True})
        >>> structured_logger.debug('hello', extra={'key': u'value'})
        >>> loads(s.getvalue()) == {
        ...     'all': True, 'message': 'hello', 'key': 'value'}
        True
    """
    def process(self, msg, kwargs):
        """ Modifies the message and/or keyword arguments passed to a logging
        call in order to insert contextual information.

        Args:
            msg (str): The message to log.
            kwargs (dict):

        Returns:
            Tuple of (:class:`~pygogo.utils.StructuredMessage`, modified kwargs)

        Examples:
            >>> from json import loads

            >>> logger = logging.getLogger()
            >>> structured_logger = StructuredAdapter(logger, {'all': True})
            >>> extra = {'key': 'value'}
            >>> m, k = structured_logger.process('message', {'extra': extra})
            >>> loads(m) == {'all': True, 'message': 'message', 'key': 'value'}
            True
            >>> k == {'extra': {'all': True, 'key': 'value'}}
            True
        """
        extra = kwargs.get('extra', {})
        extra.update(self.extra)
        kwargs['extra'] = extra
        return str(StructuredMessage(msg, **extra)), kwargs


class LogFilter(logging.Filter):
    """Filters log messages depending on level

    Attributes:
        level (int): The logging level.

            +-------------------------+-------+
            | logging level attribute | value |
            +=========================+=======+
            | CRITICAL                | 50    |
            +-------------------------+-------+
            | ERROR                   | 40    |
            +-------------------------+-------+
            | WARNING                 | 30    |
            +-------------------------+-------+
            | INFO                    | 20    |
            +-------------------------+-------+
            | DEBUG                   | 10    |
            +-------------------------+-------+
            | NOTSET                  |  0    |
            +-------------------------+-------+

    Args:
        level (int): The logging level.

    Returns:
        New instance of :class:`LogFilter`

    See also:
        :meth:`pygogo.Gogo.update_hdlr`
    """
    def __init__(self, level):
        """Initialization method.

        Args:
            level (int): The logging level.

        Returns:
            New instance of :class:`LogFilter`

        Examples:
            >>> LogFilter(40)  # doctest: +ELLIPSIS
            <pygogo.utils.LogFilter object at 0x...>
        """
        self.high_level = level

    def filter(self, record):
        """Determines whether or a not a message should be logged.

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


def get_structured_filter(name='', **kwargs):
    """Returns a structured filter that injects contextual information into
    log records.

    Args:
        kwargs (dict): The contextual information you wish to inject

    See also:
        :meth:`pygogo.Gogo.update_hdlr`

    Returns:
        New instance of :class:`pygogo.utils.StructuredFilter`

    Examples:
        >>> structured_filter = get_structured_filter(user='fred')
        >>> structured_filter  # doctest: +ELLIPSIS
        <pygogo.utils...StructuredFilter object at 0x...>
        >>>
        >>> logger = logging.getLogger('structured_filter')
        >>> hdlr = logging.StreamHandler(sys.stdout)
        >>> formatter = logging.Formatter('User %(user)s said, "%(message)s".')
        >>> hdlr.setFormatter(formatter)
        >>> logger.addFilter(structured_filter)
        >>> logger.addHandler(hdlr)
        >>> logger.debug('A debug message')
        User fred said, "A debug message".

    """
    class StructuredFilter(logging.Filter):
        """
        Injects contextual information into log records.
        """
        def filter(self, record):
            """Adds contextual information to a log record

            Args:
                record (obj): The event to contextualize

            Returns:
                bool: True
            """
            for k, v in kwargs.items():
                setattr(record, k, v)

            return True

    return StructuredFilter(name)
