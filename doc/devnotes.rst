Developer notes
===============

Build dependencies
------------------

Most dependencies from :doc:`install-quick`, plus (for Python):

- `GNU make <http://www.gnu.org/software/make/>`_
- `GNU tar <http://www.gnu.org/software/tar/>`_
- `Gzip <http://www.gnu.org/software/gzip/>`_
- `pandoc <http://johnmacfarlane.net/pandoc/>`_
- `python-sphinx <http://sphinx.pocoo.org/>`_
  (tested with version 0.6.1)
- `graphviz <http://www.graphviz.org/>`_
- the `en_US.UTF-8` locale must be enabled on the system
- `pylint <http://www.logilab.org/857>`_ and its associated
  dependencies

Note that for pylint, at the current moment the following versions
need to be used::

    $ pylint --version
    pylint 0.21.1,
    astng 0.20.1, common 0.50.3

To generate unittest coverage reports (``make coverage``), `coverage
<http://pypi.python.org/pypi/coverage>`_ needs to be installed.

For Haskell development, again all things from the quick install
document, plus:

- `haddock <http://www.haskell.org/haddock/>`_, documentation
  generator (equivalent to epydoc for Python)
- `HsColour <http://hackage.haskell.org/package/hscolour>`_, again
  used for documentation (it's source-code pretty-printing)
- `hlint <http://community.haskell.org/~ndm/hlint/>`_, a source code
  linter (equivalent to pylint for Python)
- the `QuickCheck <http://hackage.haskell.org/package/QuickCheck>`_
  library, version 2.x
- ``hpc``, which comes with the compiler, so you should already have
  it

Under Debian, these can be installed (on top of the required ones from
the quick install document) via::

  apt-get install libghc6-quickcheck1-dev hscolour hlint


Configuring for development
---------------------------

.. highlight:: sh

Run the following command (only use ``PYTHON=...`` if you need to use a
different python version)::

  ./autogen.sh && \
  ./configure --prefix=/usr/local --sysconfdir=/etc --localstatedir=/var


Packaging notes
===============

Ganeti is mostly developped and tested on `Debian
<http://www.debian.org/>`_-based distributions, while still keeping
adoptability to other Linux distributions in mind.

The ``doc/examples/`` directory contains a number of potentially useful
scripts and configuration files. Some of them might need adjustment
before use.

``daemon-util``
---------------

This script, in the source code as ``daemons/daemon-util.in``, is used
to start/stop Ganeti and do a few other things related to system
daemons. It is recommended to use ``daemon-util`` also from the system's
init scripts. That way the code starting and stopping daemons is shared
and future changes have to be made in only one place.

``daemon-util`` reads extra arguments from variables (``*_ARGS``) in
``/etc/default/ganeti``. When modifying ``daemon-util``, keep in mind to
not remove support for the ``EXTRA_*_ARGS`` variables for starting
daemons. Some parts of Ganeti use them to pass additional arguments when
starting a daemon.

The ``reload_ssh_keys`` function can be adjusted to use another command
for reloading the OpenSSH daemon's host keys.

.. vim: set textwidth=72 :
