Introduction
------------

pygogo is a Python logging library_ and command-line interface_ with super powers.
pygogo leverages the standard Python `logging module`_ under the hood, so there's
no need to learn yet-another logging library. The default implementation sends
all messages to ``stdout``, and any messages at level ``WARNING`` or above to ``stderr``.

With pygogo, you can

- Log via different handlers depending on the event severity
- Format log messages as plain text, csv, json, and more..
- Send logs to stdout, stderr, file, email, sockets, and more..
- Inter-operate with the standard python logging module
- and much more...

Motivation
----------

The standard logging module is great, but requires a ton of boilerplate before
you can do anything really interesting with it. pygogo provides many of these
useful logging use-cases out of the box. A reimplementation of
`Using LoggerAdapters to impart contextual information`_ is shown below:

.. code-block:: python

    import pygogo as gogo

    logger = gogo.Gogo(__name__).get_structured_logger(connid='1234')
    logger.info('log message')

    # Prints the following to stdout

    {"message": "log message", "connid": "1234"}

.. _library: usage.html#library-examples
.. _interface: usage.html#cli-examples
.. _logging module: https://docs.python.org/2/library/logging.html
.. _Using LoggerAdapters to impart contextual information: https://docs.python.org/2/howto/logging-cookbook.html#using-loggeradapters-to-impart-contextual-information
