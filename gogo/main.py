#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab

""" A Python logger with super powers """

from __future__ import (
    absolute_import, division, print_function, with_statement,
    unicode_literals)

import sys
import itertools as it

from os import curdir
from importlib import import_module
from argparse import FileType, RawTextHelpFormatter, ArgumentParser

from gogo import __version__ as version
from gogo.logger import Logger

handlers = ()

parser = ArgumentParser(
    description='description: Command description', prog='pyconvert',
    usage='%(prog)s [options] <message>', formatter_class=RawTextHelpFormatter)

parser.add_argument(
    dest='message', type=FileType('r+b'), nargs='?', default=sys.stdin,
    help=('the message or file to log (defaults to stdin)'))

parser.add_argument(
    '-l', '--msg-level', help="The level to log the message", default='INFO')

parser.add_argument('-n', '--name', help="The logger name", default=curdir)
parser.add_argument(
    '-p', '--prim-hdlr', metavar='HDLR', help="the primary log handler",
    choices=handlers, default='stderr_hdlr')

parser.add_argument(
    '-s', '--sec-hdlr', metavar='HDLR', help="the secondary log handler",
    choices=handlers, default='stdout_hdlr')

parser.add_argument(
    '-l', '--prim-level', help="The min level to log to primary handler",
    default='WARNING')

parser.add_argument(
    '-m', '--sec-level', metavar='LEVEL', default='DEBUG',
    help="The min level to log to secondary handler")

parser.add_argument(
    '-m', '--multilog', action='store_true', default=False,
    help="always log to secondary handler")

parser.add_argument(
    '-f', '--filename', action='append',
    help="the filename (required for the follow handlers: file_hdlr)")

parser.add_argument(
    '-s', '--subject', default="You've got mail.", action='append',
    help="the subject (used in the follow handlers: email_hdlr)")

parser.add_argument(
    '-u', '--url', action='append',
    help="the url (required for the follow handlers: webhook_hdlr)")

parser.add_argument(
    '-h', '--host', default='localhost', action='append',
    help="the host (used in the follow handlers: socket_hdlr, syslog_hdlr)")

parser.add_argument(
    '-p', '--port', metavar='NUM', type=int, action='append', help=(
        "the port number (used in the follow handlers: socket_hdlr, "
        "syslog_hdlr)"))

parser.add_argument(
    '-t', '--tcp', action='count', default=False, help=(
        "use TCP instead of UDP (used in the follow handlers: socket_hdlr, "
        "syslog_hdlr)"))

parser.add_argument(
    '-g', '--get', action='count', default=False, help=(
        "use a GET request instead of POST (used in the follow handlers: "
        "webhook_hdlr)"))

parser.add_argument(
    '--version', action='version', version='%(prog)s %s' % version)

parser.add_argument(
    '-V', '--verbose', help='increase output verbosity', action='store_true',
    default=False)

args = parser.parse_args()


def run():
    counted = set(['get', 'tcp'])
    appended = set(['filename', 'subject', 'url', 'host', 'port'])
    items = args._get_kwargs()
    counted_args = filter(lambda x: x[0] in counted, items)
    appended_args = filter(lambda x: x[0] in appended, items)

    prim_appended_args = [(k, v[0]) for k, v in appended_args]
    prim_counted_args = [(k, v > 0) for k, v in counted_args]
    prim_kwargs = dict(it.chain(prim_appended_args, prim_counted_args))

    sec_appended_args = [(k, v[-1]) for k, v in appended_args]
    sec_counted_args = [(k, v > 1) for k, v in counted_args]
    sec_kwargs = dict(it.chain(sec_appended_args, sec_counted_args))

    level = 'DEBUG' if args.verbose else 'INFO'
    logger = Logger(__file__, sec_level=level).logger

    primary_hdlr = import_module('handlers', args.primary)
    secondary_hdlr = import_module('handlers', args.secondary)

    nkwargs = {
        'prim_level': args.prim_level,
        'sec_level': args.sec_level,
        'multilog': args.multilog,
        'primary_hdlr': primary_hdlr(**prim_kwargs),
        'secondary_hdlr': secondary_hdlr(**sec_kwargs)}

    logger = Logger(args.name, **nkwargs).logger
    getattr(logger, args.msg_level)(args.message)
    exit(0)

if __name__ == '__main__':
    run()
