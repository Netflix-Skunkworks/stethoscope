# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import json
import pprint

import arrow
import pytest

import stethoscope.api.exceptions
import stethoscope.api.utils
import stethoscope.plugins.sources.bitfit.deferred


@pytest.fixture(scope='module')
def raw_userinfo():
  with open("tests/fixtures/bitfit/userinfo_response.json") as fo:
    data = json.load(fo)
  return data


@pytest.fixture(scope='function')
def mock_datasource():
  return stethoscope.plugins.sources.bitfit.deferred.DeferredBitfitDataSource({
    'BITFIT_API_TOKEN': '',
    'BITFIT_BASE_URL': '',
    'DEBUG': True,
  })


def test_process_userinfo_exists(raw_userinfo, mock_datasource):
  userinfo = mock_datasource._process_userinfo(raw_userinfo, 'fry@planetexpress.com')
  pprint.pprint(userinfo)
  assert userinfo['email'] == 'fry@planetexpress.com'
  assert userinfo['id'] == 12345
  assert userinfo['full_name'] == 'Phillip J. Fry'


def test_process_userinfo_does_not_exist(raw_userinfo, mock_datasource):
  pprint.pprint(raw_userinfo)
  with pytest.raises(stethoscope.api.exceptions.NotFoundException) as exc:
    mock_datasource._process_userinfo(raw_userinfo, 'brannigan@planetexpress.com')
  assert "user ('brannigan@planetexpress.com') not found" in str(exc.value)


@pytest.fixture(params=['lgml-pfry', 'lgmd-pfry', 'frys-laptop'], scope='module')
def asset_response(request):
  with open("tests/fixtures/bitfit/asset_response_{:s}.json".format(request.param)) as fo:
    data = json.load(fo)
  return data


def test_process_device(asset_response, mock_datasource):
  device = mock_datasource._process_device(asset_response)

  # Ensure returned info has at least these keys
  pprint.pprint(device)
  keys = [
    'model',
    'name',
    'serial',
    'source',
    'type',
    'photo_url',
  ]
  for key in keys:
    assert key in device


@pytest.fixture(params=["lgml-pfry", "lgmd-pfry", "frys-laptop"], scope='module')
def processed_device(request, mock_datasource):
  return mock_datasource._process_device(asset_response(request))


@pytest.mark.parametrize(['processed_device'], [('lgmd-pfry',)], indirect=['processed_device'])
def test_process_lgmd_pfry(processed_device):
  pprint.pprint(processed_device)
  assert processed_device['name'] == 'lgmd-pfry'
  assert processed_device['serial'] == 'DECAFBAD01'
  assert processed_device['source'] == 'bitfit'
  assert processed_device['type'] == 'Workstation'
  assert processed_device['hw_release_date'] == arrow.get('2013-10-22')

  assert '00:DE:CA:FB:AD:02' in processed_device['identifiers']['mac_addresses']
  assert '00:DE:CA:FB:AD:03' in processed_device['identifiers']['mac_addresses']
  assert processed_device['identifiers']['udid'] == "DECAFBAD-DECA-FBAD-DECA-FBAD00000001"


@pytest.mark.parametrize(['processed_device'], [('lgml-pfry',)], indirect=['processed_device'])
def test_process_lgml_pfry(processed_device):
  pprint.pprint(processed_device)
  assert processed_device['name'] == 'lgml-pfry'
  assert processed_device['serial'] == 'DECAFBAD00'
  assert processed_device['source'] == 'bitfit'
  assert processed_device['type'] == 'Laptop'
  assert processed_device['hw_release_date'] == arrow.get('2013-10-22')

  assert '00:DE:CA:FB:AD:00' in processed_device['identifiers']['mac_addresses']
  assert '00:DE:CA:FB:AD:01' in processed_device['identifiers']['mac_addresses']
  assert processed_device['identifiers']['udid'] == "DECAFBAD-DECA-FBAD-DECA-FBAD00000000"


@pytest.mark.parametrize(['processed_device'], [('frys-laptop',)], indirect=['processed_device'])
def test_process_frys_laptop(processed_device):
  pprint.pprint(processed_device)
  assert processed_device['name'] == "Fry’s MacBook Pro"
  assert processed_device['serial'] == 'DECAFBAD02'
  assert processed_device['source'] == 'bitfit'
  # 'type' is in a different place in this record
  assert processed_device['type'] == 'Laptop'

  assert '00:DE:CA:FB:AD:04' in processed_device['identifiers']['mac_addresses']
  assert '00:DE:CA:FB:AD:05' in processed_device['identifiers']['mac_addresses']
  assert processed_device['identifiers']['udid'] == "DECAFBAD-DECA-FBAD-DECA-FBAD00000002"
