# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab

"""
pygogo.utils
~~~~~~~~~~~~

Misc classes and functions that don't warrant their own module

Examples:
    basic usage::

"""

from __future__ import (
    absolute_import, division, print_function, with_statement,
    unicode_literals)

import logging
import sys

from json import JSONEncoder

hdlr = logging.StreamHandler(sys.stdout)
module_logger = logging.getLogger(__name__)
module_logger.addHandler(hdlr)


class CustomEncoder(JSONEncoder):
    """A unicode aware JSON encoder that can handle iterators, dates, and times

    http://stackoverflow.com/a/28743317/408556

    Examples:
        >>> CustomEncoder().encode(xrange(5))
        '[0, 1, 2, 3, 4]'
        >>> from json import dumps
        >>> dumps(xrange(5), cls=CustomEncoder)
        '[0, 1, 2, 3, 4]'
    """
    def default(self, obj):
        """ Encodes a given object

        Args:
            obj (scalar): The object to encode.

        Returns:
            The encoded object

        Examples:
            >>> CustomEncoder().default(xrange(5))
            [0, 1, 2, 3, 4]
        """
        if hasattr(obj, 'real'):
            encoded = float(obj)
        elif set(['quantize', 'year', 'hour']).intersection(dir(obj)):
            encoded = str(obj)
        elif hasattr(obj, 'union'):
            encoded = tuple(obj)
        elif set(['next', 'union', '__iter__']).intersection(dir(obj)):
            encoded = list(obj)
        elif isinstance(obj, unicode):
            encoded = obj.encode('unicode_escape').decode('ascii')
        else:
            try:
                encoded = super(CustomEncoder, self).default(obj)
            except TypeError:
                encoded = str(obj)

        return encoded


class StructuredMessage(object):
    """Converts a message and kwargs to a json string

    http://stackoverflow.com/a/28743317/408556

    Attributes:
        name (string): The logger name.
        high_level (string): The min level to log to high_hdlr.
        low_level (string): The min level to log to low_hdlr.
            messages < low_level               -> ignore
            low_level <= messages < high_level -> low_hdlr
            high_level <= messages             -> high_hdlr

    Examples:
        >>> logger = logging.getLogger()
        >>> hdlr = logging.StreamHandler(sys.stdout)
        >>> hdlr.setFormatter(logging.Formatter('%(message)s'))
        >>> logger.addHandler(hdlr)
        >>> logger.info(StructuredMessage('hello world', key='value'))
        {"message": "hello world", "key": "value"}
    """
    def __init__(self, message=None, **kwargs):
        """Initialization method.

        Args:
            message (string): The message to log.
            kwargs (dict): Keyword arguments passed to the encoder.

        Returns:
            New instance of :class:`StructuredMessage`

        Examples:
            >>> StructuredMessage('message') # doctest: +ELLIPSIS
            <pygogo.utils.StructuredMessage object at 0x...>
        """
        kwargs['message'] = message
        self.kwargs = kwargs

    def __str__(self):
        """ String method

        Returns:
            str: The encoded object

        Examples
            >>> str(StructuredMessage('hello world', key='value'))
            '{"message": "hello world", "key": "value"}'
        """
        return CustomEncoder().encode(self.kwargs)


class StructuredAdapter(logging.LoggerAdapter):
    """A logging adapter that creates a json string from a log message and the
    `extra` kwarg

    http://stackoverflow.com/a/28743317/408556

    Attributes:
        name (string): The logger name.
        high_level (string): The min level to log to high_hdlr.
        low_level (string): The min level to log to low_hdlr.
            messages < low_level               -> ignore
            low_level <= messages < high_level -> low_hdlr
            high_level <= messages             -> high_hdlr

    Examples:
        >>> logger = logging.getLogger()
        >>> hdlr = logging.StreamHandler(sys.stdout)
        >>> logger.addHandler(hdlr)
        >>> structured_logger = StructuredAdapter(logger, {'all': 'true'})
        >>> structured_logger.debug('hello', extra={'key': 'value'})
        {"all": "true", "message": "hello", "key": "value"}
    """
    def process(self, msg, kwargs):
        """ Modifies the message and/or keyword arguments passed to a logging
        call in order to insert contextual information.

        Args:
            msg (str): The message to log.
            kwargs (dict):

        Returns:
            Tuple of (:class:`StructuredMessage`, modified kwargs)

        Examples:
            >>> logger = logging.getLogger()
            >>> hdlr = logging.StreamHandler(sys.stdout)
            >>> logger.addHandler(hdlr)
            >>> structured_logger = StructuredAdapter(logger, {'all': 'true'})
            >>> extra = {'key': 'value'}
            >>> m, k = structured_logger.process('message', {'extra': extra})
            >>> m  # doctest: +ELLIPSIS
            <pygogo.utils.StructuredMessage object at 0x...>
            >>> k
            {u'extra': {u'all': u'true', u'key': u'value'}}
        """
        extra = kwargs.get('extra', {})
        extra.update(self.extra)
        kwargs['extra'] = extra
        return StructuredMessage(msg, **extra), kwargs


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

    Returns:
        New instance of :class:`StructuredFilter`

    Examples:
        >>> structured_filter = get_structured_filter(user='fred')
        >>> structured_filter  # doctest: +ELLIPSIS
        <pygogo.utils.StructuredFilter object at 0x...>
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
