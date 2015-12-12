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
"""

from __future__ import (
    absolute_import, division, print_function, with_statement,
    unicode_literals)

import sys
import logging
import socket

from os import environ
from logging import handlers as hdlrs
from pygogo import ENCODING


def stdout_hdlr(**kwargs):
    return logging.StreamHandler(sys.stdout)


def stderr_hdlr(**kwargs):
    return logging.StreamHandler(sys.stderr)


def fileobj_hdlr(f, **kwargs):
    return logging.StreamHandler(f)


def file_hdlr(filename, mode='a', encoding=ENCODING, delay=False, **kwargs):
    fkwargs = {'mode': mode, 'encoding': encoding, 'delay': delay}
    return logging.FileHandler(filename, **fkwargs)


def socket_hdlr(host='localhost', port=None, tcp=False, **kwargs):
    if tcp:
        def_port = logging.handlers.DEFAULT_TCP_LOGGING_PORT
        handler = hdlrs.SocketHandler
    else:
        def_port = logging.handlers.DEFAULT_UDP_LOGGING_PORT
        handler = hdlrs.DatagramHandler

    address = (host, port or def_port)
    return handler(*address)


def syslog_hdlr(host='localhost', port=None, tcp=False, **kwargs):
    if tcp:
        def_port = logging.handlers.SYSLOG_TCP_PORT
        socktype = socket.SOCK_STREAM
    else:
        def_port = logging.handlers.SYSLOG_UDP_PORT
        socktype = socket.SOCK_DGRAM

    address = (host, port or def_port)
    return hdlrs.SysLogHandler(address, socktype=socktype)


def buffered_hdlr(target, capacity=4096, level='error', **kwargs):
    return hdlrs.MemoryHandler(capacity, level.upper(), target)


def webhook_hdlr(url, host='localhost', port=None, get=False, **kwargs):
    method = 'GET' if get else 'POST'
    host = '%s:%s' % (host, port) if port else host
    return hdlrs.HTTPHandler(host, url, method=method)


def email_hdlr(subject=None, **kwargs):
    """An email log handler

    Args:
        subject (str): The email subject (default: You've got mail.).

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
