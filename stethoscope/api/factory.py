# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import os

import flask.config
import klein
import logbook
import treq
from twisted.internet import defer

import stethoscope.auth
import stethoscope.csrf
import stethoscope.plugins.utils
from stethoscope.api.endpoints.accounts import register_account_api_endpoints
from stethoscope.api.endpoints.devices import register_device_api_endpoints
from stethoscope.api.endpoints.events import register_event_api_endpoints
from stethoscope.api.endpoints.feedback import register_feedback_api_endpoints
from stethoscope.api.endpoints.notifications import register_notification_api_endpoints


logger = logbook.Logger(__name__)


def get_config():
  config = flask.config.Config(os.environ.get('STETHOSCOPE_API_INSTANCE_PATH', './instance/'))

  # load default config from package
  config.from_object('stethoscope.api.defaults')

  # load config specified via env var
  # should be absolute path to a config file
  config.from_envvar('STETHOSCOPE_API_CONFIG', silent=True)

  # load instance config (config.py from instance/)
  config.from_pyfile('config.py')

  return config


def register_error_handlers(app, config, auth):
  plugins = stethoscope.plugins.utils.instantiate_plugins(config,
      namespace='stethoscope.plugins.logging.failure')
  logger.debug("loaded failure logging plugins: {!r}", [hook.name for hook in plugins])

  @app.handle_errors(Exception)
  def check_authorization(request, failure):
    logger.error("Exception while handling request:\n{!s}\n{:s}", request, failure.getTraceback())

    # log to, e.g., a metrics backend like atlas
    for plugin in plugins:
      plugin.obj.log_failure(request, failure)

    # does this lead to infinite recursion?
    # will raise AuthError if token is invalid
    auth.check_token(request)
    return failure


@defer.inlineCallbacks
def check_upstream_response(response, request):
  content = yield treq.content(response)
  if response.code != 200:
    request.setResponseCode(502)
    defer.returnValue("Upstream response code: {:d}\n{!s}".format(response.code, content))
  else:
    defer.returnValue(content)


def handle_upstream_error(failure, request):
  request.setResponseCode(502)
  logger.error("Error connecting to upstream: {!s}\n{:s}", failure.value, failure.getTraceback())
  return "Error connecting to upstream:\n{:s}".format(failure.getErrorMessage())


def register_endpoints(app, config, auth, csrf):
  @app.route('/healthcheck')
  def healthcheck(request):
    upstream = 'http://{!s}/healthcheck'.format(os.getenv("STETHOSCOPE_LOGIN_HOST",
      "127.0.0.1:5002"))
    deferred = treq.get(upstream, timeout=0.1, headers={'Host': request.getHost().host})
    deferred.addCallback(check_upstream_response, request)
    deferred.addErrback(handle_upstream_error, request)
    return deferred

  # gather hooks to external loggers
  log_hooks = stethoscope.plugins.utils.instantiate_plugins(config,
      namespace='stethoscope.plugins.logging.request')
  logger.debug("loaded request logging hooks: {!r}", [hook.name for hook in log_hooks])

  with app.subroute('/api/v1'):
    register_device_api_endpoints(app, config, auth, log_hooks=log_hooks)
    register_event_api_endpoints(app, config, auth, log_hooks=log_hooks)
    register_account_api_endpoints(app, config, auth, log_hooks=log_hooks)
    register_notification_api_endpoints(app, config, auth, log_hooks=log_hooks)
    register_feedback_api_endpoints(app, config, auth, csrf, log_hooks=log_hooks)
    # temporarily disabled: userinfo is not in use
    # register_userinfo_api_endpoints(app, config, auth, log_hooks=log_hooks)


def create_app():
  config = get_config()

  config['LOGBOOK'].push_application()

  if "PLUGINS" not in config or len(config["PLUGINS"]) < 1:
    logger.warn("Missing or invalid PLUGINS configuration!")

  app = klein.Klein()
  auth = stethoscope.auth.KleinAuthProvider(config)
  csrf = stethoscope.csrf.CSRFProtection(config)

  register_error_handlers(app, config, auth)
  register_endpoints(app, config, auth, csrf)

  logger.info("Shields up, weapons online.")

  return app
