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

        >>> from io import StringIO
        >>> from json import loads

        >>> s = StringIO()
        >>> logger = logging.getLogger('structured_logger')
        >>> hdlr = logging.StreamHandler(s)
        >>> hdlr.setFormatter(structured_formatter)
        >>> extra = {'key': 'value'}
        >>> logger.addHandler(hdlr)
        >>> logger.info('hello world', extra=extra)
        >>> result = loads(s.getvalue())
        >>> keys = sorted(result.keys())
        >>> keys == ['key', 'level', 'message', 'msecs', 'name', 'time']
        True
        >>> [result[k] for k in keys if k not in {'msecs', 'time'}] == [
        ...     'value', 'INFO', 'hello world', 'structured_logger']
        True

Attributes:
    BASIC_FORMAT (str): A basic format

    CONSOLE_FORMAT (str): A format for displaying in a console

    FIXED_FORMAT (str): A fixed width format

    CSV_FORMAT (str): A csv format

    JSON_FORMAT (str): A json format

    DATEFMT (str): Standard date format
"""

from __future__ import (
    absolute_import, division, print_function, unicode_literals)

import logging
import sys
import traceback
import itertools as it

from builtins import *
from .utils import CustomEncoder

BASIC_FORMAT = '%(message)s'
BOM_FORMAT = '\ufeff%(message)s'
CONSOLE_FORMAT = '%(name)-12s: %(levelname)-8s %(message)s'
FIXED_FORMAT = '%(asctime)s.%(msecs)-3d %(name)-12s %(levelname)-8s %(message)s'
CSV_FORMAT = '%(asctime)s.%(msecs)d,%(name)s,%(levelname)s,"%(message)s"'
JSON_FORMAT = (
    '{"time": "%(asctime)s.%(msecs)d", "name": "%(name)s", "level":'
    ' "%(levelname)s", "message": "%(message)s"}')

DATEFMT = '%Y-%m-%d %H:%M:%S'

module_hdlr = logging.StreamHandler(sys.stdout)
module_logger = logging.getLogger(__name__)
module_logger.addHandler(module_hdlr)


class StructuredFormatter(logging.Formatter):
    """A logging formatter that creates a json string from log details

    Args:
        fmt (string): Log message format.

        datefmt (dict): Log date format.

    Returns:
        New instance of :class:`StructuredFormatter`

    Examples:
        >>> from io import StringIO
        >>> from json import loads

        >>> s = StringIO()
        >>> logger = logging.getLogger()
        >>> formatter = StructuredFormatter(BASIC_FORMAT, datefmt=DATEFMT)
        >>> hdlr = logging.StreamHandler(s)
        >>> hdlr.setFormatter(formatter)
        >>> logger.addHandler(hdlr)
        >>> logger.info('hello world')
        >>> result = loads(s.getvalue())
        >>> keys = sorted(result.keys())
        >>> keys == ['level', 'message', 'msecs', 'name', 'time']
        True
        >>> [result[k] for k in keys if k not in {'msecs', 'time'}] == [
        ...     'INFO', 'hello world', 'root']
        True
    """
    def __init__(self, fmt=None, datefmt=None):
        """Initialization method.

        Args:
            fmt (string): Log message format.

            datefmt (dict): Log date format.

        Returns:
            New instance of :class:`StructuredFormatter`

        Examples:
            >>> StructuredFormatter('name')  # doctest: +ELLIPSIS
            <pygogo.formatters.StructuredFormatter object at 0x...>
        """
        empty_record = logging.makeLogRecord({})
        filterer = lambda k: k not in empty_record.__dict__ and k != 'asctime'
        self.filterer = filterer
        super(StructuredFormatter, self).__init__(fmt, datefmt)

    def format(self, record):
        """ Formats a record as a dict string

        Args:
            record (object): The event to format.

        Returns:
            str: The formatted content

        Examples:
            >>> from json import loads

            >>> formatter = StructuredFormatter(BASIC_FORMAT, datefmt='%Y')
            >>> logger = logging.getLogger()
            >>> args = (logging.INFO, '.', 0, 'hello world', [], None)
            >>> record = logger.makeRecord('root', *args)
            >>> result = loads(formatter.format(record))
            >>> keys = sorted(result.keys())
            >>> keys == ['level', 'message', 'msecs', 'name', 'time']
            True
            >>> [result[k] for k in keys if k not in {'msecs', 'time'}] == [
            ...     'INFO', 'hello world', 'root']
            True
        """
        extra = {
            'message': record.getMessage(),
            'time': self.formatTime(record, self.datefmt),
            'msecs': record.msecs,
            'name': record.name,
            'level': record.levelname}

        keys = filter(self.filterer, record.__dict__)
        extra.update({k: record.__dict__[k] for k in keys})
        extra.pop('asctime', None)
        return str(CustomEncoder().encode(extra))

    def formatException(self, exc_info):
        """Formats an exception as a dict string

        Args:
            exc_info (tuple[type, value, traceback]): Exception tuple as
                returned by `sys.exc_info()`

        Returns:
            str: The formatted exception

        Examples:
            >>> from json import loads

            >>> formatter = StructuredFormatter(BASIC_FORMAT)
            >>> try:
            ...     1 / 0
            ... except:
            ...     result = loads(formatter.formatException(sys.exc_info()))
            >>> keys = sorted(result.keys())
            >>> keys == [
            ...     'filename', 'function', 'lineno', 'text', 'type', 'value']
            True
            >>> [result[k] for k in keys if k not in {'filename', 'type'}] == [
            ...     '<module>', 2, '1 / 0', 'division by zero']
            True
            >>> result['type'][-17:] == 'ZeroDivisionError'
            True
        """
        keys = ['type', 'value', 'filename', 'lineno', 'function', 'text']
        type_, value, trcbk = exc_info
        stype = str(type_).replace('type', '').strip(" '<>")
        values = it.chain([stype, value], *traceback.extract_tb(trcbk))
        return str(CustomEncoder().encode(dict(zip(keys, values))))

basic_formatter = logging.Formatter(BASIC_FORMAT)
bom_formatter = logging.Formatter(BOM_FORMAT)
console_formatter = logging.Formatter(CONSOLE_FORMAT)
fixed_formatter = logging.Formatter(FIXED_FORMAT, datefmt=DATEFMT)
csv_formatter = logging.Formatter(CSV_FORMAT, datefmt=DATEFMT)
json_formatter = logging.Formatter(JSON_FORMAT, datefmt=DATEFMT)
structured_formatter = StructuredFormatter(BASIC_FORMAT, datefmt=DATEFMT)
