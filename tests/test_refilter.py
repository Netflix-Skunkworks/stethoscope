# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import pytest

import stethoscope.plugins.transform.refilter


@pytest.fixture(scope='module')
def datasource():
  return stethoscope.plugins.transform.refilter.FilterMatching({
    'PATTERN_MAP': {
      'model': '(Virtual Machine|VMware|amazon|HVM domU)',
      'serial': '(Parallels|VMware)',
    },
  })


@pytest.fixture(scope='function')
def devices():
  return [
    ({'model': 'HVM domU'}, True),
    ({'model': 'Virtual Machine'}, True),
    ({'serial': 'VMware-DE CA FB AD'}, True),
    ({'serial': 'Parallels-DE CA FB AD'}, True),
    ({'model': 'should not match'}, False),
  ]


@pytest.mark.parametrize("device,expected", devices())
def test_match(datasource, device, expected):
  assert datasource.matches(device) == expected


def test_transform(datasource, devices):
  expected = [device for device, exp in devices if not exp]
  assert datasource.transform(device for device, _ in devices) == expected
