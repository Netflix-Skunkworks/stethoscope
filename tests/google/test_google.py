# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import pprint

import arrow
import logbook
import pytest


logger = logbook.Logger(__name__)


@pytest.mark.parametrize(['raw_device'], [('ios_google-sync',)], indirect=['raw_device'])
def test_process_device_ios_googlesync(raw_device, mock_datasource):
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

  assert device['identifiers']['google_device_id'] == 'exampleGoogleDeviceId'


@pytest.mark.parametrize(['raw_device'], [('android',)], indirect=['raw_device'])
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


@pytest.mark.parametrize(['raw_device'], [('android_oreo',)], indirect=['raw_device'])
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
    [
      ('chromeos', 'Verified', True),
      ('chromeos', 'Validated', True),
      ('chromeos', 'validated', True),
      ('chromeos', 'unknown', False),
      ('chromeos', 'dev', False),
    ],
    indirect=['raw_device']
)
def test_process_device_chromeos_bootmode(raw_device, boot_mode, value, mock_datasource):
  raw_device['bootMode'] = boot_mode
  device = mock_datasource._process_chromeos_device(raw_device)
  pprint.pprint(device)

  last_updated = arrow.get('2017-10-04T20:31:26.258Z')
  assert device['practices']['jailed'] == {
    'value': value,
    'last_updated': last_updated,
  }


@pytest.mark.parametrize(
    ['raw_device', 'expected'],
    [
      ('chromeos', 'Samsung Chromebook Pro'),
      ('chromeos_pixelbook', None)
    ],
    indirect=['raw_device']
)
def test_process_device_chromeos_model(raw_device, expected, mock_datasource):
  device = mock_datasource._process_chromeos_device(raw_device)
  pprint.pprint(device)
  if expected is None:
    assert 'model' not in device
  else:
    assert device['model'] == expected
