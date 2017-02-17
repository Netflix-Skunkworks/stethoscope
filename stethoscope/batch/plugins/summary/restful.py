# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import pprint
import json

import arrow
import logbook
import six

import stethoscope.plugins.mixins.http
import stethoscope.configurator


logger = logbook.Logger(__name__)


class RESTfulSummary(
    stethoscope.plugins.mixins.http.HTTPMixin,
    stethoscope.configurator.Configurator
  ):
  """Plugin to summarize and report devices via REST API."""

  def transform_to_snapshot(self, devices_by_email):
    since = arrow.utcnow().replace(days=-14)

    snapshot = list()
    for email, devices in six.iteritems(devices_by_email):
      for device in devices:
        if 'last_sync' not in device or device.get('last_sync') < since:
          # ignore devices that haven't synced in more than N days
          continue
        snapshot.append(device)

    return snapshot

  def post(self, devices):
    snapshot = self.transform_to_snapshot(devices)
    logger.debug("snapshot:\n{!s}", pprint.pformat(snapshot))

    status_code, response_text = super(RESTfulSummary, self).post(snapshot)
    try:
      response_json = json.loads(response_text)
    except:
      logger.warning("server responded with {:d}:\n{!r}", status_code, response_text)
    else:
      logger.warning("server responded with {:d}:\n{!s}", status_code,
          pprint.pformat(response_json))

    return status_code, response_json
