# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import copy
import unittest

import arrow
import pytest

import stethoscope.api.devices


DECAFBAD = '00:DE:CA:FB:AD:00'
DEADBEEF = '00:DE:AD:BE:EF:00'
LOCALMAC = '02:00:00:00:00:00'
GROUPMAC = '01:00:00:00:00:00'
ZERODMAC = '00:00:00:00:00:00'


def _copy_then_apply(fn, *values):
  return fn(*(copy.deepcopy(val) for val in values))


def test_compare_identifiers_by_serial():
  this = {'serial': '0xDECAFBAD'}
  other = {'serial': '0xDECAFBAD'}
  third = {'serial': '0xDEADBEEF'}
  assert stethoscope.api.devices.compare_identifiers(this, other)
  assert not stethoscope.api.devices.compare_identifiers(this, third)
  assert not stethoscope.api.devices.compare_identifiers(other, third)


def test_compare_identifiers_by_macaddr():
  this = {'mac_addresses': [DECAFBAD]}
  other = {'mac_addresses': [DECAFBAD, DEADBEEF]}
  third = {'mac_addresses': [DEADBEEF]}
  assert stethoscope.api.devices.compare_identifiers(this, other)
  assert stethoscope.api.devices.compare_identifiers(other, third)
  assert not stethoscope.api.devices.compare_identifiers(this, third)


def test_compare_identifiers_ignores_empty():
  this = {'mac_addresses': []}
  other = {'mac_addresses': []}
  assert not stethoscope.api.devices.compare_identifiers(this, other)


def test_compare_identifiers_by_macaddr_with_locally_administered():
  this = {'mac_addresses': [DECAFBAD, LOCALMAC]}
  other = {'mac_addresses': [DECAFBAD, DEADBEEF, LOCALMAC]}
  third = {'mac_addresses': [DEADBEEF, LOCALMAC]}
  assert stethoscope.api.devices.compare_identifiers(this, other)
  assert stethoscope.api.devices.compare_identifiers(other, third)
  assert not stethoscope.api.devices.compare_identifiers(this, third)


def test_compare_identifiers_by_macaddr_with_group_addresses():
  this = {'mac_addresses': [DECAFBAD, GROUPMAC]}
  other = {'mac_addresses': [DECAFBAD, DEADBEEF, GROUPMAC]}
  third = {'mac_addresses': [DEADBEEF, GROUPMAC]}
  assert stethoscope.api.devices.compare_identifiers(this, other)
  assert stethoscope.api.devices.compare_identifiers(other, third)
  assert not stethoscope.api.devices.compare_identifiers(this, third)


def test_compare_identifiers_by_macaddr_with_zerod_addresses():
  this = {'mac_addresses': [DECAFBAD, ZERODMAC]}
  other = {'mac_addresses': [DECAFBAD, DEADBEEF, ZERODMAC]}
  third = {'mac_addresses': [DEADBEEF, ZERODMAC]}
  assert stethoscope.api.devices.compare_identifiers(this, other)
  assert stethoscope.api.devices.compare_identifiers(other, third)
  assert not stethoscope.api.devices.compare_identifiers(this, third)


def test_group_devices_by_macaddr():
  this = {'identifiers': {'mac_addresses': [DECAFBAD]}}
  other = {'identifiers': {'mac_addresses': [DECAFBAD, DEADBEEF]}}

  groups = stethoscope.api.devices.group_devices([this, other])
  assert groups == [[this, other]]

  third = {'mac_addresses': [DEADBEEF]}
  groups = stethoscope.api.devices.group_devices([this, third])
  assert groups == [[this], [third]]


def test_group_devices_by_multiple():
  this = {
    "identifiers": {
      "mac_addresses": [
        DECAFBAD,
        DEADBEEF,
      ],
      "serial": "0xDEADBEEF",
    }
  }

  other = {
    "identifiers": {
      "serial": "0xDEADBEEF",
    }
  }

  third = {
    "identifiers": {
      "mac_addresses": [
        DECAFBAD,
      ]
    }
  }
  groups = stethoscope.api.devices.group_devices([this, other, third])
  assert len(groups) == 1
  assert len(groups[0]) == 3
  assert this in groups[0]
  assert other in groups[0]
  assert third in groups[0]

  # order dependence bug
  groups = stethoscope.api.devices.group_devices([other, third, this])
  assert len(groups) == 1
  assert len(groups[0]) == 3
  assert this in groups[0]
  assert other in groups[0]
  assert third in groups[0]


def test_merge_identifiers():
  this = {
    "mac_addresses": [
      DEADBEEF,
      DECAFBAD,
    ],
    "serial": "0xDEADBEEF",
  }

  other = {
    "mac_addresses": [
      DEADBEEF,
    ],
    "serial": "0xDEADBEEF",
  }

  third = {
    "mac_addresses": [
      DECAFBAD,
    ]
  }

  merged = stethoscope.api.devices.merge_identifiers([other, third])
  assert len(merged) == 2
  assert merged['serial'] == this['serial']
  assert set(merged['mac_addresses']) == set(this['mac_addresses'])

  # duplicate identifiers
  merged = stethoscope.api.devices.merge_identifiers([this, third])
  assert len(merged) == 2
  assert merged['serial'] == this['serial']
  assert set(merged['mac_addresses']) == set(this['mac_addresses'])


def test_merge_device_group():
  alpha = {
    'practices': {
      'foo': {'status': 'unknown', 'last_updated': arrow.get(1)},
      'bar': {'status': 'warn', 'last_updated': arrow.get(5)},
    },
    'source': 'alpha',
    'last_sync': arrow.get(2),
  }
  bravo = {
    'practices': {
      'foo': {'status': 'warn', 'last_updated': arrow.get(5)},
      'bar': {'status': 'nudge', 'last_updated': arrow.get(1)},
    },
    'source': 'bravo',
    'last_sync': arrow.get(1),
  }

  merged = _copy_then_apply(stethoscope.api.devices.merge_device_group, [alpha, bravo])
  assert merged == {
    'sources': ['alpha', 'bravo'],
    'practices': {
      'foo': bravo['practices']['foo'],
      'bar': alpha['practices']['bar'],
    },
    'identifiers': {},
    'last_sync': arrow.get(2),
  }

  charlie = {
    'practices': {
      'baz': {'status': 'nudge'},
    },
    'source': 'charlie',
    '_raw': 'the raw data'
  }
  merged = _copy_then_apply(stethoscope.api.devices.merge_device_group, [alpha, bravo, charlie])
  assert merged == {
    'sources': ['alpha', 'bravo', 'charlie'],
    'practices': {
      'foo': bravo['practices']['foo'],
      'bar': alpha['practices']['bar'],
      'baz': charlie['practices']['baz'],
    },
    'identifiers': {},
    '_raw': [alpha, bravo, charlie],
    'last_sync': arrow.get(2),
  }


class MergePracticesByStatusOrder(unittest.TestCase):

  def merge(self, *values):
    return _copy_then_apply(stethoscope.api.devices.merge_practices, *values)

  def test_merge_practices(self):
    unknown = {'practice': {'status': 'unknown'}}
    nudge = {'practice': {'status': 'nudge'}}
    warn = {'practice': {'status': 'warn'}}
    assert self.merge(unknown, nudge) == \
        {'practice': {'status': 'nudge'}}
    assert self.merge({}, nudge) == \
        {'practice': {'status': 'nudge'}}
    assert self.merge(unknown, nudge, warn) == \
        {'practice': {'status': 'warn'}}

  def test_merge_multiple_practices(self):
    alpha = {
      'foo': {'status': 'unknown'},
      'bar': {'status': 'warn'},
    }
    bravo = {
      'foo': {'status': 'warn'},
      'bar': {'status': 'nudge'},
      'baz': {'status': 'unknown'},
    }
    assert self.merge(alpha, bravo) == {
      'foo': {'status': 'warn'},
      'bar': {'status': 'warn'},
      'baz': {'status': 'unknown'},
    }

    charlie = {
      'baz': {'status': 'nudge'},
    }
    assert self.merge(alpha, bravo, charlie) == {
      'foo': {'status': 'warn'},
      'bar': {'status': 'warn'},
      'baz': {'status': 'nudge'},
    }

  def test_merge_practices_raises_on_extra_kwargs(self):
    with pytest.raises(TypeError) as excinfo:
      stethoscope.api.devices.merge_practices(foo='bar', baz='qux')
    assert str(excinfo.value) in (
        "merge_practices() got unexpected keyword argument(s) 'foo', 'baz'",
        "merge_practices() got unexpected keyword argument(s) 'baz', 'foo'"
    )


class MergePracticesByLastUpdatedTime(unittest.TestCase):

  def merge(self, *values):
    return _copy_then_apply(stethoscope.api.devices.merge_practices_by_last_updated_time, *values)

  def test_merge_practices_by_last_updated_time(self):
    unknown = {'practice': {'status': 'unknown', 'last_updated': arrow.get(1)}}
    nudge = {'practice': {'status': 'nudge', 'last_updated': arrow.get(2)}}
    warn = {'practice': {'status': 'warn', 'last_updated': arrow.get(3)}}

    assert self.merge(unknown, nudge) == nudge
    assert self.merge({}, nudge) == nudge
    assert self.merge(unknown, nudge, warn) == warn

  def test_merge_multiple_practices(self):
    alpha = {
      'foo': {'status': 'unknown', 'last_updated': arrow.get(8)},
      'bar': {'status': 'warn', 'last_updated': arrow.get(10)},
    }
    bravo = {
      'foo': {'status': 'warn', 'last_updated': arrow.get(10)},
      'bar': {'status': 'nudge', 'last_updated': arrow.get(5)},
      'baz': {'status': 'unknown'},
    }
    assert self.merge(alpha, bravo) == {
      'foo': bravo['foo'],
      'bar': alpha['bar'],
      'baz': bravo['baz'],
    }

    charlie = {
      'baz': {'status': 'nudge', 'last_updated': arrow.get(1)},
    }
    assert self.merge(alpha, bravo, charlie) == {
      'foo': bravo['foo'],
      'bar': alpha['bar'],
      'baz': charlie['baz'],
    }
