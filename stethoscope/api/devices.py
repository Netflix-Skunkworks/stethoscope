# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import copy
import itertools
import operator
import pprint

import arrow
import logbook
import six
import six.moves

import stethoscope.validation
from stethoscope.utils import json_pp


logger = logbook.Logger(__name__)


class MergeConflict(Exception):
  pass


def merge_practices(*args, **kwargs):
  """Merge two or more dictionaries, preferring values in increasing order of index in `order`.

  Treats practices with no `status` as 'na'.
  """
  order = kwargs.pop('order', ['unknown', 'na', 'nudge', 'warn', 'ok'])
  if len(kwargs) > 0:
    raise TypeError("merge_practices() got unexpected keyword argument(s) {:s}"
                    "".format(', '.join("'{:s}'".format(kw) for kw in six.iterkeys(kwargs))))

  practices = dict()
  for practice in set(itertools.chain.from_iterable(arg.keys() for arg in args)):
    practices[practice] = max(
        (arg.get(practice, {'status': 'unknown'}) for arg in args),
        key=lambda _practice: operator.indexOf(order, _practice.get('status', 'unknown'))
    )
  return practices


def merge_identifiers(identifier_sets):
  canonical = identifier_sets[0]
  for identifier_set in identifier_sets[1:]:
    for key, value in six.iteritems(identifier_set):
      if key not in canonical:
        canonical[key] = value
      elif canonical[key] == value:
        continue
      else:
        if isinstance(value, six.string_types) or isinstance(canonical[key], six.string_types):
          raise MergeConflict("could not merge values for key '{!s}'; identifier_sets:\n{:s}"
                              "".format(key, pprint.pformat(identifier_sets)))
        else:
          canonical[key] = list(set(canonical[key] + value))
  return canonical


def compare_identifiers(this_identifier_set, other_identifier_set):
  """Compare the identifier dictionaries from two devices.

  Returns `True` if any identifiers match between the two sets, `False` otherwise.
  """
  for identifier, this_value in six.iteritems(this_identifier_set):
    if identifier not in other_identifier_set:
      continue
    other_value = other_identifier_set[identifier]

    if len(this_value) == 0 or len(other_value) == 0:
      continue

    # shortcut if possible
    if this_value == other_value:
      return True

    if isinstance(this_value, six.string_types) and isinstance(other_value, six.string_types):
      # both are strings and they don't match, so continue
      continue

    # convert each to single-element list if not already a non-string iterable
    if isinstance(this_value, six.string_types):
      this_value = [this_value]
    if isinstance(other_value, six.string_types):
      other_value = [other_value]

    if identifier == 'mac_addresses':
      # filter out MAC addresses that should not be considered unique identifiers
      this_value = list(stethoscope.validation.filter_macaddrs(this_value))
      other_value = list(stethoscope.validation.filter_macaddrs(other_value))

    # now can check cartesian product for any matches
    if any(foo == bar for (foo, bar) in itertools.product(this_value, other_value)):
      return True

  return False


def should_merge(groups):
  """Returns a pair of indices for groups which should be merged.

  Two groups should be merged if they contain devices for which at least one identifier matches
  across the two groups and no identifiers conflict.
  """

  for this_idx, this_group in enumerate(groups):
    for other_idx, other_group in enumerate(groups):
      if other_idx == this_idx:
        continue
      for this_device in this_group:
        for other_device in other_group:
          this_identifiers = this_device.get('identifiers', {})
          other_identifiers = other_device.get('identifiers', {})
          if compare_identifiers(this_identifiers, other_identifiers):
            try:
              merge_identifiers([this_identifiers, other_identifiers])
            except MergeConflict:
              logger.exception("merge conflict:\nthis:\n{:s}\nother:\n{:s}",
                               json_pp(this_device), json_pp(other_device))
              continue
            return this_idx, other_idx
  return False


def group_devices(devices):
  # Start with each device in it's own group, then check if any two groups should be merged. If so,
  # merge them and recheck; if not, we're done.
  groups = [[device] for device in devices]
  while True:
    indices = should_merge(groups)
    if not indices:
      break
    groups[indices[0]] += groups[indices[1]]
    del groups[indices[1]]
  return groups


def merge_device_group(entries):
  if len(entries) > 1:
    logger.debug("merging devices:\n{!s}", pprint.pformat(entries, depth=4))

  device = dict()

  debug = any('_raw' in entry for entry in entries)
  if debug:
    device['_raw'] = entries

  device['sources'] = [entry['source'] for entry in entries]
  device['practices'] = merge_practices(*six.moves.map(copy.deepcopy,
    (entry.get('practices', {}) for entry in entries)))
  device['identifiers'] = merge_identifiers(list(six.moves.map(copy.deepcopy,
    (entry.get('identifiers', {}) for entry in entries))))

  keys = set(itertools.chain.from_iterable(entry.keys() for entry in entries)) \
      - set(['_raw', 'source', 'practices', 'identifiers'])

  # merge other keys by using the most recent value that exists
  entries = sorted(entries, key=lambda entry: entry.get("last_sync", arrow.get(0)))
  for key in keys:
    for entry in entries:
      if key in entry:
        device[key] = copy.deepcopy(entry[key])

  return device


def merge_devices(devices):
  canonical = list()
  for entry_set in group_devices(devices):
    canonical.append(merge_device_group(entry_set))
  return canonical
