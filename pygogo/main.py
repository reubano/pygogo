#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab

""" A Python logging library with super powers """

from __future__ import (
    absolute_import, division, print_function, unicode_literals)

import sys
import itertools as it

from os import getcwd, path as p
from argparse import RawTextHelpFormatter, ArgumentParser
from builtins import *

import pygogo as gogo

HDLRS_FULL = tuple(h for h in dir(gogo.handlers) if h.endswith('hdlr'))
HDLRS = tuple(h[:-5] for h in HDLRS_FULL)
LEVELS = ('critical', 'error', 'warning', 'info', 'debug')
FRMTRS_FULL = tuple(f for f in dir(gogo.formatters) if f.endswith('formatter'))
FORMATS = tuple(f[:-10] for f in FRMTRS_FULL)
CURDIR = p.basename(getcwd())
LOGFILE = '%s.log' % CURDIR

parser = ArgumentParser(
    description='description: Logs a given message', prog='gogo',
    usage='%(prog)s [options] <message>', formatter_class=RawTextHelpFormatter)

parser.add_argument(
    dest='message', nargs='?', default=sys.stdin,
    help='The message to log (default: reads from stdin).')

parser.add_argument(
    '-l', '--level', metavar='LEVEL', choices=LEVELS, default='info',
    help=(
        "The level to log the message (default: info).\n"
        "Must be one of: %s,\n%s.\n\n" % (
            ', '.join(LEVELS[:4]), ', '.join(LEVELS[4:]))))

parser.add_argument(
    '-n', '--name', default=CURDIR,
    help="The logger name (default: %s).\n\n" % CURDIR)

parser.add_argument(
    '-D', '--high-hdlr', metavar='HANDLER', choices=HDLRS, default='stderr',
    help=(
        "The high pass log handler (default: stderr).\n"
        "Must be one of: %s,\n%s.\n\n" % (
            ', '.join(HDLRS[:4]), ', '.join(HDLRS[4:]))))

parser.add_argument(
    '-d', '--low-hdlr', metavar='HANDLER', choices=HDLRS, default='stdout',
    help=(
        "The low pass log handler (default: stdout).\n"
        "Must be one of: %s,\n%s.\n\n" % (
            ', '.join(HDLRS[:4]), ', '.join(HDLRS[4:]))))

parser.add_argument(
    '-L', '--high-level', metavar='LEVEL', choices=LEVELS, default='warning',
    help=(
        "Min level to log to the high pass handler\n"
        "(default: warning). Must be one of: %s,\n%s.\n\n" % (
            ', '.join(LEVELS[:1]), ', '.join(LEVELS[1:]))))

parser.add_argument(
    '-e', '--low-level', metavar='LEVEL', choices=LEVELS, default='debug',
    help=(
        "Min level to log to the low pass handler\n"
        "(default: debug). Must be one of: %s,\n%s.\n\n" % (
            ', '.join(LEVELS[:1]), ', '.join(LEVELS[1:]))))

parser.add_argument(
    '-F', '--high-format', metavar='FORMAT', choices=FORMATS, default='basic',
    help=(
        "High pass handler log format (default: basic)."
        "\nMust be one of: %s,\n%s.\n\n" % (
            ', '.join(FORMATS[:4]), ', '.join(FORMATS[4:]))))

parser.add_argument(
    '-o', '--low-format', metavar='FORMAT', choices=FORMATS, default='basic',
    help=(
        "Low pass handler log format (default: basic)."
        "\nMust be one of: %s,\n%s.\n\n" % (
            ', '.join(FORMATS[:4]), ', '.join(FORMATS[4:]))))

parser.add_argument(
    '-m', '--monolog', action='store_true', default=False,
    help="Log high level events only to high pass handler.\n\n")

parser.add_argument(
    '-f', '--filename', action='append', default=[LOGFILE],
    help=(
        "The filename to log to  (default: %s).\nUsed in the following "
        "handlers: file.\n\n") % LOGFILE)

parser.add_argument(
    '-s', '--subject', default=["You've got mail"], action='append',
    help=(
        "The log subject (default: You've got mail)."
        "\nUsed in the following handlers: email.\n\n"))

parser.add_argument(
    '-u', '--url', action='append', default=[''],
    help="The log url. Required for the following handlers:\nwebhook.\n\n")

parser.add_argument(
    '-H', '--host', default=['localhost'], action='append',
    help=(
        "The host (default: localhost).\nUsed in the following handlers: "
        "socket and syslog.\n\n"))

parser.add_argument(
    '-p', '--port', metavar='NUM', type=int, action='append', default=[''],
    help=(
        "The port number (default: Python logging default).\nUsed in the "
        "following handlers: socket and syslog.\n\n"))

parser.add_argument(
    '-t', '--tcp', action='count', default=0, help=(
        "Use TCP instead of UDP.\nUsed in the following handlers: socket and "
        "syslog.\n\n"))

parser.add_argument(
    '-g', '--get', action='count', default=0, help=(
        "Use a GET request instead of POST.\nUsed in the following handlers: "
        "webhook.\n\n"))

parser.add_argument(
    '-v', '--version', help="Show version and exit.", action='store_true',
    default=False)

parser.add_argument(
    '-V', '--verbose', help='Increase output verbosity.', action='store_true',
    default=False)


def run():
    """CLI runner
    """
    args = parser.parse_args()
    gogo_logger = gogo.Gogo(__name__, verbose=args.verbose).get_logger('run')

    if args.version:
        gogo_logger.info('gogo v%s' % gogo.__version__)
        exit(0)

    counted = {'get', 'tcp'}
    appended = {'filename', 'subject', 'url', 'host', 'port'}
    items = args._get_kwargs()
    counted_args = [i for i in items if i[0] in counted]
    appended_args = [i for i in items if i[0] in appended]

    high_appended_args = [(k, v[0]) for k, v in appended_args]
    high_counted_args = [(k, v > 0) for k, v in counted_args]
    high_kwargs = dict(it.chain(high_appended_args, high_counted_args))

    low_appended_args = [(k, v[-1]) for k, v in appended_args]
    low_counted_args = [(k, v > 1) for k, v in counted_args]
    low_kwargs = dict(it.chain(low_appended_args, low_counted_args))

    high_hdlr = getattr(gogo.handlers, '%s_hdlr' % args.high_hdlr)
    low_hdlr = getattr(gogo.handlers, '%s_hdlr' % args.low_hdlr)
    high_format = getattr(gogo.formatters, '%s_formatter' % args.high_format)
    low_format = getattr(gogo.formatters, '%s_formatter' % args.low_format)

    nkwargs = {
        'verbose': args.verbose,
        'high_level': args.high_level.upper(),
        'low_level': args.low_level.upper(),
        'high_formatter': high_format,
        'low_formatter': low_format,
        'monolog': args.monolog,
        'high_hdlr': high_hdlr(**high_kwargs),
        'low_hdlr': low_hdlr(**low_kwargs)}

    logger = gogo.Gogo(args.name, **nkwargs).get_logger('runner')

    try:
        message = args.message.read()
    except AttributeError:
        message = args.message

    getattr(logger, args.level)(message)
    exit(0)

if __name__ == '__main__':
    run()
