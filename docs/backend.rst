Backend
=======

The backend itself consists of two major components: a login server and the API server. The login
server is a `Flask`_ application which handles authentication for the user, generating tokens for
the browser's use when it hits API endpoints. The API server is a `Klein`_ application.

Prerequisites
^^^^^^^^^^^^^

The Python-based backend has a few basic prerequisites:

-  A compatible operating system (we develop on OS X and deploy on Ubuntu)
-  CPython 2.7+ or CPython 3.3+ (we develop and deploy with 2.7 but test against 3.3+)
-  `FreeTDS`_ (if using the LANDESK plugin)
-  ``libffi`` (Install with `Homebrew`_ on Mac with ``brew install libffi``)

Installation
^^^^^^^^^^^^

We recommend using a Python `virtualenv`_. Once you've set up an environment for Stethoscope, you
can install the backend and the bundled plugins easily using our :file:`Makefile`:

.. code:: sh

    make develop

LANDESK Plugin
''''''''''''''

The LANDESK plugin has `pymssql`_ as a dependency, which in turn requires `FreeTDS`_. On OS X,
`FreeTDS`_ can be installed via `Homebrew`_:

.. code:: sh

    brew install freetds

Troubleshooting
'''''''''''''''

Python 2.7.6 and ``pyenv``
++++++++++++++++++++++++++

If installing on OSX 10.10+ for Python 2.7.6 or 2.7.7 using `pyenv`_, you may encounter an error
(``ld: file not found: python.exe``; see `this issue <https://github.com/yyuu/pyenv/issues/273>`__)
while installing `Twisted`_. The workaround is to build a wheel for `Twisted`_ under 2.7.8, then
install the wheel into the 2.7.6 environment:

.. code:: sh

    pyenv install 2.7.6
    pyenv virtualenv 2.7.6 stethoscope
    pyenv install 2.7.8
    pyenv shell 2.7.8
    pip wheel --wheel-dir=$TMPDIR/wheelhouse Twisted
    pyenv shell stethoscope
    pip install --no-index --find-links=$TMPDIR/wheelhouse Twisted


Errors installing ``pymssql``
+++++++++++++++++++++++++++++

If you encounter a compilation error installing `pymssql`_, you may need to revert to an older
version of `FreeTDS`_ via:

.. code:: sh

    brew unlink freetds
    brew install homebrew/versions/freetds091
    pip install pymssql


Configuration
^^^^^^^^^^^^^

Configuration for the login and API servers is separate, but share the same pattern (a series of
``.py`` files loaded via `Flask`_'s configuration mechanism). In order (last file taking
precedence), the configurations are loaded from:

#. The ``defaults.py`` file from the package's directory (e.g.,
   :file:`stethoscope/login/defaults.py`).
#. An 'instance' ``config.py`` file (in the `Flask`_ :file:`instance` subdirectory, which can be
   changed using :envvar:`STETHOSCOPE_API_INSTANCE_PATH` and
   :envvar:`STETHOSCOPE_LOGIN_INSTANCE_PATH`).
#. A file specified by the :envvar:`STETHOSCOPE_API_CONFIG` or :envvar:`STETHOSCOPE_LOGIN_CONFIG`
   environment variables. Examples of these are in the :file:`config/login` and :file:`config/api`
   subdirectories.

The minimum configuration file needs define only two variables: ``SECRET_KEY`` and
``JWT_SECRET_KEY`` (see the included :file:`instance/config.py` file for details).

Testing
^^^^^^^

The basic tests can be run via the ``Makefile``:

.. code:: sh

    make test

Alternatively, to test against multiple versions of Python, first
install `tox`_, then run:

.. code:: sh

    make tox

Running
^^^^^^^

The backend has two processes which generally need to be running simultaneously: the login server
and the API server.

Login
'''''

.. code:: sh

    stethoscope-login runserver -p 5002

API
'''

.. code:: sh

    twistd -n web -p 5001 --class=stethoscope.api.resource.resource


.. _Flask: http://flask.pocoo.org
.. _Klein: https://github.com/twisted/klein
.. _Twisted: https://twistedmatrix.com
.. _FreeTDS: http://www.freetds.org
.. _Homebrew: https://brew.sh
.. _virtualenv: https://virtualenv.pypa.io
.. _Nginx: https://www.nginx.com/
.. _pymssql: http://pymssql.org
.. _pyenv: https://github.com/yyuu/pyenv
.. _tox: https://tox.readthedocs.io/
