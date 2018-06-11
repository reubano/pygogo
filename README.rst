pygogo: a Python logger with super powers
=========================================

|travis| |versions| |pypi|

.. image:: https://raw.githubusercontent.com/reubano/pygogo/master/gogo.png
    :alt: sample pygogo usage
    :width: 800
    :align: center

Index
-----
`Introduction`_ | `Requirements`_ | `Motivation`_ | `Usage`_ | `Installation`_ |
`Project Structure`_ | `Design Principles`_ | `Structured Logging`_ |
`Formatters`_ | `Handlers`_ | `Scripts`_ | `Contributing`_ | `License`_

Introduction
------------

pygogo is a Python logging `library`_ and `command-line interface`_ with super powers.
pygogo leverages the standard Python `logging module`_ under the hood, so there's
no need to learn yet-another logging library. The default implementation sends
all messages to ``stdout``, and any messages at level ``WARNING`` or above to ``stderr``.

With pygogo, you can

- Log via different handlers depending on the event severity
- Format log messages as plain text, csv, json, and more..
- Send logs to stdout, stderr, file, email, sockets, and more..
- Inter-operate with the standard python logging module
- and much more...

Requirements
------------

pygogo has been tested and is known to work on Python 2.7, 3.4, and 3.5;
PyPy2 5.1.1; and PyPy3 2.4

Motivation
----------

The standard logging module is great, but requires a ton of boilerplate before
you can do anything really interesting with it. I designed pygogo to provide
many useful logging use-cases out of the box. A reimplementation of
`Using LoggerAdapters to impart contextual information`_ is shown below:

.. _Using LoggerAdapters to impart contextual information: https://docs.python.org/2/howto/logging-cookbook.html#using-loggeradapters-to-impart-contextual-information

.. code-block:: python

    import pygogo as gogo

    logger = gogo.Gogo(__name__).get_structured_logger(connid='1234')
    logger.info('log message')

    # Prints the following to stdout

    {"message": "log message", "connid": "1234"}

Usage
-----

pygogo is intended to be used either directly as a Python `library`_ or from
the terminal via the `command-line interface`_.

Library
~~~~~~~

Examples
^^^^^^^^

*Hello World*

.. code-block:: python

    from pygogo import logger

    logger.debug('hello world')
    logger.error('hello error')

    # Prints the following to `stdout`

    hello world
    hello error

    # Prints the following to `stderr`

    hello error

*Log based debugging*

.. code-block:: python

    import pygogo as gogo

    def main(verbose=False):
        logger = gogo.Gogo(__name__, verbose=verbose).logger
        logger.debug('I will log to `stdout` only if `verbose` is True')
        logger.info('I will log to `stdout` always')
        logger.warning('I will log to both `stdout` and `stderr` always')

*Disabled dual logging*

.. code-block:: python

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

*Custom formatter* [1]_

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

*Structured logging* [2]_

.. code-block:: python

    import pygogo as gogo

    formatter = gogo.formatters.structured_formatter
    kwargs = {'low_level': 'info', 'low_formatter': formatter}
    logger = gogo.Gogo('examples.structured', **kwargs).logger
    extra = {'set_value': set([1, 2, 3]), 'snowman': '☃'}
    logger.info('log message', extra=extra)  # doctest: +ELLIPSIS

    # Prints the following to `stdout`:

    {"snowman": "\u2603", "name": "examples.structured.base", "level": "INFO", "message": "log message", "time": "2015-12-18 18:52:39", "msecs": 58.973073959350586, "set_value": [1, 2, 3]}

*Using Filters to impart contextual information* [3]_

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
    2015-12-19 10:12:24,479 a.e.f INFO     IP: 192.168.0.1     User: sheila   AN INFO msg
    2015-12-19 10:12:24,479 a.e.f WARNING  IP: 192.168.0.1     User: sheila   A WARNING msg
    2015-12-19 10:12:24,479 a.e.f ERROR    IP: 192.168.0.1     User: sheila   AN ERROR msg
    2015-12-19 10:12:24,479 a.e.f CRITICAL IP: 192.168.0.1     User: sheila   A CRITICAL msg

    # Prints the following to `stderr` (messages at level `WARNING` or above):

    2015-12-19 10:12:24,479 a.e.f WARNING  IP: 192.168.0.1     User: sheila   A WARNING msg
    2015-12-19 10:12:24,479 a.e.f ERROR    IP: 192.168.0.1     User: sheila   AN ERROR msg
    2015-12-19 10:12:24,479 a.e.f CRITICAL IP: 192.168.0.1     User: sheila   A CRITICAL msg

*Multiple loggers* [4]_

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

Notes
^^^^^

.. [1] https://docs.python.org/2/howto/logging-cookbook.html#multiple-handlers-and-formatters
.. [2] https://docs.python.org/2/howto/logging-cookbook.html#implementing-structured-logging
.. [3] https://docs.python.org/2/howto/logging-cookbook.html#using-filters-to-impart-contextual-information
.. [4] https://docs.python.org/2/howto/logging-cookbook.html#logging-to-multiple-destinations

Command-line Interface
~~~~~~~~~~~~~~~~~~~~~~

Examples
^^^^^^^^

*Basic Usage*

.. code-block:: bash

    gogo [options] <message>

*show help*

.. code-block:: bash

    gogo -h

*CLI usage*

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

    # Prints the following to `stdout` (all messages at level `INFO` or below):

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

Installation
------------

(You are using a `virtualenv`_, right?)

At the command line, install pygogo using either ``pip`` (*recommended*)

.. code-block:: bash

    pip install pygogo

or ``easy_install``

.. code-block:: bash

    easy_install pygogo

Please see the `installation doc`_ for more details.

Project Structure
-----------------

.. code-block:: bash

    ┌── bin
    │   └── gogo
    ├── docs
    │   ├── AUTHORS.rst
    │   ├── CHANGES.rst
    │   ├── INSTALLATION.rst
    │   └── TODO.rst
    ├── helpers
    │   ├── check-stage
    │   ├── clean
    │   ├── pippy
    │   ├── srcdist
    │   └── wheel
    ├── pygogo
    │   ├── __init__.py
    │   ├── formatters.py
    │   ├── handlers.py
    │   ├── main.py
    │   └── utils.py
    ├── tests
    │   ├── __init__.py
    │   ├── standard.rc
    │   ├── test.py
    │   └── test_main.py
    ├── CONTRIBUTING.rst
    ├── LICENSE
    ├── MANIFEST.in
    ├── Makefile
    ├── README.rst
    ├── dev-requirements.txt
    ├── examples.py
    ├── manage.py
    ├── py2-requirements.txt
    ├── setup.cfg
    ├── setup.py
    └── tox.ini

Design Principles
-----------------

- the built-in ``logging`` module isn't broken so don't reinvent the wheel
- prefer functions over objects
- keep the API as simple as possible

Structured Logging
------------------

There are severals ways to get structured (machine readable) log messages using pygogo.
Each method makes a different customization/complexity trade-off which is
outlined below:

Setup
~~~~~

The following methods make use of these variables.

.. code-block:: python

    import pygogo as gogo

    kwargs = {'contextual': True}
    extra = {'additional': True}

Methods
~~~~~~~

basic structured logger
^^^^^^^^^^^^^^^^^^^^^^^

The simplest to use. Useful if you don’t need message metadata, i.e., log level,
log name, and log time.

.. code-block:: python

    logger = gogo.Gogo('basic').get_structured_logger('base', **kwargs)
    logger.debug('message', extra=extra)

    # Prints the following to `stdout`:

    {"additional": true, "contextual": true, "message": "message"}

structured formatter
^^^^^^^^^^^^^^^^^^^^

Requires an additional step of specifying a formatter. Useful if you need
message metadata, i.e., log level, log name, and log time.

.. code-block:: python

    formatter = gogo.formatters.structured_formatter
    logger = gogo.Gogo('struct', low_formatter=formatter).get_logger(**kwargs)
    logger.debug('message', extra=extra)

    # Prints the following to `stdout`:

     {"additional": true, "contextual": true, "level": "DEBUG", "message": "message", "msecs": 760.5140209197998, "name": "struct.base", "time": "2015-12-19 14:25:58"}

JSON formatter
^^^^^^^^^^^^^^

Requires an additional step of specifying a formatter. Useful if you require
millisecond precision in the date. If you are ok with having the milliseconds
in a separate field, consider the ``structured formatter`` since it supports
the ``extra`` keyword and contextual information.

.. code-block:: python

    formatter = gogo.formatters.json_formatter
    logger = gogo.Gogo('json', low_formatter=formatter).get_logger(**kwargs)
    logger.debug('message', extra=extra)

    # Prints the following to `stdout`:

    {"level": "DEBUG", "message": "message", "name": "json.base", "time": "2015-12-19 14:25:58.760"}

    # Note that both `extra` and `kwargs` were ignored

custom logger
^^^^^^^^^^^^^

The most complex and customizable. Useful if you need a custom
log or date format not provided by the above methods. However, even though this
method supports the ``extra`` keyword when logging, it is static (unlike the
``structured logger`` or ``structured formatter``). This is because the log
format must be specified at the time of the log's creation and therefore can't
adapt to log messages with differing ``extra`` parameters.

.. code-block:: python

    logfmt = (
        '{"time": "%(asctime)s.%(msecs)d", "name": "%(name)s", "level":'
        ' "%(levelname)s", "message": "%(message)s", '
        '"contextual": "%(contextual)s", "additional": "%(additional)s"}')

    fmtr = logging.Formatter(logfmt, datefmt=gogo.formatters.DATEFMT)
    logger = gogo.Gogo('custom', low_formatter=fmtr).get_logger(**kwargs)
    logger.debug('message', extra=extra)

    # Prints the following to `stdout`:

    {"additional": "True", "contextual": "True", "level": "DEBUG", "message": "message", "name": "custom.logger", "time": "2015-12-19 14:25:58.760"}

Summary
~~~~~~~

The following table can help make sense of the different methods:

+-------------------------------+-------------------+----------------------+----------------+---------------+
|                               | structured logger | structured formatter | json formatter | custom logger |
+===============================+===================+======================+================+===============+
| contextual information        | ✔                 | ✔                    |                | ✔             |
+-------------------------------+-------------------+----------------------+----------------+---------------+
| ``extra`` param support       | ✔                 | ✔                    |                | ✔             |
+-------------------------------+-------------------+----------------------+----------------+---------------+
| dynamic ``extra`` support     | ✔                 | ✔                    |                |               |
+-------------------------------+-------------------+----------------------+----------------+---------------+
| message metadata              |                   | ✔                    | ✔              | ✔             |
+-------------------------------+-------------------+----------------------+----------------+---------------+
| available via the command line|                   | ✔                    | ✔              |               |
+-------------------------------+-------------------+----------------------+----------------+---------------+
| ``msecs`` field               |                   | ✔                    |                |               |
+-------------------------------+-------------------+----------------------+----------------+---------------+
| milliseconds in time field    |                   |                      | ✔              | ✔             |
+-------------------------------+-------------------+----------------------+----------------+---------------+
| custom date format            |                   |                      |                | ✔             |
+-------------------------------+-------------------+----------------------+----------------+---------------+
| custom log format             |                   |                      |                | ✔             |
+-------------------------------+-------------------+----------------------+----------------+---------------+

Formatters
----------

pygogo has several builtin formatters and also supports any ``logging.Formatter``
instance.

Examples
~~~~~~~~

builtin CSV format in python
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    import pygogo as gogo

    formatter = gogo.formatters.csv_formatter
    gogo.Gogo('csv', low_formatter=formatter).logger.debug('message')

    # Prints the following to `stdout`:

    2015-12-19 17:03:48.99,csv.base,DEBUG,"message"


``logging.Formatter`` instance in python
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    import logging
    import pygogo as gogo

    datefmt = gogo.formatters.DATEFMT
    formatter = logging.Formatter(gogo.formatters.CSV_FORMAT, datefmt=datefmt)
    gogo.Gogo('csv', low_format=formatter).get_logger('custom').debug('message')

    # Prints the following to `stdout`:

    2015-12-19 17:03:48.99,csv.custom,DEBUG,"message"

builtin CSV format via CLI
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    gogo --low-format=csv 'message'

    # Prints the following to `stdout`:

    2015-12-19 15:51:32.16,pygogo.runner,INFO,"message"

Summary
~~~~~~~

The following table can help make sense of the different builtin formatters:

+------------+------------------------------------------------------------------------------------------------------------------+
| name       | message                                                                                                          |
+============+==================================================================================================================+
| basic      | message                                                                                                          |
+------------+------------------------------------------------------------------------------------------------------------------+
| bom        | message                                                                                                          |
+------------+------------------------------------------------------------------------------------------------------------------+
| console    | name: INFO     message                                                                                           |
+------------+------------------------------------------------------------------------------------------------------------------+
| csv        | 2015-12-19 15:51:32.16,name,INFO,"message"                                                                       |
+------------+------------------------------------------------------------------------------------------------------------------+
| fixed      | 2015-12-19 15:51:32.16 name INFO     message                                                                     |
+------------+------------------------------------------------------------------------------------------------------------------+
| json       | {"level": "INFO", "message": "message", "name": "name", "time": "2015-12-19 15:51:32.16"}                        |
+------------+------------------------------------------------------------------------------------------------------------------+
| structured | {"level": "INFO", "message": "message", "msecs": 16.5140209197998, "name": "name", "time": "2015-12-19 15:51:32"}|
+------------+------------------------------------------------------------------------------------------------------------------+

Handlers
--------

pygogo has several builtin handlers and also supports any instance from the
``logging.handlers`` module.

Examples
~~~~~~~~

builtin stdout handler in python
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    import pygogo as gogo

    hdlr = gogo.handlers.stdout_hdlr()
    gogo.Gogo('stdout', low_hdlr=hdlr).logger.debug('message')

    # Prints 'message' to `stdout`

``logging.StreamHandler`` instance in python
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    import logging
    import sys
    import pygogo as gogo

    hdlr = logging.StreamHandler(sys.stdout)
    gogo.Gogo('stdout', low_hdlr=hdlr).get_logger('custom').debug('message')

    # Prints 'message' to `stdout`

builtin CSV format via CLI
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    gogo --low-hdlr=stdout 'message'

    # Prints 'message' to `stdout`

Summary
~~~~~~~

The following table can help make sense of the different builtin handlers:

+------------+------------------------------------------+
| name       | description                              |
+============+==========================================+
| buffered   | Holds log in memory until it reaches its |
|            | capacity, or it logs a message with a    |
|            | level at or above the flush level        |
+------------+------------------------------------------+
| email      | Emails log to a given email address      |
+------------+------------------------------------------+
| file       | Writes log to a given filename           |
+------------+------------------------------------------+
| fileobj    | Writes log to a given file-like object   |
+------------+------------------------------------------+
| socket     | Writes log to a given network socket     |
+------------+------------------------------------------+
| stderr     | Writes log to standard error             |
+------------+------------------------------------------+
| stdout     | Writes log to standard output            |
+------------+------------------------------------------+
| syslog     | Writes log to syslog                     |
+------------+------------------------------------------+
| webhook    | POSTs log to a url                       |
+------------+------------------------------------------+

Scripts
-------

pygogo comes with a built in task manager ``manage.py``

Setup
~~~~~

.. code-block:: bash

    pip install -r dev-requirements.txt

Examples
~~~~~~~~

*Run python linter and nose tests*

.. code-block:: bash

    manage lint
    manage test

Contributing
------------

Please mimic the coding style/conventions used in this repo.
If you add new classes or functions, please add the appropriate doc blocks with
examples. Also, make sure the python linter and nose tests pass.

Please see the `contributing doc`_ for more details.

License
-------

pygogo is distributed under the `MIT License`_.

.. |travis| image:: https://img.shields.io/travis/reubano/pygogo/master.svg
    :target: https://travis-ci.org/reubano/pygogo

.. |versions| image:: https://img.shields.io/pypi/pyversions/pygogo.svg
    :target: https://pypi.python.org/pypi/pygogo

.. |pypi| image:: https://img.shields.io/pypi/v/pygogo.svg
    :target: https://pypi.python.org/pypi/pygogo

.. _MIT License: http://opensource.org/licenses/MIT
.. _logging module: https://docs.python.org/2/library/logging.html
.. _virtualenv: http://www.virtualenv.org/en/latest/index.html
.. _contributing doc: https://github.com/reubano/pygogo/blob/master/CONTRIBUTING.rst
.. _installation doc: https://github.com/reubano/pygogo/blob/master/docs/INSTALLATION.rst
