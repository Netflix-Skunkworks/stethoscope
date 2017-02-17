# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import collections

import logbook

import stethoscope.api.exceptions


logger = logbook.Logger(__name__)


def check_response(response, service=None, resource=None):
  if response.code >= 300 or response.code < 200:
    raise stethoscope.api.exceptions.InvalidResponseException(response.code, service=service,
        resource=resource)
  return response


def check_user_not_found(failure):
  return check_not_found(failure,
      exception_types=stethoscope.api.exceptions.UserNotFoundException)


def check_device_not_found(failure):
  return check_not_found(failure,
      exception_types=stethoscope.api.exceptions.DeviceNotFoundException)


def check_not_found(failure, exception_types=(stethoscope.api.exceptions.UserNotFoundException,
  stethoscope.api.exceptions.DeviceNotFoundException)):
  # log user-not-found exceptions, but don't re-raise
  if isinstance(failure.value, exception_types):
    logger.debug(str(failure.value))
    return []
  return failure


def write_to_file(response, filename="response.json"):
  with open(filename, "w") as fo:
    fo.write(response)
  return response


def filter_keyed_by_status(keys, values_with_status, context=None, level=logbook.ERROR):
  """Filter `values_with_status` (a `list` of `(bool, value)`); return dict with corresponding keys.

  >>> dict(filter_keyed_by_status(['one', 'two'], [(True, 'foo'), (False, 'bar')]))
  {'one': 'foo'}

  """

  values = collections.OrderedDict()
  for key, (status, value_or_traceback) in zip(keys, values_with_status):
    if not status:
      logger.log(level, "[{!s}] failed to retrieve data for '{!s}':\n{!s}", context, key,
          value_or_traceback)
    else:
      values[key] = value_or_traceback
  return values


def filter_by_status(values_with_status, context=None, level=logbook.ERROR):
  """Filter a `list` of `(bool, value)` pairs on the `bool` value, warning on `False` values.

  >>> filter_by_status([(True, 'foo'), (False, 'bar')])
  ['foo']

  """
  values = list()
  for (status, value_or_traceback) in values_with_status:
    if not status:
      logger.log(level, "[{!s}] failed to retrieve data:\n{!s}", context, value_or_traceback)
    else:
      values.append(value_or_traceback)
  return values
