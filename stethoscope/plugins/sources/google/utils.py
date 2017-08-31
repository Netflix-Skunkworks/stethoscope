# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import pprint

import arrow
import logbook
import oauth2client
import six
from retrying import retry


logger = logbook.Logger(__name__)


def parse_activity(activity):
  dt = arrow.get(activity['id']['time'])

  if len(activity['events']) > 1:
    logger.error("more than one event returned: {!s}", pprint.pformat(activity['events']))

  result = activity['events'][-1]['name']
  # TODO: replace with parse_parameters
  params = dict((pair['name'], pair['value']) for pair in activity['events'][-1]['parameters'])

  content_lines = [
    "Google Login: {dt!s}",
    "IP: {ip_address!s}",
    "Event: {result!s}",
  ]
  content_lines.extend("{:s}: {!s}".format(key, val) for key, val in six.iteritems(params))
  content = "<br/>".join(content_lines).format(dt=dt, ip_address=activity['ipAddress'],
      result=result)
  event = {
    'source': 'google',
    'type': 'logout' if result == 'logout' else params['login_type'],
    'success': (result in ['login_success', 'logout']),
    'reason': params.get('login_failure_type', ''),
    'ip_address': activity['ipAddress'],
    'timestamp': dt,
    'content': content,
    '_raw': activity,
  }

  # logger.debug("GOOGLE LOGIN: {!s}\n  entry: {!r}\n  event: {!r}", activity['id']['time'],
  # activity, event)
  return event


def execute_batch(resource, request, result_key, max_results=None):
  """Get accumulated results from paginated responses to Google API requests."""
  results = list()
  while request:
    response = execute_request(request)
    if result_key in response:
      results.extend(response[result_key])
    if max_results is not None and len(results) >= max_results:
      return results[:max_results]
    request = resource.list_next(request, response)
  return results


def execute_request(request):
  """Execute a Google API request with retries and exponential backoff."""
  return request.execute(num_retries=3)


def parse_parameters_list(dict_list):
  """

  >>> import arrow
  >>> returned = parse_parameters_list([
  ...   { "name": "accounts:is_2sv_enrolled", "boolValue": False },
  ...   { "name": "accounts:last_name", "stringValue": "Smith" },
  ...   { "name": "accounts:drive_used_quota_in_mb", "intValue": "0" },
  ...   { "name": "accounts:creation_time",
  ...     "datetimeValue": "2010-10-28T10:26:35.000Z" },
  ... ])
  >>> returned == {
  ...   "accounts:is_2sv_enrolled": False,
  ...   "accounts:last_name": "Smith",
  ...   "accounts:drive_used_quota_in_mb": 0,
  ...   "accounts:creation_time": arrow.Arrow(2010, 10, 28, 10, 26, 35),
  ... }
  True

  >>> parse_parameters_list([{ "name": "fakeValue", "otherType": False }])
  Traceback (most recent call last):
    ...
  ValueError: Failed to determine appropriate type for parameter 'fakeValue'

  """

  retval = dict()
  for item_dict in dict_list:
    if 'boolValue' in item_dict:
      value = item_dict['boolValue']
    elif 'intValue' in item_dict:
      value = int(item_dict['intValue'])
    elif 'stringValue' in item_dict:
      value = item_dict['stringValue']
    elif 'datetimeValue' in item_dict:
      value = arrow.get(item_dict['datetimeValue'])
    else:
      raise ValueError("Failed to determine appropriate type for parameter "
                       "{!r}".format(item_dict['name']))
    retval[item_dict['name']] = value
  return retval
