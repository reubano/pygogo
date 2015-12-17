# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab

"""
pygogo.formatters
~~~~~~~~~~~~~~~~~

Log formatters

Examples:
    Add a console formatter::

        >>> import sys

        >>> logger = logging.getLogger('console_logger')
        >>> hdlr = logging.StreamHandler(sys.stdout)
        >>> hdlr.setFormatter(console_formatter)
        >>> logger.addHandler(hdlr)
        >>> logger.info('hello world')
        console_logger: INFO     hello world

    Add a structured formatter::

        >>> import sys

        >>> logger = logging.getLogger('structured_logger')
        >>> hdlr = logging.StreamHandler(sys.stdout)
        >>> hdlr.setFormatter(structured_formatter)
        >>> extra = {'key': 'value'}
        >>> logger.addHandler(hdlr)
        >>> logger.info('hello world', extra=extra)  # doctest: +ELLIPSIS
        {"message": "hello world", "level": "INFO", "name": \
"structured_logger", "key": "value", "time": "20..."}

Attributes:
    BASIC_FORMAT (str): A basic format
    CONSOLE_FORMAT (str): A format for displaying in a console
    FIXED_FORMAT (str): A fixed width format
    CSV_FORMAT (str): A csv format
    JSON_FORMAT (str): A json format
    DATEFMT (str): Standard date format
"""

from __future__ import (
    absolute_import, division, print_function, with_statement,
    unicode_literals)

import logging
import traceback
import itertools as it

from .utils import CustomEncoder

BASIC_FORMAT = '%(message)s'
BOM_FORMAT = u'\ufeff%(message)s'
CONSOLE_FORMAT = '%(name)-12s: %(levelname)-8s %(message)s'
FIXED_FORMAT = '%(asctime)s.%(msecs)d %(name)-12s %(levelname)-8s %(message)s'
CSV_FORMAT = '%(asctime)s.%(msecs)d,%(name)s,%(levelname)s,"%(message)s"'
JSON_FORMAT = (
    '{"time": "%(asctime)s.%(msecs)d", "name": "%(name)s", "level":'
    ' "%(levelname)s", "message": "%(message)s"}')

DATEFMT = '%Y-%m-%d %H:%M:%S'

basic_formatter = logging.Formatter(BASIC_FORMAT)
bom_formatter = logging.Formatter(BOM_FORMAT)
console_formatter = logging.Formatter(CONSOLE_FORMAT)
fixed_formatter = logging.Formatter(FIXED_FORMAT, datefmt=DATEFMT)
csv_formatter = logging.Formatter(CSV_FORMAT, datefmt=DATEFMT)
json_formatter = logging.Formatter(JSON_FORMAT, datefmt=DATEFMT)


class StructuredFormatter(logging.Formatter):
    """A logging formatter that creates a json string from log details

    TODO: Add log exception handling

    Examples:
        >>> import sys
        >>>
        >>> logger = logging.getLogger()
        >>> formatter = StructuredFormatter(BASIC_FORMAT, datefmt=DATEFMT)
        >>> hdlr = logging.StreamHandler(sys.stdout)
        >>> hdlr.setFormatter(formatter)
        >>> logger.addHandler(hdlr)
        >>> logger.info('hello world')  # doctest: +ELLIPSIS
        {"message": "hello world", "level": "INFO", "name": \
"root", "time": "..."}
    """
    def __init__(self, *args, **kwargs):
        """Initialization method.

        Args:
            args (string): The min level to log to low_hdlr.
            kwargs (dict): Keyword arguments.

        Kwargs:
            high_hdlr (obj): The high pass log handler (a

        Returns:
            New instance of :class:`StructuredFormatter`

        Examples:
            >>> StructuredFormatter('name') # doctest: +ELLIPSIS
            <pygogo.formatters.StructuredFormatter object at 0x...>
        """
        empty_record = logging.makeLogRecord({})
        filterer = lambda k: k not in empty_record.__dict__ and k != 'asctime'
        self.filterer = filterer
        super(StructuredFormatter, self).__init__(*args, **kwargs)

    def format(self, record):
        """ Formats a record as a dict string

        Args:
            record (object): The event to format.

        Returns:
            str: The formatted content

        Examples:
            >>> formatter = StructuredFormatter(BASIC_FORMAT, datefmt='%Y')
            >>> logger = logging.getLogger()
            >>> msg = 'hello world'
            >>> args = (logging.INFO, '.', 0, msg, [], None)
            >>> record = logger.makeRecord('root', *args)
            >>> formatter.format(record)  # doctest +ELLIPSIS
            '{"message": "hello world", "level": "INFO", "name": \
"root", "time": "2015"}'
        """
        extra = {
            'message': record.getMessage(),
            'time': self.formatTime(record, self.datefmt),
            'name': record.name,
            'level': record.levelname}

        keys = filter(self.filterer, record.__dict__)
        extra.update({k: record.__dict__[k] for k in keys})
        extra.pop('asctime', None)
        return CustomEncoder().encode(extra)

    def formatException(self, exc_info):
        """Formats an exception as a dict string

        Args:
            exc_info (tuple[type, value, traceback]): Exception tuple as
                returned by sys.exc_info()

        Returns:
            dict: The formatted exception

        Examples:
            >>> import sys
            >>>
            >>> formatter = StructuredFormatter(BASIC_FORMAT)
            >>> try:
            ...     1 / 0
            ... except:
            ...     formatter.formatException(sys.exc_info())
            '{"function": "<module>", "text": "1 / 0", "value": \
"division by zero", "filename": \
"<doctest pygogo.formatters.StructuredFormatter.formatException[2]>", \
"lineno": 2, "type": "exceptions.ZeroDivisionError"}'
        """
        keys = ['type', 'value', 'filename', 'lineno', 'function', 'text']
        type_, value, tb = exc_info
        stype = str(type_).replace('type', '').strip(" '<>")
        values = it.chain([stype, value], *traceback.extract_tb(tb))
        return CustomEncoder().encode(dict(zip(keys, values)))

structured_formatter = StructuredFormatter(BASIC_FORMAT, datefmt=DATEFMT)
