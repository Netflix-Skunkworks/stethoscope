# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import flask
import logbook
import requests_oauthlib
import six

import stethoscope.login.plugins.base


logger = logbook.Logger(__name__)

DEFAULTS = {
    'CALLBACK_PATHS': ['/auth/oidc', '/auth/oidc/<string:email>'],
    'CALLBACK_PORT': 5000,
    'CALLBACK_SCHEME': 'https',
    'SCOPES': ['openid', 'email', 'profile'],
}


class OpenIDConnectLogin(stethoscope.login.plugins.base.LoginPluginBase):

  config_prefix = 'OIDC_'
  callback_endpoint = 'oidc_login'
  state_session_key = 'oidc_state'

  def __init__(self, app=None):
    if app:
      self.init_app(app)

  def init_app(self, app):
    for key, default_value in six.iteritems(DEFAULTS):
      app.config.setdefault(self.config_prefix + key, default_value)

    for callback_path in self.get_config_value('CALLBACK_PATHS', app):
      app.add_url_rule(callback_path, self.callback_endpoint, self.login)

  def get_config_value(self, name, app=None):
    if app is None:
      app = flask.current_app
    return app.config[self.config_prefix + name]

  def callback_url(self, **kwargs):
    server = self.get_config_value('CALLBACK_URL')
    scheme = self.get_config_value('CALLBACK_SCHEME')
    port = str(self.get_config_value('CALLBACK_PORT'))
    logger.debug("scheme={!r}; server={!r}; port={!r}", scheme, server, port)

    uri = scheme + '://' + server
    if port != '':
      uri += ':' + port
    uri += flask.url_for(self.callback_endpoint, **kwargs)

    return uri

  def authorization_url(self, **kwargs):
    redirect_uri = self.callback_url(**kwargs)
    flask.current_app.logger.debug("redirect URI: {!r}".format(redirect_uri))

    oauth2_session = requests_oauthlib.OAuth2Session(self.get_config_value('CLIENT_ID'),
        redirect_uri=redirect_uri, scope=self.get_config_value('SCOPES'))

    auth_url, state = oauth2_session.authorization_url(self.get_config_value('AUTHORIZATION_URL'))
    flask.session[self.state_session_key] = state
    flask.current_app.logger.debug("authorization URL: {!s}".format(auth_url))

    return auth_url

  def login(self, **kwargs):
    try:
      oauth2_session = requests_oauthlib.OAuth2Session(client_id=self.get_config_value('CLIENT_ID'),
          redirect_uri=self.callback_url(**kwargs),
          scope=self.get_config_value('SCOPES'),
          state=flask.session[self.state_session_key])
      token = oauth2_session.fetch_token(self.get_config_value('TOKEN_URL'),
          code=flask.request.args['code'], client_secret=self.get_config_value('CLIENT_SECRET'))
    except Exception as exc:
      flask.current_app.logger.exception("exception while retrieving token")
      self.login_failure_func(exc)

    try:
      profile = self.get_profile(oauth2_session)
    except Exception as exc:
      flask.current_app.logger.exception("exception while retrieving profile")
      self.login_failure_func(exc)
    # flask.current_app.logger.debug("profile: {!s}".format(pprint.pformat(profile)))

    return self.login_success_func(token, profile, **kwargs)

  def get_profile(self, oauth2_session):
    resp = oauth2_session.get(self.get_config_value('USERINFO_URL'))
    resp.raise_for_status()
    return resp.json()
