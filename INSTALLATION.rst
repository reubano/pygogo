Installation
------------

(You are using a `virtualenv`_, right?)

At the command line, install bump using either ``pip`` (recommended)

.. code-block:: bash

    pip install bump

or ``easy_install``

.. code-block:: bash

    easy_install bump

Detailed installation instructions
----------------------------------

If you have `virtualenvwrapper`_ installed, at the command line type:

.. code-block:: bash

    mkvirtualenv bump
    pip install bump

Or, if you only have ``virtualenv`` installed:

.. code-block:: bash

	virtualenv ~/.venvs/bump
	source ~/.venvs/bump/bin/activate
	pip install bump

Otherwise, you can install globally::

    pip install bump

.. _virtualenv: https://virtualenv.pypa.io/en/latest/index.html
.. _virtualenvwrapper: https://virtualenvwrapper.readthedocs.org/en/latest/
