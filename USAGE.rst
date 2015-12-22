Usage
-----

pygogo is intended to be used either directly as a Python library or from the command line.

.. _library:

Library Examples
~~~~~~~~~~~~~~~~

*Hello World*

.. code-block:: bash

    import pygogo as gogo

    gogo.Gogo().logger.debug('hello world')
    gogo.Gogo().logger.error('hello error')

    # Prints the following to `stdout`

    hello world
    hello error

    # Prints the following to `stderr`

    hello error

*Log based debugging*

.. code-block:: bash

    import pygogo as gogo

    def main(verbose=False):
        logger = gogo.Gogo(__name__, verbose=verbose).logger
        logger.debug('I will log to `stdout` only if `verbose` is True')
        logger.info('I will log to `stdout` always')
        logger.warning('I will log to both `stdout` and `stderr` always')

*Disabled dual logging*

.. code-block:: bash

    import pygogo as gogo

    logger = gogo.Gogo(monolog=True).logger
    logger.debug('debug message')
    logger.info('info message')
    logger.warning('warning message')
    logger.error('error message')
    logger.critical('critical message')

    # Prints the following to `stdout.log` (all messages at level `INFO` or below):

    debug message
    info message

    # Prints the following to `stderr` (messages at level `WARNING` or above):

    warning message
    error message
    critical message

*Custom formatter* [#]_

.. code-block:: python

    import logging
    import pygogo as gogo

    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(log_format)

    logger = gogo.Gogo(
        'examples.fmt',
        low_hdlr=gogo.handlers.file_hdlr('custom_fmt.log'),
        low_formatter=formatter,
        high_level='error',
        high_formatter=formatter).logger

    # Now let's log something!

    logger.debug('debug message')
    logger.info('info message')
    logger.warn('warn message')
    logger.error('error message')
    logger.critical('critical message')

    # Prints the following to `custom_fmt.log` (all messages):

    2015-12-18 18:51:30,416 - examples.fmt.base - DEBUG - debug message
    2015-12-18 18:51:30,416 - examples.fmt.base - INFO - info message
    2015-12-18 18:51:30,416 - examples.fmt.base - WARNING - warn message
    2015-12-18 18:51:30,416 - examples.fmt.base - ERROR - error message
    2015-12-18 18:51:30,416 - examples.fmt.base - CRITICAL - critical message

    # Prints the following to `stderr` (messages at level `ERROR` or above):

    2015-12-18 18:51:30,416 - examples.fmt.base - ERROR - error message
    2015-12-18 18:51:30,416 - examples.fmt.base - CRITICAL - critical message

*Structured logging* [#]_

.. code-block:: python

    import pygogo as gogo

    formatter = gogo.formatters.structured_formatter
    kwargs = {'low_level': 'info', 'low_formatter': formatter}
    logger = gogo.Gogo('examples.structured', **kwargs).logger
    extra = {'set_value': set([1, 2, 3]), 'snowman': '☃'}
    logger.info('log message', extra=extra)  # doctest: +ELLIPSIS

    # Prints the following to `stdout`:

    {"snowman": "\u2603", "name": "examples.structured.base", "level": "INFO", "message": "log message", "time": "2015-12-18 18:52:39", "msecs": 58.973073959350586, "set_value": [1, 2, 3]}

*Using Filters to impart contextual information* [#]_

.. code-block:: python

    import logging
    import pygogo as gogo

    levels = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
    log_frmt = (
       '%(asctime)-4s %(name)-5s %(levelname)-8s IP: %(ip)-15s User: '
       '%(user)-8s %(message)s')

    formatter = logging.Formatter(log_frmt)
    going = gogo.Gogo('a', low_formatter=formatter)
    a1 = going.get_logger('b.c', ip='123.231.231.123', user='fred')
    a2 = going.get_logger('e.f', ip='192.168.0.1', user='sheila')

    # Now let's log something!

    a1.debug('A debug message')
    a1.info('An info %s', 'message')

    for level in [getattr(logging, l) for l in levels]:
       name = logging.getLevelName(level)
       a2.log(level, 'A %s msg', name)

    # Prints the following to `stdout` (all messages):

    2015-12-19 10:12:24,479 a.b.c DEBUG    IP: 123.231.231.123 User: fred     A debug message
    2015-12-19 10:12:24,479 a.b.c INFO     IP: 123.231.231.123 User: fred     An info message
    2015-12-19 10:12:24,479 a.e.f DEBUG    IP: 192.168.0.1     User: sheila   A DEBUG msg
    2015-12-19 10:12:24,479 a.e.f INFO     IP: 192.168.0.1     User: sheila   A INFO msg
    2015-12-19 10:12:24,479 a.e.f WARNING  IP: 192.168.0.1     User: sheila   A WARNING msg
    2015-12-19 10:12:24,479 a.e.f ERROR    IP: 192.168.0.1     User: sheila   A ERROR msg
    2015-12-19 10:12:24,479 a.e.f CRITICAL IP: 192.168.0.1     User: sheila   A CRITICAL msg

    # Prints the following to `stderr` (messages at level `WARNING` or above):

    2015-12-19 10:12:24,479 a.e.f WARNING  IP: 192.168.0.1     User: sheila   A WARNING msg
    2015-12-19 10:12:24,479 a.e.f ERROR    IP: 192.168.0.1     User: sheila   A ERROR msg
    2015-12-19 10:12:24,479 a.e.f CRITICAL IP: 192.168.0.1     User: sheila   A CRITICAL msg

*Multiple loggers* [#]_

.. code-block:: python

    import pygogo as gogo

    going = gogo.Gogo(
        'examples.lggrs',
        low_hdlr=gogo.handlers.file_hdlr('multi_lggrs.log'),
        low_formatter=gogo.formatters.fixed_formatter,
        high_level='info',
        high_formatter=gogo.formatters.console_formatter)

    root = going.logger
    logger1 = going.get_logger('area1')
    logger2 = going.get_logger('area2')

    # Now let's log something!

    root.info('Jackdaws love my big sphinx.')
    logger1.debug('Quick zephyrs blow, daft Jim.')
    logger1.info('How daft jumping zebras vex.')
    logger2.warning('Jail zesty vixen who grabbed pay.')
    logger2.error('The five boxing wizards jump.')

    # Prints the following to `multi_lggrs.log` (all messages):

    2015-12-18 17:21:37.417 examples.lggrs.base INFO     Jackdaws love my big sphinx.
    2015-12-18 17:21:37.417 examples.lggrs.area1 DEBUG    Quick zephyrs blow, daft Jim.
    2015-12-18 17:21:37.417 examples.lggrs.area1 INFO     How daft jumping zebras vex.
    2015-12-18 17:21:37.417 examples.lggrs.area2 WARNING  Jail zesty vixen who grabbed pay.
    2015-12-18 17:21:37.417 examples.lggrs.area2 ERROR    The five boxing wizards jump.

    # Prints the following to `stderr` (messages at level `INFO` or above):

    examples.lggrs.base: INFO     Jackdaws love my big sphinx.
    examples.lggrs.area1: INFO     How daft jumping zebras vex.
    examples.lggrs.area2: WARNING  Jail zesty vixen who grabbed pay.
    examples.lggrs.area2: ERROR    The five boxing wizards jump.

.. _interface:

CLI Examples
~~~~~~~~~~~~

Usage
^^^^^

.. code-block:: bash

    gogo [options] <message>

Examples
^^^^^^^^

*show help*

.. code-block:: bash

    pygogo -h

.. code-block:: bash

    usage: gogo [options] <message>

    description: Logs a given message

    positional arguments:
      message               The message to log (defaults to reading from stdin).

    optional arguments:
      -h, --help            show this help message and exit
      -l LEVEL, --msg-level LEVEL
                            The level to log the message (default: info).
                            Must be one of: critical, error, warning, info, debug.

      -n NAME, --name NAME  The logger name (default: pygogo)
      -D HANDLER, --high-hdlr HANDLER
                            The high pass log handler (default: stderr).
                            Must be one of: buffered, email, file, fileobj,
                            socket, stderr, stdout, syslog, webhook.

      -d HANDLER, --low-hdlr HANDLER
                            The low pass log handler (default: stdout).
                            Must be one of: buffered, email, file, fileobj,
                            socket, stderr, stdout, syslog, webhook.

      -L LEVEL, --high-level LEVEL
                            Min level to log to the high pass handler
                            (default: warning).
                            Must be one of: buffered, email, file, fileobj,
                            socket, stderr, stdout, syslog, webhook.

      -e LEVEL, --low-level LEVEL
                            Min level to log to the low pass handler
                            (default: debug).
                            Must be one of: buffered, email, file, fileobj,
                            socket, stderr, stdout, syslog, webhook.

      -F FORMAT, --high-format FORMAT
                            High pass handler log format (default: basic).
                            Must be one of: basic, bom, console, csv,
                            fixed, json, structured.

      -o FORMAT, --low-format FORMAT
                            Low pass handler log format (default: basic).
                            Must be one of: basic, bom, console, csv,
                            fixed, json, structured.

      -m, --monolog         Log high level events only to high pass handler.
      -f FILENAME, --filename FILENAME
                            The filename to log to.
                            Required for the follow handlers: file.

      -s SUBJECT, --subject SUBJECT
                            The log subject (default: You've got mail).
                            Used in the follow handlers: email.

      -u URL, --url URL     The log url. Required for the follow handlers: webhook.
      -H HOST, --host HOST  The host.
                            Used in the follow handlers: socket and syslog.

      -p NUM, --port NUM    The port number.
                            Used in the follow handlers: socket and syslog.

      -t, --tcp             Use TCP instead of UDP.
                            Used in the follow handlers: socket and syslog.

      -g, --get             Use a GET request instead of POST.
                            Used in the follow handlers: webhook.

      -v, --version         Show version and exit.
      -V, --verbose         Increase output verbosity.

*Hello World*

.. code-block:: bash

    gogo 'hello world'

*Log based debugging*

.. code-block:: bash

    gogo 'default info level will log to `stdout`'
    gogo --level=debug "debug won't log"
    gogo --level=debug -V 'verbose will log to `stdout`'
    gogo --level=info 'info will log to `stdout`'
    gogo --level=warning 'warning will log to both `stdout` and `stderr`'

    # Prints the following to `stdout`:

    default info level will log to `stdout`
    verbose will log to `stdout`
    info will log to `stdout`
    warning will log to both `stdout` and `stderr`

    # Prints the following to `stderr`:

    warning will log to both `stdout` and `stderr`

*Disable dual logging*

.. code-block:: bash

    gogo --level=debug -V 'debug message'
    gogo --level=info 'info message'
    gogo --level=warning -m 'warning message'
    gogo --level=error -m 'error message'
    gogo --level=critical -m 'critical message'

    # Prints the following to `stdout.log` (all messages at level `INFO` or below):

    debug message
    info message

    # Prints the following to `stderr` (messages at level `WARNING` or above):

    warning message
    error message
    critical message

*Structured logging*

.. code-block:: bash

    gogo --low-format=json 'log message'

    # Prints the following to `stdout`:

    {"time": "2015-12-19 11:26:53.776", "name": "pygogo.runner", "level": "INFO", "message": "log message"}

*Alternate handler*

.. code-block:: bash

    gogo --low-hdlr=file 'log message'

    # Prints the following to `pygogo.log` in the current dir (assuming the current dir is named `pygogo`):

    {"time": "2015-12-19 11:26:53.776", "name": "pygogo.runner", "level": "INFO", "message": "log message"}

.. _logging module: https://docs.python.org/2/library/logging.html
.. _Using LoggerAdapters to impart contextual information: https://docs.python.org/2/howto/logging-cookbook.html#using-loggeradapters-to-impart-contextual-information
.. _virtualenv: http://www.virtualenv.org/en/latest/index.html

Footnotes
~~~~~~~~~

.. [#] https://docs.python.org/2/howto/logging-cookbook.html#multiple-handlers-and-formatters
.. [#] https://docs.python.org/2/howto/logging-cookbook.html#implementing-structured-logging
.. [#] https://docs.python.org/2/howto/logging-cookbook.html#using-filters-to-impart-contextual-information
.. [#] https://docs.python.org/2/howto/logging-cookbook.html#logging-to-multiple-destinations
