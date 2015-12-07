#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab

""" A Python logging framework with super powers """

from __future__ import (
    absolute_import, division, print_function, with_statement,
    unicode_literals)

import sys
import itertools as it

from os import curdir
from argparse import RawTextHelpFormatter, ArgumentParser

from gogo import __version__ as version, handlers
from gogo.logger import Logger

hdlrs = filter(lambda h: h.endswith('hdlr'), dir(handlers))
choices = [h[:-5] for h in hdlrs]

parser = ArgumentParser(
    description='description: Command description', prog='gogo',
    usage='%(prog)s [options] <message>', formatter_class=RawTextHelpFormatter)

parser.add_argument(
    dest='message', nargs='?', default=sys.stdin,
    help='the message to log (defaults to reading from stdin)')

parser.add_argument(
    '-l', '--msg-level', metavar='LEVEL', default='info',
    help="The level to log the message")

parser.add_argument('-n', '--name', help="The logger name", default=curdir)
parser.add_argument(
    '--prim-hdlr', help="the primary log handler (default: stdout)",
    choices=choices, default='stdout')

parser.add_argument(
    '--sec-hdlr', help="the secondary log handler (default: stdout)",
    choices=choices, default='stdout')

parser.add_argument(
    '-L', '--prim-level', metavar='LEVEL', default='warning',
    help="The min level to log to primary handler")

parser.add_argument(
    '-e', '--sec-level', metavar='LEVEL', default='debug',
    help="The min level to log to secondary handler")

parser.add_argument(
    '-m', '--multilog', action='store_true', default=False,
    help="always log to secondary handler")

parser.add_argument(
    '-f', '--filename', action='append', default=[''],
    help="the filename (required for the follow handlers: file)")

parser.add_argument(
    '-s', '--subject', default=["You've got mail."], action='append',
    help="the subject (used in the follow handlers: email)")

parser.add_argument(
    '-u', '--url', action='append', default=[''],
    help="the url (required for the follow handlers: webhook)")

parser.add_argument(
    '-H', '--host', default=['localhost'], action='append',
    help="the host (used in the follow handlers: socket, syslog)")

parser.add_argument(
    '-p', '--port', metavar='NUM', type=int, action='append', default=[''],
    help=(
        "the port number (used in the follow handlers: socket, "
        "syslog)"))

parser.add_argument(
    '-t', '--tcp', action='count', default=0, help=(
        "use TCP instead of UDP (used in the follow handlers: socket, "
        "syslog)"))

parser.add_argument(
    '-g', '--get', action='count', default=0, help=(
        "use a GET request instead of POST (used in the follow handlers: "
        "webhook)"))

parser.add_argument(
    '-v', '--version', help="show version and exit", action='store_true',
    default=False)

parser.add_argument(
    '-V', '--verbose', help='increase output verbosity', action='store_true',
    default=False)

args = parser.parse_args()


def run():
    level = 'DEBUG' if args.verbose else 'INFO'
    gogo_logger = Logger(__name__, sec_level=level).logger

    if args.version:
        gogo_logger.info('gogo v%s' % version)
        exit(0)

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

    primary_hdlr = getattr(handlers, '%s_hdlr' % args.prim_hdlr)
    secondary_hdlr = getattr(handlers, '%s_hdlr' % args.sec_hdlr)
    nkwargs = {
        'prim_level': args.prim_level,
        'sec_level': args.sec_level,
        'multilog': args.multilog,
        'primary_hdlr': primary_hdlr(**prim_kwargs),
        'secondary_hdlr': secondary_hdlr(**sec_kwargs)}

    logger = Logger(args.name, **nkwargs).logger

    try:
        message = args.message.read()
    except AttributeError:
        message = args.message

    getattr(logger, args.msg_level)(message)
    exit(0)

if __name__ == '__main__':
    run()
