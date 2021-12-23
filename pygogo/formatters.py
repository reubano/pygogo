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

    JSON_FORMAT (str): A json format

    DATEFMT (str): Standard date format
"""

import logging
import sys
import traceback
import itertools as it
import csv

from io import StringIO
from .utils import CustomEncoder

BASIC_FORMAT = "%(message)s"
BOM_FORMAT = "\ufeff%(message)s"
CONSOLE_FORMAT = "%(name)-12s: %(levelname)-8s %(message)s"
FIXED_FORMAT = "%(asctime)s.%(msecs)-3d %(name)-12s %(levelname)-8s %(message)s"
JSON_FORMAT = (
    '{"time": "%(asctime)s.%(msecs)d", "name": "%(name)s", "level":'
    ' "%(levelname)s", "message": "%(message)s"}'
)

DATEFMT = "%Y-%m-%d %H:%M:%S"

# https://stackoverflow.com/a/56944256/408556
GREY = "\x1b[38;21m"
YELLOW = "\x1b[33;21m"
RED = "\x1b[31;21m"
BOLD_RED = "\x1b[31;1m"
RESET = "\x1b[0m"

module_hdlr = logging.StreamHandler(sys.stdout)
module_logger = logging.getLogger(__name__)
module_logger.addHandler(module_hdlr)


class BaseFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, **kwargs):
        """Initialization method.

        Args:
            fmt (string): Log message format.

            datefmt (dict): Log date format.

        Returns:
            New instance of :class:`BaseFormatter`

        Examples:
            >>> BaseFormatter("%(message)s")  # doctest: +ELLIPSIS
            <pygogo.formatters.BaseFormatter object at 0x...>
        """
        empty_record = logging.makeLogRecord({})
        filterer = lambda k: k not in empty_record.__dict__ and k != "asctime"
        self.filterer = filterer
        super().__init__(datefmt=datefmt)


# https://stackoverflow.com/a/19766056/408556
class CsvFormatter(BaseFormatter):
    """A logging formatter that creates a csv string from log details

    Args:
        fmt (string): Log message format.

        datefmt (dict): Log date format.

    Returns:
        New instance of :class:`CsvFormatter`

    Examples:
        >>> from io import StringIO
        >>>
        >>> s = StringIO()
        >>> logger = logging.getLogger()
        >>> formatter = CsvFormatter(datefmt=DATEFMT)
        >>> hdlr = logging.StreamHandler(s)
        >>> hdlr.setFormatter(formatter)
        >>> logger.addHandler(hdlr)
        >>> logger.info('hello "world"')
        >>> s.getvalue().strip()  # doctest: +ELLIPSIS
        '"20...","root","INFO","hello \"\"world\"\"","hello \"\"world\"\""'
    """

    def __init__(self, fmt=None, datefmt=None, quoting=csv.QUOTE_ALL, **kwargs):
        """Initialization method.

        Args:
            fmt (string): Log message format.

            datefmt (dict): Log date format.

        Returns:
            New instance of :class:`CsvFormatter`

        Examples:
            >>> CsvFormatter("%(message)s")  # doctest: +ELLIPSIS
            <pygogo.formatters.CsvFormatter object at 0x...>
        """
        super().__init__(fmt=fmt, datefmt=datefmt)
        self.output = StringIO()
        self.writer = csv.writer(self.output, quoting=quoting, **kwargs)

    def format(self, record):
        """ Formats a record as a dict string

        Args:
            record (object): The event to format.

        Returns:
            str: The formatted content

        Examples:
            >>> formatter = CsvFormatter(datefmt='%Y')
            >>> logger = logging.getLogger()
            >>> args = (logging.INFO, '.', 0, 'hello "world"', [], None)
            >>> record = logger.makeRecord('root', *args)
            >>> formatter.format(record)  # doctest: +ELLIPSIS
            '"20...","root","INFO","hello \"\"world\"\""'
        """
        row = [self.formatTime(record, self.datefmt), record.name, record.levelname]
        keys = filter(self.filterer, record.__dict__)
        extra = [record.__dict__[k] for k in keys]

        self.writer.writerow(row + extra + [record.getMessage()])
        data = self.output.getvalue()
        self.output.truncate(0)
        self.output.seek(0)
        return data.strip()

    def formatException(self, exc_info):
        """Formats an exception as a dict string

        Args:
            exc_info (tuple[type, value, traceback]): Exception tuple as
                returned by `sys.exc_info()`

        Returns:
            str: The formatted exception

        Examples:
            >>> formatter = CsvFormatter()
            >>>
            >>> try:  # doctest: +ELLIPSIS
            ...     1 / 0
            ... except:
            ...     formatter.formatException(sys.exc_info())
            '"ZeroDivisionError","division by zero","<docte...>","2","<module>","1 / 0"'
        """
        type_, value, trcbk = exc_info

        # ["type", "value", "filename", "lineno", "function", "text"]
        self.writer.writerow(
            it.chain([type_.__name__, value], *traceback.extract_tb(trcbk))
        )
        data = self.output.getvalue()
        self.output.truncate(0)
        self.output.seek(0)
        return data.strip()


class StructuredFormatter(BaseFormatter):
    """A logging formatter that creates a json string from log details

    Args:
        fmt (string): Log message format.

        datefmt (dict): Log date format.

    Returns:
        New instance of :class:`StructuredFormatter`

    Examples:
        >>> from io import StringIO
        >>> from json import loads
        >>>
        >>> s = StringIO()
        >>> logger = logging.getLogger()
        >>> formatter = StructuredFormatter(datefmt=DATEFMT)
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

    def format(self, record):
        """ Formats a record as a dict string

        Args:
            record (object): The event to format.

        Returns:
            str: The formatted content

        Examples:
            >>> from json import loads
            >>>
            >>> formatter = StructuredFormatter(datefmt='%Y')
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
            "message": record.getMessage(),
            "time": self.formatTime(record, self.datefmt),
            "msecs": record.msecs,
            "name": record.name,
            "level": record.levelname,
        }

        keys = filter(self.filterer, record.__dict__)
        extra.update({k: record.__dict__[k] for k in keys})
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
            >>>
            >>> formatter = StructuredFormatter()
            >>>
            >>> try:
            ...     1 / 0
            ... except:
            ...     result = loads(formatter.formatException(sys.exc_info()))
            >>>
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
        keys = ["type", "value", "filename", "lineno", "function", "text"]
        type_, value, trcbk = exc_info
        values = it.chain([type_.__name__, value], *traceback.extract_tb(trcbk))
        return str(CustomEncoder().encode(dict(zip(keys, values))))


class ColorizedFormatter(BaseFormatter):
    """A logging formatter that creates a colorized log

    Args:
        fmt (string): Log message format.

        datefmt (dict): Log date format.

    Returns:
        New instance of :class:`ColorizedFormatter`

    Examples:
        >>> from io import StringIO
        >>>
        >>> s = StringIO()
        >>> logger = logging.getLogger()
        >>> formatter = ColorizedFormatter(datefmt=DATEFMT)
        >>> hdlr = logging.StreamHandler(s)
        >>> hdlr.setFormatter(formatter)
        >>> logger.addHandler(hdlr)
        >>> logger.info('hello world')
        >>> s.getvalue().strip()
        'hello world'
    """
    def format(self, record):
        FORMATS = {
            logging.DEBUG: f"{GREY} {self._fmt} {RESET}",
            logging.INFO: f"{GREY} {self._fmt} {RESET}",
            logging.WARNING: f"{YELLOW} {self._fmt} {RESET}",
            logging.ERROR: f"{RED} {self._fmt} {RESET}",
            logging.CRITICAL: f"{BOLD_RED} {self._fmt} {RESET}",
        }

        log_fmt = FORMATS.get(record.levelno)
        return BaseFormatter(log_fmt).format(record)


basic_formatter = logging.Formatter(BASIC_FORMAT)
bom_formatter = logging.Formatter(BOM_FORMAT)
console_formatter = logging.Formatter(CONSOLE_FORMAT)
fixed_formatter = logging.Formatter(FIXED_FORMAT, datefmt=DATEFMT)
csv_formatter = CsvFormatter(BASIC_FORMAT, datefmt=DATEFMT)
json_formatter = logging.Formatter(JSON_FORMAT, datefmt=DATEFMT)
structured_formatter = StructuredFormatter(BASIC_FORMAT, datefmt=DATEFMT)
colorized_formatter = ColorizedFormatter(BASIC_FORMAT, datefmt=DATEFMT)
