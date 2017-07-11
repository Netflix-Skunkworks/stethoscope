# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import abc
import json
import types

import logbook
import requests
import six

import stethoscope.configurator
import stethoscope.utils


logger = logbook.Logger(__name__)


@six.add_metaclass(abc.ABCMeta)
class BaseHTTPMixin(stethoscope.configurator.Configurator):
  """Abstract plugin base class for implementing methods to POST to arbitrary HTTP endpoints."""

  config_keys = (
    'URL',
  )

  def _process_arguments(self, payload, **kwargs):
    url = self.config['URL']

    content = json.dumps(payload, default=stethoscope.utils.json_serialize_datetime)

    headers = kwargs.get('headers', {})
    headers.setdefault('Content-Type', 'application/json')
    headers.setdefault('User-Agent', 'Stethoscope')
    kwargs['headers'] = headers

    default_timeout = self.config.get('TIMEOUT', self.config.get('DEFAULT_TIMEOUT'))
    kwargs.setdefault('timeout', default_timeout)

    logger.debug("posting\n  to: {!s}\n  kwargs: {!s}\n  content: {!r}", url, kwargs, content)

    return url, content, kwargs


def _test_connectivity(self):
  """Method to bind to `HTTPMixin` instances with a configured `HEALTHCHECK_URL`."""
  response = requests.get(self.config['HEALTHCHECK_URL'])
  if response.status_code != 200:
    raise Exception("Healthcheck endpoint returned {!d}".format(response.status_code))
  return response


@six.add_metaclass(abc.ABCMeta)
class HTTPMixin(BaseHTTPMixin):

  def __init__(self, config):
    if 'HEALTHCHECK_URL' in config:
      # bind the connectivity test method to this instance if a healthcheck URL is configured
      self.test_connectivity = types.MethodType(_test_connectivity, self)
    super(HTTPMixin, self).__init__(config)

  def post(self, payload, **kwargs):
    """Execute a POST request to the object's URL returning the response body."""
    url, content, kwargs = self._process_arguments(payload, **kwargs)
    response = requests.post(url, data=content, **kwargs)

    try:
      response.raise_for_status()
    except:
      logger.exception("request to {!s} returned {:d}", url, response.status_code)
      logger.debug("response text:\n{!s}", response.text)

    return response
