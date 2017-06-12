# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import logging
import os

import flask
import logbook
import stevedore.driver
import validate_email
import werkzeug.exceptions

import stethoscope.auth
import stethoscope.csrf
import stethoscope.plugins.utils


logger = logbook.Logger(__name__)


class CustomFlask(flask.Flask):
  jinja_options = flask.Flask.jinja_options.copy()
  jinja_options.update(dict(
    variable_start_string='{{{',
    variable_end_string='}}}',
  ))


def setup_logbook(app):
  # remove pre-existing handlers
  del app.logger.handlers[:]

  # redirect app.logger log records to logbook
  redirect_handler = logbook.compat.RedirectLoggingHandler()
  app.logger.addHandler(redirect_handler)

  # set up logbook handlers
  app.config['LOGBOOK'].push_application()

  # log messages to other loggers to the same handlers as the app's logger
  for logger_ in map(logging.getLogger, ['stevedore']):
    logger_.addHandler(redirect_handler)

  return app


def create_app():
  app = CustomFlask(__name__, instance_relative_config=True,
      instance_path=os.environ.get('STETHOSCOPE_LOGIN_INSTANCE_PATH'))

  # load default config from package
  app.config.from_object('stethoscope.login.defaults')

  # load config specified via env var
  # should be absolute path to a config file
  app.config.from_envvar('STETHOSCOPE_LOGIN_CONFIG', silent=True)

  # load instance config (config.py from instance/)
  app.config.from_pyfile('config.py', silent=True)

  setup_logbook(app)

  @app.route('/favicon.ico')
  def favicon():
    flask.abort(404)

  @app.route('/healthcheck')
  def healthcheck():
    return 'ok'

  # setup for JWT
  auth = stethoscope.auth.AuthProvider(app.config)

  # setup for CSRF
  csrf = stethoscope.csrf.CSRFProtection(app.config)

  # setup login manager
  login_manager = stevedore.driver.DriverManager(
      namespace='stethoscope.plugins.login',
      name=app.config.get('LOGIN_MANAGER', 'null'),
      invoke_on_load=True,
      invoke_args=(app,),
      on_load_failure_callback=stethoscope.plugins.utils.extension_load_failure_callback
  ).driver

  @login_manager.login_success
  def login_success(token, profile, email=None):
    # if behind ELB, use the original URL scheme; otherwise, use the scheme provided in the request
    scheme = flask.request.headers.get('X-Forwarded-Proto',
        flask.request.environ['wsgi.url_scheme'])

    if email is None:
      email = profile.get('email', profile['sub'])
    response = flask.redirect(flask.url_for('index', email=email, _scheme=scheme, _external=True))

    response.set_cookie('token', auth.create_token(**profile),
      httponly=app.config['SESSION_COOKIE_HTTPONLY'],
      secure=app.config['SESSION_COOKIE_SECURE'])

    csrf_token = stethoscope.csrf.generate_token()
    response.set_cookie(csrf._csrf_cookie_name, csrf_token,
        httponly=csrf._csrf_cookie_httponly, secure=csrf._csrf_cookie_secure,
        domain=csrf._csrf_cookie_domain, max_age=csrf._csrf_cookie_timeout)
    app.jinja_env.globals[csrf._csrf_input_name] = csrf_token

    return response

  @app.route('/')
  @app.route('/<string:email>')
  def index(email=None):
    token = flask.request.cookies.get('token')

    try:
      userinfo = auth.decode_token(token)
    except werkzeug.exceptions.Unauthorized as exc:
      if token is not None:
        logger.exception("Invalid token in auth flow:")
      return flask.redirect(login_manager.authorization_url())

    if email is None:
      email = userinfo.get('email', userinfo['sub'])

    if not validate_email.validate_email(email):
      flask.abort(400)

    return flask.make_response(flask.render_template('layout.html', email=email,
      debug=app.config['DEBUG']))

  app.jinja_env.filters['strftime'] = lambda dt: dt.strftime('%Y-%m-%d %H:%M:%S')

  logger.info("Hailing frequencies open.")

  return app
