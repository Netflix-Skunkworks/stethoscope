# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import time

import logbook

import stethoscope.plugins.mixins.deferred_http


logger = logbook.Logger(__name__)


class AtlasLogger(stethoscope.plugins.mixins.deferred_http.DeferredHTTPMixin):
  """Log metrics to Atlas via REST API."""

  def post_counter(self, name, tags, value=1):
    payload = {
      'timestamp': int(time.time() * 1000.0),
      'type': 'COUNTER',
      'name': name,
      'tags': tags,
      'value': value,
    }
    return self.post(payload)

  def log_failure(self, request, failure):
    tags = {
      'exceptionName': type(failure.value).__name__,
      # 'endpoint': '-'.join(request.prepath),
    }
    return self.post_counter('stethoscope.api.numExceptions', tags)

  def test_connectivity(self):
    # send an empty set of metrics to test connectivity
    return self.post([])
