# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import itertools
import json
import pprint

from twisted.internet import defer
import logbook
import mock
import pytest

import stethoscope.api.devices
import stethoscope.api.factory
import stethoscope.plugins.sources.bitfit.deferred
import stethoscope.plugins.sources.jamf.deferred


logger = logbook.Logger(__name__)


@pytest.fixture
def jamf_datasource():
  return stethoscope.plugins.sources.jamf.deferred.DeferredJAMFDataSource({
    'JAMF_API_USERNAME': '',
    'JAMF_API_PASSWORD': '',
    'JAMF_API_HOSTADDR': '',
    'DEBUG': True,
  })


@pytest.fixture
def jamf_devices(jamf_datasource):
  devices = list()
  for device in ["lgml-pfry", "lgmd-pfry"]:
    with open("tests/fixtures/jamf/{:s}.json".format(device)) as fo:
      devices.append(jamf_datasource._process_device(json.load(fo)))
  return devices


@pytest.fixture
def bitfit_datasource():
  return stethoscope.plugins.sources.bitfit.deferred.DeferredBitfitDataSource({
    'BITFIT_API_TOKEN': '',
    'BITFIT_BASE_URL': '',
    'DEBUG': True,
  })


@pytest.fixture
def bitfit_devices(bitfit_datasource):
  devices = list()
  for device in ["lgml-pfry", "lgmd-pfry"]:
    with open("tests/fixtures/bitfit/asset_response_{:s}.json".format(device)) as fo:
      devices.append(bitfit_datasource._process_device(json.load(fo)))
  return devices


@pytest.fixture
def all_devices(jamf_devices, bitfit_devices):
  return list(itertools.chain(jamf_devices, bitfit_devices))


def check_merge_devices(devices):
  logger.debug("identifiers returned:\n{:s}", pprint.pformat([device['identifiers'] for device in
    devices]))
  # logger.debug("devices:\n{:s}", pprint.pformat(devices))

  # check serials recognized and merged upon
  assert set(dev['serial'] for dev in devices) == set(['DECAFBAD00', 'DECAFBAD01'])

  assert len(devices) == 2

  # check keywords are present
  for device in devices:
    for kw in ['name', 'practices', 'sources', 'platform']:
      assert kw in device

  # check sources merged
  for device in devices:
    assert set(device['sources']) == set(['bitfit', 'jamf'])


def test_merge_devices(all_devices):
  check_merge_devices(stethoscope.api.devices.merge_devices(all_devices))


@pytest.fixture
def mock_jamf_ext(jamf_devices):
  ext = mock.Mock()
  ext.obj = mock.create_autospec(stethoscope.plugins.sources.jamf.deferred.DeferredJAMFDataSource)
  ext.obj.get_devices_by_email.return_value = defer.succeed(jamf_devices)
  ext.obj.get_devices_by_serial.return_value = defer.succeed(jamf_devices)
  ext.obj.get_devices_by_macaddr.return_value = defer.succeed(jamf_devices)
  ext.name = 'jamf'
  return ext


@pytest.fixture
def mock_bitfit_ext(bitfit_devices):
  ext = mock.Mock()
  ext.obj = mock.create_autospec(stethoscope.plugins.sources.jamf.deferred.DeferredJAMFDataSource)
  ext.obj.get_devices_by_email.return_value = defer.succeed(bitfit_devices)
  ext.obj.get_devices_by_serial.return_value = defer.succeed(bitfit_devices)
  ext.obj.get_devices_by_macaddr.return_value = defer.succeed(bitfit_devices)
  ext.name = 'bitfit'
  return ext


@pytest.fixture
def mock_failure_ext():
  ext = mock.Mock()
  ext.obj = mock.create_autospec(stethoscope.plugins.sources.jamf.deferred.DeferredJAMFDataSource)
  ext.obj.get_devices_by_email.return_value = defer.fail(Exception())
  ext.obj.get_devices_by_serial.return_value = defer.fail(Exception())
  ext.obj.get_devices_by_macaddr.return_value = defer.fail(Exception())
  ext.name = 'failure'
  return ext


@pytest.fixture
def mock_sources(mock_jamf_ext, mock_bitfit_ext, mock_failure_ext):
  return [mock_jamf_ext, mock_bitfit_ext, mock_failure_ext]


def test_get_devices_by_email(mock_sources):
  deferred = stethoscope.api.factory.get_devices_by_email(None, mock_sources)
  deferred.addCallback(stethoscope.api.devices.merge_devices)
  deferred.addCallback(check_merge_devices)
  return deferred


def test_get_devices_by_serial(mock_sources):
  deferred = stethoscope.api.factory.get_devices_by_serial(None, mock_sources)
  deferred.addCallback(stethoscope.api.devices.merge_devices)
  deferred.addCallback(check_merge_devices)
  return deferred


def test_get_devices_by_macaddr(mock_sources):
  deferred = stethoscope.api.factory.get_devices_by_macaddr(None, mock_sources)
  deferred.addCallback(stethoscope.api.devices.merge_devices)
  deferred.addCallback(check_merge_devices)
  return deferred


def test_get_devices_by_stages(mock_bitfit_ext, mock_jamf_ext):
  deferred = stethoscope.api.factory.get_devices_by_stages(None, [mock_bitfit_ext],
      [mock_jamf_ext])
  deferred.addCallback(stethoscope.api.devices.merge_devices)
  deferred.addCallback(check_merge_devices)
  return deferred
