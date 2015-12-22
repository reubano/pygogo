pygogo: a Python logger with super powers
=========================================

|versions| |pypi|

.. image:: https://raw.githubusercontent.com/reubano/pygogo/master/pygogo.png
    :alt: sample pygogo usage
    :width: 800
    :align: center

.. include:: INTRO.rst
    :end-line: 38

.. include:: USAGE.rst

.. include:: INSTALLATION.rst

Project structure
-----------------

.. code-block:: bash

    ├── AUTHORS.rst
    ├── CHANGES.rst
    ├── CONTRIBUTING.rst
    ├── LICENSE
    ├── MANIFEST.in
    ├── Makefile
    ├── pygogo.png
    ├── README.rst
    ├── TODO.rst
    ├── bin
    │   └── gogo
    ├── dev-requirements.txt
    ├── examples.py
    ├── helpers
    │   ├── check-stage
    │   ├── clean
    │   ├── docs
    │   ├── sdist
    │   ├── srcdist
    │   ├── test
    │   └── wheel
    ├── manage.py
    ├── pygogo
    │   ├── __init__.py
    │   ├── formatters.py
    │   ├── handlers.py
    │   ├── main.py
    │   └── utils.py
    ├── requirements.txt
    ├── setup.cfg
    ├── setup.py
    ├── tests
    │   ├── __init__.py
    │   ├── standard.rc
    │   ├── test.py
    │   └── test_main.py
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

    kwargs = {'contextual': True}
    extra = {'additional': True}

Methods
~~~~~~~

basic structured logger
^^^^^^^^^^^^^^^^^^^^^^^

The simplest to use. Useful if you don’t need message metadata, i.e., log level,
log name, and log time.

.. code-block:: python

    logger = gogo.Gogo().get_structured_logger('base', **kwargs)
    logger.debug('message', extra=extra)

    # Prints the following to `stdout`:

    {"additional": true, "contextual": true, "message": "message"}

structured formatter
^^^^^^^^^^^^^^^^^^^^

Requires an additional step of specifying a formatter. Useful if you need
message metadata, i.e., log level, log name, and log time.

.. code-block:: python

    formatter = gogo.formatters.structured_formatter
    logger = gogo.Gogo('struct', low_formatter=formatter).logger
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
    logger = gogo.Gogo('json', low_formatter=formatter).logger
    logger.debug('message', extra=extra)

    # Prints the following to `stdout`:

    {"level": "DEBUG", "message": "message", "name": "json.base", "time": "2015-12-19 14:25:58.760"}

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

+----------------------------+-------------------+----------------------+----------------+---------------+
|                            | structured logger | structured formatter | json formatter | custom logger |
+============================+===================+======================+================+===============+
| contextual information     | ✔                 | ✔                    |                | ✔             |
+----------------------------+-------------------+----------------------+----------------+---------------+
| ``extra`` param support    | ✔                 | ✔                    |                | ✔             |
+----------------------------+-------------------+----------------------+----------------+---------------+
| dynamic ``extra`` support  | ✔                 | ✔                    |                |               |
+----------------------------+-------------------+----------------------+----------------+---------------+
| message metadata           |                   | ✔                    | ✔              | ✔             |
+----------------------------+-------------------+----------------------+----------------+---------------+
| available via the cli      |                   | ✔                    | ✔              |               |
+----------------------------+-------------------+----------------------+----------------+---------------+
| ``msecs`` field            |                   | ✔                    |                |               |
+----------------------------+-------------------+----------------------+----------------+---------------+
| milliseconds in time field |                   |                      | ✔              | ✔             |
+----------------------------+-------------------+----------------------+----------------+---------------+
| custom date format         |                   |                      |                | ✔             |
+----------------------------+-------------------+----------------------+----------------+---------------+
| custom log format          |                   |                      |                | ✔             |
+----------------------------+-------------------+----------------------+----------------+---------------+

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

License
-------

pygogo is distributed under the `MIT License`_.

.. _MIT License: http://opensource.org/licenses/MIT

Contributing
------------

Please mimic the coding style/conventions used in this repo.
If you add new classes or functions, please add the appropriate doc blocks with
examples. Also, make sure the python linter and nose tests pass.

Please see the `contributing doc`_ for more details.

.. |versions| image:: https://img.shields.io/pypi/pyversions/pygogo.svg
    :target: https://pypi.python.org/pypi/pygogo

.. |pypi| image:: https://img.shields.io/pypi/v/pygogo.svg
    :target: https://pypi.python.org/pypi/pygogo

.. _contributing doc: https://github.com/reubano/pygogo/master/CONTRIBUTING.png
