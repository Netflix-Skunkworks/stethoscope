# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import json

import six

import stethoscope.api.devices
import stethoscope.utils


def serialized_endpoint(*_callbacks):
  """Decorator which wraps an endpoint by applying callbacks to the results then serializing to JSON.

  First, the decorated function is called and must return a `defer.Deferred`. The callbacks supplied
  to the decorator are then applied followed by any callbacks supplied as keyword arguments to the
  decorated function.  The result is then serialized and returned in the response (with
  ``Content-Type`` set to ``application/json``).
  """
  def decorator(func):
    @six.wraps(func)
    def wrapped(request, *args, **kwargs):
      callbacks = kwargs.pop('callbacks', [])
      # logger.debug("in wrapped:\nargs: {!r}\nkwargs: {!r}", args, kwargs)

      deferred_list = func(*args, **kwargs)

      for callback in list(_callbacks) + callbacks:
        deferred_list.addCallback(callback)

      deferred_list.addCallback(json.dumps, default=stethoscope.utils.json_serialize_datetime)
      request.setHeader('Content-Type', 'application/json')
      return deferred_list
    return wrapped
  return decorator
