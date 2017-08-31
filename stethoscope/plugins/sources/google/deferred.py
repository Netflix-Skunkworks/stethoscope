# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import sys
from itertools import chain

import httplib2
import logbook
from twisted.internet import defer, threads

import stethoscope.api.utils
import stethoscope.configurator
import stethoscope.plugins.sources.google.base


logger = logbook.Logger(__name__)


class GoogleAPIConnection(stethoscope.configurator.Configurator):

  config_keys = (
    'GOOGLE_API_SECRETS',
    'GOOGLE_API_USERNAME',
    'GOOGLE_API_SCOPES',
  )

  @property
  def connection(self):
    return self.connect()

  @property
  def credentials(self):
    if getattr(self, '_credentials', None) is None:
      try:
        self._credentials = self.get_google_api_credentials()
      except Exception as exc:
        raise RuntimeError("Unable to get credentials for Google API access: {!s}".format(exc))
    return self._credentials

  def connect(self, http=None):
    """Get an authorized `httplib2.Http` object for interacting with Google APIs."""
    if http is None:
      http = httplib2.Http()
    return self.credentials.authorize(http)

  def get_google_api_credentials(self):
    """Create a credentials object for talking to Google APIs."""
    secrets = self.config['GOOGLE_API_SECRETS']

    try:
      # oauth2client < 2.0.0
      import oauth2client.client
      credentials = oauth2client.client.SignedJwtAssertionCredentials(secrets['client_email'],
          secrets['private_key'], token_uri=secrets['token_uri'],
          scope=self.config['GOOGLE_API_SCOPES'], sub=self.config['GOOGLE_API_USERNAME'])
    except AttributeError:
      # oauth2client >= 2.0.0
      import oauth2client.service_account
      root = oauth2client.service_account.ServiceAccountCredentials.from_json_keyfile_dict(
          secrets, scopes=self.config['GOOGLE_API_SCOPES'])
      credentials = root.create_delegated(self.config['GOOGLE_API_USERNAME'])

    return credentials


class DeferredGoogleDataSource(
    GoogleAPIConnection,
    stethoscope.plugins.sources.google.base.GoogleDataSourceBase,
  ):

  def get_events_by_email(self, email, **kwargs):
    return threads.deferToThread(super(DeferredGoogleDataSource, self).get_events_by_email, email,
        **kwargs)

  def get_userinfo_by_email(self, email):
    return threads.deferToThread(super(DeferredGoogleDataSource, self).get_userinfo_by_email, email)

  def get_account_by_email(self, email):
    return threads.deferToThread(super(DeferredGoogleDataSource, self).get_account_by_email, email)

  def get_devices_by_email(self, email):
    deferred_list = defer.DeferredList([
        threads.deferToThread(super(DeferredGoogleDataSource, self)._get_mobile_devices_by_email,
          email),
        threads.deferToThread(super(DeferredGoogleDataSource, self)._get_chromeos_devices_by_email,
          email),
      ], consumeErrors=True)
    deferred_list.addCallback(stethoscope.api.utils.filter_by_status,
        context=sys._getframe().f_code.co_name, level=logbook.ERROR)
    deferred_list.addCallback(chain.from_iterable)
    deferred_list.addCallback(list)
    return deferred_list

  def test_connectivity(self):
    return threads.deferToThread(super(DeferredGoogleDataSource, self).test_connectivity)
