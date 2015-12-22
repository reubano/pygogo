Installation
------------

(You are using a `virtualenv`_ [#]_, right?)

At the command line, install pygogo using either pip (recommended)

.. code-block:: bash

    pip install pypygogo

or easy_install

.. code-block:: bash

    easy_install pygogo


.. [#] If you have ``virtualenvwrapper`` installed, at the command line type:

.. code-block:: bash

    mkvirtualenv pygogo
    pip install pygogo

Or, if you only have ``virtualenv`` installed:

.. code-block:: bash

	virtualenv ~/.venvs/pygogo
	source ~/.venvs/pygogo/bin/activate
	pip install pygogo

Otherwise, you can install globally::

    pip install pygogo

.. _virtualenv: http://www.virtualenv.org/en/latest/index.html
