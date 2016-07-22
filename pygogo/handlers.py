# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab

"""
pygogo.handlers
~~~~~~~~~~~~~~~

Log handlers

Examples:
    Add a stdout handler::

        >>> logger = logging.getLogger()
        >>> logger.addHandler(stdout_hdlr())
        >>> logger.info('hello world')
        hello world

Attributes:
    ENCODING (str): The module encoding
"""

from __future__ import (
    absolute_import, division, print_function, unicode_literals)

import sys
import logging
import socket

from os import environ
from logging import handlers as hdlrs
from builtins import *

ENCODING = 'utf-8'

module_hdlr = logging.StreamHandler(sys.stdout)
module_logger = logging.getLogger(__name__)
module_logger.addHandler(module_hdlr)


def stdout_hdlr(**kwargs):
    """A standard output log handler

    Returns:
        New instance of :class:`logging.StreamHandler`

    Examples:
        >>> stdout_hdlr()  # doctest: +ELLIPSIS
        <logging.StreamHandler object at 0x...>
    """
    return logging.StreamHandler(sys.stdout)


def stderr_hdlr(**kwargs):
    """A standard error log handler

    Returns:
        New instance of :class:`logging.StreamHandler`

    Examples:
        >>> stderr_hdlr()  # doctest: +ELLIPSIS
        <logging.StreamHandler object at 0x...>
    """
    return logging.StreamHandler(sys.stderr)


def fileobj_hdlr(f, **kwargs):
    """A file object log handler

    Args:
        f (obj): A file like object.

    Returns:
        New instance of :class:`logging.StreamHandler`

    Examples:
        >>> from io import StringIO
        >>> fileobj_hdlr(StringIO())  # doctest: +ELLIPSIS
        <logging.StreamHandler object at 0x...>
    """
    return logging.StreamHandler(f)


def file_hdlr(filename, mode='a', encoding=ENCODING, delay=False, **kwargs):
    """A file log handler

    Args:
        filename (string): The logfile name.

        mode (string): The file open mode (default: a, i.e., append).

        encoding (string): The file encoding (default: the module ENCODING).

        delay (bool): Defer file opening until the first call to emit
            (default: False).

    Returns:
        New instance of :class:`logging.FileHandler`

    Examples:
        >>> from tempfile import NamedTemporaryFile
        >>> f = NamedTemporaryFile()
        >>> file_hdlr(f.name)  # doctest: +ELLIPSIS
        <logging.FileHandler object at 0x...>
    """
    fkwargs = {'mode': mode, 'encoding': encoding, 'delay': delay}
    return logging.FileHandler(filename, **fkwargs)


def socket_hdlr(host='localhost', port=None, tcp=False, **kwargs):
    """A socket log handler

    Args:
        host (string): The host name (default: localhost).

        port (int): The port (default: `logging.handlers` default).

        tcp (bool): Create a TCP connection instead of UDP (default: False).

    Returns:
        New instance of either :class:`logging.handlers.DatagramHandler` or
            :class:`logging.handlers.SocketHandler`

    Examples:
        >>> socket_hdlr()  # doctest: +ELLIPSIS
        <logging.handlers.DatagramHandler object at 0x...>
        >>> socket_hdlr(tcp=True)  # doctest: +ELLIPSIS
        <logging.handlers.SocketHandler object at 0x...>
    """
    if tcp:
        def_port = logging.handlers.DEFAULT_TCP_LOGGING_PORT
        handler = hdlrs.SocketHandler
    else:
        def_port = logging.handlers.DEFAULT_UDP_LOGGING_PORT
        handler = hdlrs.DatagramHandler

    address = (host, port or def_port)
    return handler(*address)


def syslog_hdlr(host='localhost', port=None, tcp=False, **kwargs):
    """A syslog log handler

    Args:
        host (string): The host name (default: localhost).

        port (int): The port (default: `logging.handlers` default).

        tcp (bool): Create a TCP connection instead of UDP (default: False).

    Returns:
        New instance of :class:`logging.handlers.SysLogHandler`

    Examples:
        >>> syslog_hdlr()  # doctest: +ELLIPSIS
        <logging.handlers.SysLogHandler object at 0x...>
    """
    if tcp:
        def_port = logging.handlers.SYSLOG_TCP_PORT
        socktype = socket.SOCK_STREAM
    else:
        def_port = logging.handlers.SYSLOG_UDP_PORT
        socktype = socket.SOCK_DGRAM

    address = (host, port or def_port)
    return hdlrs.SysLogHandler(address, socktype=socktype)


def buffered_hdlr(target=None, capacity=4096, level='error', **kwargs):
    """A memory buffered log handler

    Args:
        target (obj): The target logger handler (default stdout).

        capacity (int): The buffer size (default 4096).

        level (string): The min event level required to flush buffer
            (default: error).

    Returns:
        New instance of :class:`logging.handlers.MemoryHandler`

    Examples:
        >>> buffered_hdlr()  # doctest: +ELLIPSIS
        <logging.handlers.MemoryHandler object at 0x...>
    """
    target = target or logging.StreamHandler(sys.stdout)
    return hdlrs.MemoryHandler(capacity, level.upper(), target)


def webhook_hdlr(url, host='localhost', port=None, get=False, **kwargs):
    """A web log handler

    Args:
        url (string): The logging endpoint.

        host (string): The host name (default: localhost).

        port (int): The port (default: None).

        get (bool): Use a GET request instead of POST (default: False).

    Returns:
        New instance of :class:`logging.handlers.HTTPHandler`

    Examples:
        >>> webhook_hdlr('api/log', 'mysite.com')  # doctest: +ELLIPSIS
        <logging.handlers.HTTPHandler object at 0x...>
    """
    method = 'GET' if get else 'POST'
    host = '%s:%s' % (host, port) if port else host
    return hdlrs.HTTPHandler(host, url, method=method)


def email_hdlr(subject=None, **kwargs):
    """An email log handler

    Args:
        subject (str): The email subject (default: You've got mail.).

        kwargs(dict): Keyword arguments.

    Kwargs:
        host (str): The email server host (default: localhost).

        port (str): The email sever port (default: None).

        sender (str): The email sender (default: the system username at gmail).

        recipients (List[str]): The email recipients (default: the system
            username at gmail).

        username (str): The email sever username (default: None).

        password (str): The email sever password (default: None).

    Returns:
        New instance of :class:`logging.handlers.SMTPHandler`

    Examples:
        >>> email_hdlr('hello world')  # doctest: +ELLIPSIS
        <logging.handlers.SMTPHandler object at 0x...>
    """
    host = kwargs.get('host', 'localhost')
    port = kwargs.get('port')
    address = (host, port) if port else host
    sender = kwargs.get('sender', '%s@gmail.com' % environ.get('USER'))
    def_recipient = '%s@gmail.com' % environ.get('USER')
    recipients = kwargs.get('recipients', [def_recipient])
    subject = kwargs.get('subject', "You've got mail")
    username = kwargs.get('username')
    password = kwargs.get('password')

    args = (address, sender, recipients, subject)
    credentials = (username, password) if username or password else None
    return hdlrs.SMTPHandler(*args, credentials=credentials)
