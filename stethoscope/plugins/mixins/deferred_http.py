# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import abc

import logbook
import six
import treq
import txwebretry

import stethoscope.api.utils
import stethoscope.plugins.mixins.http


logger = logbook.Logger(__name__)


@six.add_metaclass(abc.ABCMeta)
class DeferredHTTPMixin(stethoscope.plugins.mixins.http.BaseHTTPMixin):

  def check_response(self, response):
    return stethoscope.api.utils.check_response(response, service=self.plugin_name, resource='post')

  def log_error(self, failure):
    logger.error("{!s} error:\n{!s}", self.plugin_name, failure)
    return failure

  def _post(self, url, content, **kwargs):
    return txwebretry.ExponentialBackoffRetry(3)(treq.post, url, content, **kwargs)

  def post(self, payload, **kwargs):
    """Execute a POST request to the object's URL, returning a deferred with a `treq` Response."""
    url, content, kwargs = self._process_arguments(payload, **kwargs)

    deferred = self._post(url, content, **kwargs)
    deferred.addCallback(self.check_response)
    deferred.addCallback(treq.content)
    deferred.addErrback(self.log_error)

    return deferred
