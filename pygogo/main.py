#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab

""" A Python logging library with super powers """

from __future__ import (
    absolute_import, division, print_function, with_statement,
    unicode_literals)

import sys
import itertools as it
import pygogo as gogo

from os import getcwd, path as p
from argparse import RawTextHelpFormatter, ArgumentParser

hdlrs_full = filter(lambda h: h.endswith('hdlr'), dir(gogo.handlers))
hdlrs = [h[:-5] for h in hdlrs_full]
levels = ['critical', 'error', 'warning', 'info', 'debug']
frmtrs_full = filter(lambda h: h.endswith('formatter'), dir(gogo.formatters))
formats = [f[:-10] for f in frmtrs_full]
curdir = p.basename(getcwd())

parser = ArgumentParser(
    description='description: Command description', prog='pygogo',
    usage='%(prog)s [options] <message>', formatter_class=RawTextHelpFormatter)

parser.add_argument(
    dest='message', nargs='?', default=sys.stdin,
    help='The message to log (defaults to reading from stdin).')

parser.add_argument(
    '-l', '--level', metavar='LEVEL', choices=levels, default='info',
    help=(
        "The level to log the message (default: info).\n"
        "Must be one of: %s,\n%s.\n\n" % (
            ', '.join(levels[:4]), ', '.join(levels[4:]))))

parser.add_argument(
    '-n', '--name', default=curdir,
    help="The logger name (default: %s).\n\n" % curdir)

parser.add_argument(
    '-D', '--high-hdlr', metavar='HANDLER', choices=hdlrs, default='stderr',
    help=(
        "The high pass log handler (default: stderr).\n"
        "Must be one of: %s,\n%s.\n\n" % (
            ', '.join(hdlrs[:4]), ', '.join(hdlrs[4:]))))

parser.add_argument(
    '-d', '--low-hdlr', metavar='HANDLER', choices=hdlrs, default='stdout',
    help=(
        "The low pass log handler (default: stdout).\n"
        "Must be one of: %s,\n%s.\n\n" % (
            ', '.join(hdlrs[:4]), ', '.join(hdlrs[4:]))))

parser.add_argument(
    '-L', '--high-level', metavar='LEVEL', choices=levels, default='warning',
    help=(
        "Min level to log to the high pass handler\n(default: warning)."
        "\nMust be one of: %s,\n%s.\n\n" % (
            ', '.join(hdlrs[:4]), ', '.join(hdlrs[4:]))))

parser.add_argument(
    '-e', '--low-level', metavar='LEVEL', choices=levels, default='debug',
    help=(
        "Min level to log to the low pass handler\n(default: debug)."
        "\nMust be one of: %s,\n%s.\n\n" % (
            ', '.join(hdlrs[:4]), ', '.join(hdlrs[4:]))))

parser.add_argument(
    '-F', '--high-format', metavar='FORMAT', choices=formats, default='json',
    help=(
        "High pass handler log format (default: json)."
        "\nMust be one of: %s,\n%s.\n\n" % (
            ', '.join(formats[:4]), ', '.join(formats[4:]))))

parser.add_argument(
    '-o', '--low-format', metavar='FORMAT', choices=formats, default='basic',
    help=(
        "Low pass handler log format (default: basic)."
        "\nMust be one of: %s,\n%s.\n\n" % (
            ', '.join(formats[:4]), ', '.join(formats[4:]))))

parser.add_argument(
    '-m', '--monolog', action='store_true', default=False,
    help="Log high level events only to high pass handler.")

parser.add_argument(
    '-f', '--filename', action='append', default=['gogo.log'],
    help="The filename to log to.\nRequired for the follow handlers: file.\n\n")

parser.add_argument(
    '-s', '--subject', default=["You've got mail"], action='append',
    help=(
        "The log subject (default: You've got mail)."
        "\nUsed in the following handlers: email.\n\n"))

parser.add_argument(
    '-u', '--url', action='append', default=[''],
    help="The log url. Required for the follow handlers: webhook.")

parser.add_argument(
    '-H', '--host', default=['localhost'], action='append',
    help="The host.\nUsed in the follow handlers: socket and syslog.\n\n")

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

args = parser.parse_args()


def run():
    gogo_logger = gogo.Gogo(__name__, verbose=args.verbose).logger

    if args.version:
        gogo_logger.info('gogo v%s' % gogo.__version__)
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

    logger = gogo.Gogo(args.name, **nkwargs).logger

    try:
        message = args.message.read()
    except AttributeError:
        message = args.message

    getattr(logger, args.level)(message)
    exit(0)

if __name__ == '__main__':
    run()
