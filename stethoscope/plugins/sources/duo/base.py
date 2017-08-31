# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import time

import duo_client

import stethoscope.configurator
import stethoscope.plugins.sources.duo.utils


class DuoDataSourceBase(stethoscope.configurator.Configurator):

  config_keys = (
    'DUO_INTEGRATION_KEY',
    'DUO_SECRET_KEY',
    'DUO_API_HOSTNAME',
  )

  def __init__(self, *args, **kwargs):
    self._events = list()
    super(DuoDataSourceBase, self).__init__(*args, **kwargs)

  def connect(self):
    return duo_client.Admin(self.config['DUO_INTEGRATION_KEY'],
        self.config['DUO_SECRET_KEY'], self.config['DUO_API_HOSTNAME'])

  def update_events(self):
    # TODO: fix so events list doesn't grow arbitrarily large over time
    end = int(time.time())
    if len(self._events) > 0:
      start = self._events[-1]['timestamp'].timestamp + 1
    else:
      start = end - (60 * 60 * 12)
    self._events.extend(stethoscope.plugins.sources.duo.utils.parse_duo_auth_log(
      stethoscope.plugins.sources.duo.utils.get_auth_log(self.connection, start, end)))

  def get_events_by_email(self, email):
    """Retrieve Duo authentication log entries for given user."""
    self.update_events()
    username = email.split('@')[0]
    return [event for event in self._events if event['username'] == username]
