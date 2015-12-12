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

from json import JSONEncoder

BASIC_FORMAT = '%(message)s'
CONSOLE_FORMAT = '%(name)-12s: %(levelname)-8s %(message)s'
FIXED_FORMAT = '%(asctime)s.%(msecs)d %(name)-12s %(levelname)-8s %(message)s'
CSV_FORMAT = '%(asctime)s.%(msecs)d,%(name)s,%(levelname)s,"%(message)s"'
JSON_FORMAT = (
    '{"time": "%(asctime)s.%(msecs)d", "name": "%(name)s", "level":'
    ' "%(levelname)s", "message": "%(message)s"}')

DATEFMT = '%Y-%m-%d %H:%M:%S'

basic_formatter = logging.Formatter(BASIC_FORMAT)
console_formatter = logging.Formatter(CONSOLE_FORMAT)
fixed_formatter = logging.Formatter(FIXED_FORMAT, datefmt=DATEFMT)
csv_formatter = logging.Formatter(CSV_FORMAT, datefmt=DATEFMT)
json_formatter = logging.Formatter(JSON_FORMAT, datefmt=DATEFMT)


class CustomEncoder(JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'real'):
            encoded = float(obj)
        elif set(['quantize', 'year', 'hour']).intersection(dir(obj)):
            encoded = str(obj)
        elif hasattr(obj, 'union'):
            encoded = tuple(obj)
        elif set(['next', 'union', '__iter__']).intersection(dir(obj)):
            encoded = list(obj)
        elif isinstance(obj, unicode):
            return obj.encode('unicode_escape').decode('ascii')
        else:
            encoded = super(CustomEncoder, self).default(obj)

        return encoded


class StructuredMessage(object):
    """Converts a message and kwargs to a json string

    Examples:
        >>> import sys
        >>>
        >>> logger = logging.getLogger()
        >>> hdlr = logging.StreamHandler(sys.stdout)
        >>> hdlr.setFormatter(basic_formatter)
        >>> logger.addHandler(hdlr)
        >>> logger.info(StructuredMessage('hello world', key='value'))
        {"message": "hello world", "key": "value"}
    """
    def __init__(self, message=None, **kwargs):
        kwargs['message'] = message
        self.kwargs = kwargs

    def __str__(self):
        return CustomEncoder().encode(self.kwargs)


class StructuredAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        extra = kwargs.get('extra', {})
        extra.update(self.extra)
        kwargs['extra'] = extra
        return StructuredMessage(msg, **extra), kwargs


class StructuredFormatter(logging.Formatter):
    """A logging formatter that converts log details to a json string

    """
    def __init__(self, *args, **kwargs):
        empty_record = logging.makeLogRecord({})
        self.filterer = lambda k: k not in empty_record.__dict__
        super(StructuredFormatter, self).__init__(*args, **kwargs)

    def format(self, record):
        extra = {
            'message': record.getMessage(),
            'time': self.formatTime(record, self.datefmt),
            'name': record.name,
            'level': record.levelname}

        keys = filter(self.filterer, record.__dict__)
        extra.update({k: record.__dict__[k] for k in keys})
        return CustomEncoder().encode(extra)

structured_formatter = StructuredFormatter(BASIC_FORMAT, datefmt=DATEFMT)
