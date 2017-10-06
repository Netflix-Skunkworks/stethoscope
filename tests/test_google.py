# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import copy
import json
import pprint

import arrow
import pytest

import stethoscope.plugins.sources.google.deferred


@pytest.fixture(scope='module')
def raw_devices():
  with open("tests/fixtures/google/list-devices_response.json") as fo:
    data = json.load(fo)
  with open("tests/fixtures/google/list-devices_response_oreo.json") as fo:
    data.extend(json.load(fo))
  return data


@pytest.fixture(params=[0, 1], scope='function')
def raw_device(request, raw_devices):
  return copy.deepcopy(raw_devices[request.param])


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

  last_updated = arrow.get('2016-03-24T01:42:02.702000+00:00')

  assert device['practices']['jailed'] == {
    'last_updated': last_updated,
  }

  assert device['practices']['unknownsources'] == {
    'value': True,
    'last_updated': last_updated,
  }

  assert device['practices']['adbstatus'] == {
    'value': True,
    'last_updated': last_updated,
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

  last_updated = arrow.get('2016-02-23T21:49:14.719000+00:00')

  assert device['practices']['jailed'] == {
    'value': True,
    'last_updated': last_updated,
  }

  assert device['practices']['encryption'] == {
    'value': True,
    'last_updated': last_updated,
  }

  assert device['practices']['unknownsources'] == {
    'value': False,
    'last_updated': last_updated,
  }

  assert device['practices']['adbstatus'] == {
    'value': False,
    'last_updated': last_updated,
  }

  assert device['source'] == 'google'
  assert device['type'] == 'Mobile Device'
  assert device['platform'] == 'Android'
  assert device['model'] == 'SAMSUNG-SM-G925A'
  assert device['os'] == 'Android'
  assert device['os_version'] == '5.1.1'
  assert device['last_sync'].to('utc') == arrow.get('2016-02-23T21:49:14.719Z')


@pytest.mark.parametrize(['raw_device'], [(-1,)], indirect=['raw_device'])
def test_process_device_android_oreo(raw_device, mock_datasource):
  device = mock_datasource._process_mobile_device(raw_device)
  pprint.pprint(device)

  last_updated = arrow.get('2017-10-06T16:06:52.071Z')

  assert device['practices']['jailed'] == {
    'value': True,
    'last_updated': last_updated,
  }

  assert device['practices']['encryption'] == {
    'value': True,
    'last_updated': last_updated,
  }

  # Oreo has no system-level setting for unknown sources
  assert 'unknownsources' not in device['practices']

  assert device['practices']['adbstatus'] == {
    'value': True,
    'last_updated': last_updated,
  }

  assert device['source'] == 'google'
  assert device['type'] == 'Mobile Device'
  assert device['platform'] == 'Android'
  assert device['model'] == 'Pixel XL'
  assert device['os'] == 'Android'
  assert device['os_version'] == '8.0.0'
  assert device['last_sync'].to('utc') == last_updated


@pytest.mark.parametrize(
    ['raw_device', 'boot_mode', 'value'],
    [(1, 'Verified', True), (1, 'Validated', True), (1, 'validated', True), (1, 'unknown', False)],
    indirect=['raw_device']
)
def test_process_device_android_case_insensitive(raw_device, boot_mode, value, mock_datasource):
  # pretend device 1 is ChromeOS device
  del raw_device['deviceCompromisedStatus']
  raw_device['bootMode'] = boot_mode
  device = mock_datasource._process_chromeos_device(raw_device)
  pprint.pprint(device)

  last_updated = arrow.get('2016-02-23T21:49:14.719000+00:00')
  assert device['practices']['jailed'] == {
    'value': value,
    'last_updated': last_updated,
  }
