#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab

""" A Python logging library with super powers """

from __future__ import (
    absolute_import, division, print_function, with_statement,
    unicode_literals)

import sys
import itertools as it

from os import curdir
from argparse import RawTextHelpFormatter, ArgumentParser

from pygogo import __version__ as version, handlers
from pygogo.logger import Logger

hdlrs = filter(lambda h: h.endswith('hdlr'), dir(handlers))
choices = [h[:-5] for h in hdlrs]

parser = ArgumentParser(
    description='description: Command description', prog='pygogo',
    usage='%(prog)s [options] <message>', formatter_class=RawTextHelpFormatter)

parser.add_argument(
    dest='message', nargs='?', default=sys.stdin,
    help='the message to log (defaults to reading from stdin)')

parser.add_argument(
    '-l', '--msg-level', metavar='LEVEL', default='info',
    help="The level to log the message")

parser.add_argument('-n', '--name', help="The logger name", default=curdir)
parser.add_argument(
    '--high-hdlr', help="the high pass log handler (default: stdout)",
    choices=choices, default='stdout')

parser.add_argument(
    '--low-hdlr', help="the low pass log handler (default: stdout)",
    choices=choices, default='stdout')

parser.add_argument(
    '-L', '--high-level', metavar='LEVEL', default='warning',
    help="The min level to log to the high pass handler")

parser.add_argument(
    '-e', '--low-level', metavar='LEVEL', default='debug',
    help="The min level to log to the low pass handler")

parser.add_argument(
    '-d', '--monolog', action='store_true', default=False,
    help="log high level events only to high pass handler")

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
    pygogo_logger = Logger(__name__, low_level=level).logger

    if args.version:
        pygogo_logger.info('pygogo v%s' % version)
        exit(0)

    counted = set(['get', 'tcp'])
    appended = set(['filename', 'subject', 'url', 'host', 'port'])
    items = args._get_kwargs()
    counted_args = filter(lambda x: x[0] in counted, items)
    appended_args = filter(lambda x: x[0] in appended, items)

    high_appended_args = [(k, v[0]) for k, v in appended_args]
    high_counted_args = [(k, v > 0) for k, v in counted_args]
    high_kwargs = dict(it.chain(high_appended_args, high_counted_args))

    low_appended_args = [(k, v[-1]) for k, v in appended_args]
    low_counted_args = [(k, v > 1) for k, v in counted_args]
    low_kwargs = dict(it.chain(low_appended_args, low_counted_args))

    high_pass_hdlr = getattr(handlers, '%s_hdlr' % args.high_hdlr)
    low_pass_hdlr = getattr(handlers, '%s_hdlr' % args.low_hdlr)
    nkwargs = {
        'high_level': args.high_level,
        'low_level': args.low_level,
        'monolog': args.monolog,
        'high_pass_hdlr': high_pass_hdlr(**high_kwargs),
        'low_pass_hdlr': low_pass_hdlr(**low_kwargs)}

    logger = Logger(args.name, **nkwargs).logger

    try:
        message = args.message.read()
    except AttributeError:
        message = args.message

    getattr(logger, args.msg_level)(message)
    exit(0)

if __name__ == '__main__':
    run()
