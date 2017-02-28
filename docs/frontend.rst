Frontend
========

You can run (and develop) the frontend code without running the backend services at all, and rely on
the example data files in :file:`stethoscope/ui/public/api`. We use Facebook's `create-react-app`_
scripts for easy, zero-configuration development, testing, and building.

If you would like to develop against real data, you can run the backend
(locally or in Docker) and proxy API requests to the backend. This is
handled automatically by
`create-react-app`_,
and you can change the proxy address in ``stethoscope/ui/package.json``.

**Note:** For API authentication to work with the proxy, you'll need to
generate a token that will be loaded into your development environment.
If you have installed the Python dependencies, you can do this with
``make dev-token``. If you have `Docker <https://www.docker.com/>`__
installed, you can do this with ``make dev-token-docker``.

Prerequisites
^^^^^^^^^^^^^

To run the frontend directly, without Docker, you'll need recent
versions of `node <https://nodejs.org/>`__ (version 6.4+) and npm
(included with node).

Installation
^^^^^^^^^^^^

From the project root, run ``make install-develop-ui``. This will
install the npm packages, start a development server, and load the site
in your default browser.

Running
^^^^^^^

After your node dependencies are installed, you can run the development
server with ``make develop-ui``. (This is equivalent to running
``cd stethoscope/ui && npm start``.)

Configuration
^^^^^^^^^^^^^

The frontend can be customized by adding to
``stethoscope/ui/config.json``. These settings are applied after loading
``stethoscope/ui/config.defaults.json``, so you can reference that file
for the defaults. You can customize things like the application name,
the name of your organization, and your contact email address without
changing any of the javascript source files.

Testing
^^^^^^^

`create-react-app`_
includes a script that will automatically watch for changes and rerun
relevant tests. You can run this with ``make test-js-watch``. (This is
equivalent to running ``cd stethoscope/ui && npm test``.)

If you'd like to run all tests and exit, run ``make test-js``.

Building
^^^^^^^^

To build the static assets, you can run ``make react-build``. (This is
equivalent to running ``cd stethoscope/ui && npm build``.)

This is only necessary if you want to build new static assets for a
local Python backend, or if you want to check the gzipped file size of
the generated js and css resources. These build files are not checked in
to the project.

If you would like to build these resources without a local node
development environment, you can run ``make docker-build-ui`` to
generate the files using Docker. (This happens automatically when you
run ``docker-compose up``.)

.. _create-react-app: https://github.com/facebookincubator/create-react-app
