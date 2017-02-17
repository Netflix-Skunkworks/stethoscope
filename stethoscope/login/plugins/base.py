# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import abc

import flask
import logbook
import six


logger = logbook.Logger(__name__)


@six.add_metaclass(abc.ABCMeta)
class LoginPluginBase(object):

  def __init__(self, app=None):
    if app:
      self.init_app(app)

  def login_success(self, f):
    self.login_success_func = f
    return f

  def login_failure_func(self, exc):
    """Default function to call for login failure."""
    flask.abort(401)

  def login_failure(self, f):
    self.login_failure_func = f
    return f

  @abc.abstractmethod
  def init_app(self, app):
    pass

  @abc.abstractmethod
  def authorization_url(self, **kwargs):
    pass


class NullLogin(LoginPluginBase):
  """Process as a successful authentication without actually doing anything."""

  callback_endpoint = 'null_login'

  def init_app(self, app):
    app.add_url_rule('/auth/null', self.callback_endpoint, self.login)
    app.add_url_rule('/auth/null/<string:email>', self.callback_endpoint, self.login)

  def authorization_url(self, **kwargs):
    # redirect straight to our login function
    return flask.url_for(self.callback_endpoint, **kwargs)

  def login(self, email='user@example.com'):
    # make up a profile and return it
    return self.login_success_func(None, {'sub': '*'}, email=email)
