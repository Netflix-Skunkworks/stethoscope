# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import json
import pprint

import arrow
import pytest

import stethoscope.plugins.sources.google.deferred


@pytest.fixture(scope='module')
def raw_devices():
  with open("tests/fixtures/google/list-devices_response.json") as fo:
    data = json.load(fo)
  return data


@pytest.fixture(params=[0, 1], scope='module')
def raw_device(request, raw_devices):
  return raw_devices[request.param]


@pytest.fixture(scope='function')
def mock_datasource():
  return stethoscope.plugins.sources.google.deferred.DeferredGoogleDataSource({
    'GOOGLE_API_SECRETS': '',
    'GOOGLE_API_USERNAME': '',
    'GOOGLE_API_SCOPES': '',
    'DEBUG': True,
  })


@pytest.mark.parametrize(['raw_device'], [(0,)], indirect=['raw_device'])
def test_process_device_ios(raw_device, mock_datasource):
  device = mock_datasource._process_mobile_device(raw_device)
  pprint.pprint(device)
  assert device['practices']['jailed'] == {
    'last_updated': arrow.get('2016-03-24T01:42:02.702000+00:00'),
  }

  assert device['source'] == 'google'
  assert device['type'] == 'Mobile Device'
  assert device['platform'] == 'iOS'
  assert device['model'] == 'iPad Mini Retina'
  assert device['os'] == 'iOS'
  # assert device['os_version'] == '9.3'
  assert device['last_sync'].to('utc') == arrow.get('2016-03-24T01:42:02.702Z')


@pytest.mark.parametrize(['raw_device'], [(1,)], indirect=['raw_device'])
def test_process_device_android(raw_device, mock_datasource):
  device = mock_datasource._process_mobile_device(raw_device)
  pprint.pprint(device)
  assert device['practices']['jailed'] == {
    'value': True,
    'last_updated': arrow.get('2016-02-23T21:49:14.719000+00:00'),
  }

  assert device['practices']['encryption'] == {
    'value': True,
    'last_updated': arrow.get('2016-02-23T21:49:14.719000+00:00'),
  }

  assert device['source'] == 'google'
  assert device['type'] == 'Mobile Device'
  assert device['platform'] == 'Android'
  assert device['model'] == 'SAMSUNG-SM-G925A'
  assert device['os'] == 'Android'
  assert device['os_version'] == '5.1.1'
  assert device['last_sync'].to('utc') == arrow.get('2016-02-23T21:49:14.719Z')
