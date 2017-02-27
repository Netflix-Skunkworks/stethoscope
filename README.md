# Stethoscope: User-Focused Security

![Giraffe logo](stethoscope/ui/public/static/images/giraffe-small.png)

Stethoscope is a web application that collects information from existing device data sources (e.g.,
JAMF or LANDESK) on a given user’s devices and gives them clear and specific recommendations for
securing their systems. An overview is available on the [Netflix Tech
Blog](http://techblog.netflix.com/).

[![Join the chat at https://gitter.im/Netflix-Stethoscope/Lobby](https://badges.gitter.im/Netflix-Stethoscope/Lobby.svg)](https://gitter.im/Netflix-Stethoscope/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![Apache 2.0](https://img.shields.io/github/license/Netflix/stethoscope.svg)](http://www.apache.org/licenses/LICENSE-2.0)
[![NetflixOSS Lifecycle](https://img.shields.io/osslifecycle/Netflix/stethoscope.svg)]()
[![Build Status](https://travis-ci.org/Netflix/stethoscope.svg?branch=master)](https://travis-ci.org/Netflix/stethoscope)

![Stethoscope screenshot](docs/screenshot.png)

## Quickstart

If you have node and npm already and just want to play around with the front end, run:

`make install-develop-ui`


## What is Stethoscope?

### Main Features

- Retrieves device information from:
  - JAMF
  - LANDESK
  - G Suite (Google) Mobile Management
  - bitFit
- Evaluates status of various security practices, including:
  - Disk encryption
  - Firewall
  - Screen saver lock/password
  - Operating system up-to-date
  - Operating system auto-update
  - Not jailbroken/rooted
  - Software presence (e.g., for monitoring tools)
- Merges associated device records
- Plugin architecture:
  - Easy to add data sources, practices, and other components
  - Examples and base plugins for communicating with Elasticsearch and HTTP REST APIs

## Getting Started

Stethoscope consists of two primary pieces: a Python-based back-end and a React-based front-end.
Nginx is used to serve static files and route traffic to the back-end.

The easiest way to get up-and-running quickly is through the provided Docker configuration.

### Docker

To run with [Docker](https://www.docker.com/), first install Docker
([standard](https://docs.docker.com/mac/) or [beta](https://beta.docker.com/)).

We have provided a [Docker Compose](https://docs.docker.com/compose/) file, `docker-compose.yml`,
that defines the services that make up Stethoscope. To start these services, run:

```sh
docker-compose up
```

Then connect to the main Nginx web server at `http://localhost:5000`.

#### Troubleshooting

If you encounter the following error, you likely need to upgrade `docker-compose` to version 1.10 or
higher.

> ERROR: In file './docker-compose.yml' service 'version' doesn't have any configuration options.
> All top level keys in your docker-compose.yml must map to a dictionary of configuration options.

### Front end

You can run (and develop) the front end code without running the backend services at all, and rely on the example data files in `stethoscope/ui/public/api`. We use Facebook's [create-react-app] scripts for easy, zero-configuration development, testing, and building.

If you would like to develop against real data, you can run the backend (locally or in Docker) and proxy API requests to the backend. This is handled automatically by [create-react-app], and you can change the proxy address in `stethoscope/ui/package.json`.

**Note:** For API authentication to work with the proxy, you'll need to generate a token that will be loaded into your development environment. If you have installed the Python dependencies, you can do this with `make dev-token`. If you have [Docker] installed, you can do this with `make dev-token-docker`.


#### Prerequisites

To run the front end directly, without Docker, you'll need recent versions of [node] and [npm].

#### Installation

From the project root, run `make install-develop-ui`. This will install the npm packages, start a development server, and load the site in your default browser.

#### Running

After your node dependencies are installed, you can run the development server with `make develop-ui`. (This is equivalent to running `cd stethoscope/ui && npm start`.)

#### Configuration

The front end can be customized by adding to `stethoscope/ui/config.json`. These settings are applied after loading `stethoscope/ui/config.defaults.json`, so you can reference that file for the defaults. You can customize things like the application name, the name of your organization, and your contact email address without changing any of the javascript source files.

#### Testing

[create-react-app] includes a script that will automatically watch for changes and rerun relevant tests. You can run this with `make test-js-watch`. (This is equivalent to running `cd stethoscope/ui && npm test`.)

If you'd like to run all tests and exit, run `make test-js`.

#### Building

To build the static assets, you can run `make react-build`. (This is equivalent to running `cd stethoscope/ui && npm build`.)

This is only necessary if you want to build new static assets for a local Python backend, or if you want to check the gzipped file size of the generated js and css resources. These build files are not checked in to the project.

If you would like to build these resources without a local node development environment, you can run `make docker-build-ui` to generate the files using Docker. (This happens automatically when you run `docker-compose up`.)

### Back-end

The back-end itself consists of two major components: a login server and the API server. The login
server is a [Flask] application which handles authentication for the user, generating tokens for the
browser's use when it hits API endpoints. The API server is a [Klein] application.

#### Prerequisites

The Python-based back-end has a few basic prerequisites:

- A compatible operating system (we develop on OS X and deploy on Ubuntu)
- CPython 2.7+ or CPython 3.3+ (we develop and deploy with 2.7 but test against 3.3+)
- [FreeTDS][] (if using the LANDESK plugin)
- libffi (Install with [Homebrew] on Mac with `brew install libffi`)

#### Installation

We recommend using a Python [virtualenv]. Once you've set up an environment for Stethoscope, you can
install the back-end and the bundled plugins easily using our `Makefile`:

```sh
make develop
```

##### LANDESK Plugin

The LANDESK plugin has [pymssql](http://pymssql.org) as a dependency, which in turn requires
[FreeTDS]. On OS X, [FreeTDS] can be installed via [Homebrew]:

```sh
brew install freetds
```

##### Troubleshooting

###### Python 2.7.6 and `pyenv`

If installing on OSX 10.10+ for Python 2.7.6 or 2.7.7 using [pyenv], you may encounter an
error (`ld: file not found: python.exe`; see [this issue](https://github.com/yyuu/pyenv/issues/273))
while installing [Twisted]. The workaround is to build a wheel for [Twisted] under 2.7.8, then
install the wheel into the 2.7.6 environment:

```sh
pyenv install 2.7.6
pyenv virtualenv 2.7.6 stethoscope
pyenv install 2.7.8
pyenv shell 2.7.8
pip wheel --wheel-dir=$TMPDIR/wheelhouse Twisted
pyenv shell stethoscope
pip install --no-index --find-links=$TMPDIR/wheelhouse Twisted
```

###### Errors installing `pymssql`

If you encounter a compilation error installing [pymssql], you may need to revert to an older
version of [FreeTDS] via:

```sh
brew unlink freetds
brew install homebrew/versions/freetds091
pip install pymssql
```

#### Configuration

Configuration for the login and API servers is separate, but share the same pattern (a series of
`.py` files loaded via [Flask]'s configuration mechanism). In order (last file taking precedence),
the configurations are loaded from:

1. The `defaults.py` file from the package's directory (e.g., `stethoscope/login/defaults.py`).
2. An 'instance' `config.py` file (in the [Flask] `instance` subdirectory, which can be changed
   using `STETHOSCOPE_API_INSTANCE_PATH` and `STETHOSCOPE_LOGIN_INSTANCE_PATH`).
3. A file specified by the `STETHOSCOPE_API_CONFIG` or `STETHOSCOPE_LOGIN_CONFIG` environment
   variables. Examples of these are in the `config/login` and `config/api` subdirectories.

The minimum configuration file needs define only two variables: `SECRET_KEY` and `JWT_SECRET_KEY`
(see the included `instance/config.py` file for details).

#### Testing

The basic tests can be run via the `Makefile`:

```sh
make test
```

Alternatively, to test against multiple versions of Python, first install [tox], then run:

```sh
make tox
```

#### Running

The back-end has two processes which generally need to be running simultaneously: the login server
and the API server.

##### Login

```sh
stethoscope-login runserver -p 5002
```

##### API

```sh
twistd -n web -p 5001 --class=stethoscope.api.resource.resource
```

### Nginx

#### Configuration

For `nginx`, the supplied `nginx.conf` sets up the appropriate configuration for running locally out
of the repository directory. Essentially, requests for static files are handled by `nginx`, requests
for non-API endpoints are proxied to port 5002 (to be handled by the login server), and requests for
API endpoints are proxied to port 5001 (to be handled by the API server).


#### Running

```sh
nginx -c nginx.conf -p $(pwd)
```

## Plugins

Plugins provide much of the functionality of Stethoscope and make it easy to add new functionality
for your environment and to pick-and-choose what data sources, outputs, etc. make sense for your
organization.

Configuration for each plugin is provided in your `instance/config.py` file by defining a top-level
`PLUGINS` dictionary. Each key in the dictionary must be the name of a plugin (as given in
`setup.py`, e.g., `es_notifications`) and the corresponding value must itself be a dictionary with
keys and values as described in the sections below for each individual plugin. For example, your
`config.py` might contain:

```py
PLUGINS = {
  'bitfit': {
    'BITFIT_API_TOKEN': 'super secret API token',
    'BITFIT_BASE_URL': 'https://api.bitfit.com/',
  },
}
```

The above example configures only the `bitfit` plugin.

##### Timeouts

Many plugins involve communicating with external servers. Each of these respects an optional
`TIMEOUT` configuration variable which controls the timeout for these external connections. If not
set for a particular plugin, the top-level configuration variable `DEFAULT_TIMEOUT` is used. If this
is not set, no timeout will be enforced.

### Data Sources

#### Google

Google provides:

- Detailed device information on ChromeOS, Android and iOS devices via their mobile management
  services.
- Account information.
<!-- - Authentication logs. -->

##### Configuration

- `GOOGLE_API_SECRETS`: JSON blob containing service account credentials.
- `GOOGLE_API_USERNAME`: Service account name.
- `GOOGLE_API_SCOPES`: List of scopes required (depends on what information you're using from
  Google). We use:

    ```py
    [
      "https://www.googleapis.com/auth/admin.directory.device.chromeos.readonly",
      "https://www.googleapis.com/auth/admin.directory.device.mobile.readonly",
      "https://www.googleapis.com/auth/admin.directory.user.readonly",
      "https://www.googleapis.com/auth/admin.reports.audit.readonly",
      "https://www.googleapis.com/auth/admin.reports.usage.readonly",
    ]
    ```

#### JAMF

JAMF provides detailed device information on OS X systems.

##### Configuration

The JAMF plugin requires the following configuration variables:

- `JAMF_API_USERNAME`: Username for interacting with JAMF's API.
- `JAMF_API_PASSWORD`: Password for interacting with JAMF's API.
- `JAMF_API_HOSTADDR`: JAMF API URL (e.g., `https://example.jamfcloud.com/JSSResource`).

##### Extension Attributes

JAMF does not provide enough information out-of-the-box for us to determine the status of all the
desired security practices. However, we can define Extension Attributes in JAMF to gather the needed
information.

#### LANDESK

LANDESK provides detailed device information for Windows systems.

##### Configuration

Our LANDESK plugin communicates directly with the LANDESK SQL server. It requires the
following configuration variables:

- `LANDESK_SQL_HOSTNAME`
- `LANDESK_SQL_HOSTPORT`
- `LANDESK_SQL_USERNAME`
- `LANDESK_SQL_PASSWORD`
- `LANDESK_SQL_DATABASE`

#### bitFit

bitFit provides ownership attribution for devices.

##### Configuration

- `BITFIT_API_TOKEN`: API token from bitFit.
- `BITFIT_BASE_URL`: URL for bitFit's API (e.g., `https://api.bitfit.com/`).

#### Duo

Duo provides authentication logs.

##### Work in Progress

The `duo` plugin currently suffers from a major issue which makes it unsuitable for production use
at this time. In particular, Duo's API does not provide a method for retrieving only a single user's
authentication logs *and* the frequency of API requests allowed by Duo's API is severely limited.
Therefore, some method of caching authentication logs or storing them externally is required.
However, this has not yet been implemented in Stethoscope.

##### Configuration

The `duo` plugin requires the following:

- `DUO_INTEGRATION_KEY`: The integration key from Duo.
- `DUO_SECRET_KEY`: The secret key for the integration from Duo.
- `DUO_API_HOSTNAME`: The hostname for your Duo API server (e.g., `api-xxxxxx.duosecurity.com`).

Values for the above can be found using [these
instructions](https://duo.com/docs/adminapi#first-steps).

### Notifications and Feedback

Stethoscope's UI provides a place for users to view and respond to alerts or notifications. Plugins
provide the mechanisms to both retrieve notifications from and write feedback to external data
sources.

#### Notifications from Elasticsearch

The `es_notifications` plugin reads notifications (or alerts) for the user from an Elasticsearch
cluster so they can be formatted and displayed in the Stethoscope UI.

##### Configuration

As with our other Elasticsearch-based plugins, the `es_notifications` plugin requires the following
configuration variables:

- `ELASTICSEARCH_HOSTS`: List of host specifiers for the Elasticsearch cluster (e.g.,
  `["http://es.example.com:7104"]`)
- `ELASTICSEARCH_INDEX`: Name of the index to query.
- `ELASTICSEARCH_DOCTYPE`: Name of the document type to query.

#### Feedback via REST API

Stethoscope allows users to respond to the displayed alerts in the UI. The `restful_feedback` plugin
tells the Stethoscope API to send this feedback on to another REST API.

##### Configuration

The only configuration required for the `restful_feedback` plugin is:

- `URL`: The URL to which to POST the feedback JSON.


### Logging and Metrics

#### Logging Accesses to Elasticsearch

The `es_logger` plugin tracks each access of Stethoscope's API and logs the access along with the
exact data returned to an Elasticsearch cluster.

##### Configuration

- `ELASTICSEARCH_HOSTS`: List of host specifiers for the Elasticsearch cluster (e.g.,
  `["http://es.example.com:7104"]`)
- `ELASTICSEARCH_INDEX`: Name of the index to which to write.
- `ELASTICSEARCH_DOCTYPE`: Type of document to write.

#### Logging Metrics to Atlas

The `atlas` plugin demonstrates how one might track errors which arise in the API server and post
metrics around those events to an external service. Unfortunately, there is no standard way to
ingest data from Python into [Atlas](https://github.com/Netflix/atlas), so so this plugin is
provided primarily as an example to build upon.

##### Configuration

The `atlas` plugin requires:

- `URL`: The URL to which to POST metrics.

### Event Transforms

One type of plugins takes as input the merged stream of events from the event-providing plugins and
applies a transformation to each event if desired. For example, an event-transform plugin might
inject geo-data into each event after looking up the IP for the event with a geo-data service.

#### VPN Filter

We provide an example event-transform plugin which tags an event as coming from an IP associated
with a given IP range, e.g., that of a corporate VPN. The `vpnfilter` plugin requires the following
configuration variable:

- `VPN_CIDRS`: An iterable of CIDRs, e.g., `["192.0.2.0/24"]` (The value of this variable is passed
  directly to `netaddr.IPSet`, so any value accepted by [that
  method](https://netaddr.readthedocs.io/en/latest/tutorial_03.html) will work.)

### Batch Plugins

#### Incremental Writes to Elasticsearch

The `batch_es` plugin writes each user's device records to Elasticsearch incrementally (i.e., as
they are retrieved by the batch process).

##### Configuration

- `ELASTICSEARCH_HOSTS`: List of host specifiers for the Elasticsearch cluster (e.g.,
  `["http://es.example.com:7104"]`)
- `ELASTICSEARCH_INDEX`: Name of the index to which to write.
- `ELASTICSEARCH_DOCTYPE`: Type of document to write.

#### POSTing a Summary via REST Endpoint

The `batch_restful_summary` plugin collects all of the data from a run of the batch process and
POSTs that data to an external server via HTTP(S).

#####

- `URL`: The URL to which to POST summary data.


## LICENSE

Copyright 2016 Netflix, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

<http://www.apache.org/licenses/LICENSE-2.0>

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


[Flask]: http://flask.pocoo.org/
[FreeTDS]: http://www.freetds.org
[Homebrew]: https://brew.sh
[Klein]: https://github.com/twisted/klein
[Twisted]: https://twistedmatrix.com/
[pyenv-virtualenv]: https://github.com/yyuu/pyenv-virtualenv
[pyenv]: https://github.com/yyuu/pyenv
[tox]: https://tox.readthedocs.io/
[virtualenv]: https://virtualenv.pypa.io
[create-react-app]: https://github.com/facebookincubator/create-react-app
[Docker]: https://www.docker.com/
