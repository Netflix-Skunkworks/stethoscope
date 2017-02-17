# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import pprint

import logbook
import six.moves


logger = logbook.Logger(__name__)


def _parse_parameter_dict(item_dict):
  """Convert a mapping with 'name' and 'value' keys into a key-value tuple.

  >>> _parse_parameter_dict({
  ...   u'id': 65,
  ...   u'name': u'Computer Model',
  ...   u'type': u'String',
  ...   u'value': u'MacBook Pro (Retina, 15-inch, Mid 2015)',
  ... })
  (u'Computer Model', u'MacBook Pro (Retina, 15-inch, Mid 2015)')

  >>> _parse_parameter_dict({
  ...   u'value': u'MacBook Pro (Retina, 15-inch, Mid 2015)',
  ... })
  Traceback (most recent call last):
    ...
  KeyError: 'name'

  """
  try:
    name = item_dict['name']
    value = item_dict['value']
    # appears there is only the string type at the moment (2015-12-17)
    # vtype = item_dict['type']
    # not using 'id'
    # item_dict['id']
  except KeyError:
    logger.error("incorrect input for parameter: {!s}".format(pprint.pformat(item_dict)))
    raise
  return (name, value)


def _parse_parameter_list(dict_list):
  """Create a mapping from the given list of item-describing dictionaries.

  >>> returned = _parse_parameter_list([
  ...   {u'id': 68,
  ...    u'name': u'Carbon Black Installed',
  ...    u'type': u'String',
  ...    u'value': u'Installed'},
  ...   {u'id': 65,
  ...    u'name': u'Computer Model',
  ...    u'type': u'String',
  ...    u'value': u'MacBook Pro (Retina, 15-inch, Mid 2015)'},
  ... ])
  >>> returned == {
  ...   u'Computer Model': u'MacBook Pro (Retina, 15-inch, Mid 2015)',
  ...   u'Carbon Black Installed': u'Installed',
  ... }
  True

  """
  return dict(six.moves.map(_parse_parameter_dict, dict_list))
