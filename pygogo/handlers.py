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

import sys
import logging
import socket

from os import environ
from logging import handlers as hdlrs

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

ENCODING = "utf-8"

module_hdlr = logging.StreamHandler(sys.stdout)
module_logger = logging.getLogger(__name__)
module_logger.addHandler(module_hdlr)


def stdout_hdlr(**kwargs):
    """A standard output log handler

    Returns:
        New instance of :class:`logging.StreamHandler`

    Examples:
        >>> stdout_hdlr()  # doctest: +ELLIPSIS
        <...StreamHandler...>
    """
    return logging.StreamHandler(sys.stdout)


def stderr_hdlr(**kwargs):
    """A standard error log handler

    Returns:
        New instance of :class:`logging.StreamHandler`

    Examples:
        >>> stderr_hdlr()  # doctest: +ELLIPSIS
        <...StreamHandler...>
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
        <...StreamHandler...>
    """
    return logging.StreamHandler(f)


def file_hdlr(filename, mode="a", encoding=ENCODING, delay=False, **kwargs):
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
        <...FileHandler...>
    """
    fkwargs = {"mode": mode, "encoding": encoding, "delay": delay}
    return logging.FileHandler(filename, **fkwargs)


def socket_hdlr(host="localhost", port=None, tcp=False, **kwargs):
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
        <...DatagramHandler...>
        >>> socket_hdlr(tcp=True)  # doctest: +ELLIPSIS
        <...SocketHandler...>
    """
    if tcp:
        def_port = hdlrs.DEFAULT_TCP_LOGGING_PORT
        handler = hdlrs.SocketHandler
    else:
        def_port = hdlrs.DEFAULT_UDP_LOGGING_PORT
        handler = hdlrs.DatagramHandler

    address = (host, port or def_port)
    return handler(*address)


def syslog_hdlr(host="localhost", port=None, tcp=False, **kwargs):
    """A syslog log handler

    Args:
        host (string): The host name (default: localhost). Set to None to use
            the platform dependent domain socket.

        port (int): The port (default: `logging.handlers` default).

        tcp (bool): Create a TCP connection instead of UDP (default: False).

    Returns:
        New instance of :class:`logging.handlers.SysLogHandler`

    Examples:
        >>> syslog_hdlr()  # doctest: +ELLIPSIS
        <...SysLogHandler...>
    """
    # http://stackoverflow.com/a/13874620/408556
    DEF_SOCKETS = {"linux2": "/dev/log", "darwin": "/var/run/syslog"}

    if tcp:
        def_port = hdlrs.SYSLOG_TCP_PORT
        socktype = socket.SOCK_STREAM
    else:
        def_port = hdlrs.SYSLOG_UDP_PORT
        socktype = socket.SOCK_DGRAM

    if kwargs.get("address"):
        address = kwargs["address"]
    elif host:
        address = (host, port or def_port)
    elif sys.platform in DEF_SOCKETS:
        address = DEF_SOCKETS[sys.platform]
    else:
        msg = "Domain socket location for {} is not supported."
        raise ValueError(msg.format(sys.platform))

    if kwargs.get("facility"):
        facility = kwargs["facility"]
    elif kwargs.get("local_num") and 8 > kwargs["local_num"] >= 0:
        # http://unix.stackexchange.com/a/146993
        value = "LOG_LOCAL{}".format(kwargs["facility"])
        facility = getattr(hdlrs.SysLogHandler, value)
    else:
        facility = hdlrs.SysLogHandler.LOG_USER

    return hdlrs.SysLogHandler(address, facility=facility, socktype=socktype)


def buffered_hdlr(target=None, capacity=4096, level="error", **kwargs):
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
        <...MemoryHandler...>
    """
    target = target or logging.StreamHandler(sys.stdout)
    return hdlrs.MemoryHandler(capacity, level.upper(), target)


def webhook_hdlr(url, **kwargs):
    """A web log handler

    Args:
        url (string): The logging endpoint.

    Kwargs:
        get (bool): Use a GET request instead of POST (default: False).

    Returns:
        New instance of :class:`logging.handlers.HTTPHandler`

    Examples:
        >>> webhook_hdlr('http://api.mysite.com/log')  # doctest: +ELLIPSIS
        <...HTTPHandler...>
    """
    parsed = urlparse(url)
    secure = parsed.scheme == "https"
    method = "GET" if kwargs.get("get") else "POST"
    args = (parsed.netloc, parsed.path)

    try:
        hdlr = hdlrs.HTTPHandler(*args, method=method, secure=secure)
    except TypeError:
        hdlr = hdlrs.HTTPHandler(*args, method=method)

    return hdlr


def email_hdlr(subject="You've got mail", host="localhost", port=587, **kwargs):
    """An email log handler

    Kwargs:
        subject (str): The email subject (default: You've got mail.).
        host (str): The email server host (default: localhost).
        port (str): The email sever port (default: 587).
        sender (str): The email sender (default: the system username at gmail).

        recipients (List[str]): The email recipients (default: the system
            username at gmail).

        username (str): The email sever username (default: None).
        password (str): The email sever password (default: None).

    Returns:
        New instance of :class:`logging.handlers.SMTPHandler`

    Examples:
        >>> email_hdlr('hello world')  # doctest: +ELLIPSIS
        <...SMTPHandler...>
    """
    address = (host, port) if port else host
    def_email = "%s@gmail.com" % environ.get("USER")
    sender = kwargs.get("sender", def_email)
    recipients = kwargs.get("recipients", [def_email])
    username = kwargs.get("username")
    password = kwargs.get("password")

    args = (address, sender, recipients, subject)
    credentials = (username, password) if username or password else None
    return hdlrs.SMTPHandler(*args, credentials=credentials)
