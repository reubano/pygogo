pygogo |travis| |version| |pypi|
===============================


.. |travis| image:: https://secure.travis-ci.org/reubano/pygogo.png?branch=master
    :target: https://travis-ci.org/reubano/pygogo

.. |version| image:: https://badge.fury.io/py/pygogo.png
    :target: http://badge.fury.io/py/pygogo

.. |pypi| image:: https://pypip.in/d/pygogo/badge.png
    :target: https://pypi.python.org/pypi/pygogo

Introduction
------------

`pygogo <https://github.com/reubano/pygogo>`_ is a Python logging library with super powers.

With ckanutils, you can

- Download a CKAN resource
- Upload CSV/XLS/XLSX files into a CKAN DataStore
- and much more...

Requirements
------------

ckanutils has been tested on the following configuration:

- MacOS X 10.9.5
- Python 2.7.9

pygogo requires the following in order to run properly:

* `Python >= 2.7 <http://www.python.org/download>`_

Installation
------------

(You are using a `virtualenv <http://www.virtualenv.org/en/latest/index.html>`, right?)

Install pygogo using either pip (recommended)

    sudo pip install pypygogo

or easy_install

    sudo easy_install pygogo


Using pygogo
-----------

ckanutils is intended to be used either directly from Python as a library or from the command line.

Usage
^^^^^

    pygogo [options] <argument>

Examples
^^^^^^^^

*show help*

    pygogo -h

Options
^^^^^^^

      -h, --help            show this help message and exit

Arguments
^^^^^^^^^

========= ===========
argument  description
========= ===========

Features
--------

* TODO

==============  ==========================================================
Python support  Python 2.7, >= 3.3
Source          https://github.com/reubano/pygogo
Docs            http://pygogo.rtfd.org
Changelog       http://pygogo.readthedocs.org/en/latest/changes.html
Issues          https://github.com/reubano/pygogo/issues
Travis          http://travis-ci.org/reubano/pygogo
pypi            https://pypi.python.org/pypi/pygogo
git repo        .. code-block:: bash

                    git clone https://github.com/reubano/pygogo.git
install dev     .. code-block:: bash

                    git clone https://github.com/reubano/pygogo.git pygogo
                    cd ./pygogo
                    virtualenv .env
                    source .env/bin/activate
                    pip install -e .
tests           .. code-block:: bash

                    python setup.py test
==============  ==========================================================

.. _Documentation: http://pygogo.readthedocs.org/en/latest/
`Docs <http://pygogo.rtfd.org>`_
`Changelog <http://pygogo.readthedocs.org/en/latest/changes.html>`_

Preparation
-----------

Check that the correct version of Python is installed

	python -V

LICENSE
-------

pygogo is distributed under the `MIT License <http://opensource.org/licenses/MIT>`_.
