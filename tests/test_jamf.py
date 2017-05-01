# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import json

import arrow
import pprint
import pytest
import six

import stethoscope.plugins.sources.jamf.deferred


@pytest.fixture
def userinfo(scope='module'):
  return json.loads('''{
  "user":{
    "id":300,
    "name":"pfry",
    "full_name":"Phillip J Fry",
    "email":"fry@planetexpress.com",
    "position":"Delivery Associate",
    "links":{
      "computers":[
        {"id":3001,"name":"lgmd-pfry"},
        {"id":3002,"name":"lgml-pfry"}
      ]
    }
  }
}''')


@pytest.fixture(scope='function')
def mock_datasource():
  return stethoscope.plugins.sources.jamf.deferred.DeferredJAMFDataSource({
    'JAMF_API_USERNAME': '',
    'JAMF_API_PASSWORD': '',
    'JAMF_API_HOSTADDR': '',
    'DEBUG': True,
  })


def test_extract_device_ids(userinfo, mock_datasource):
  assert [3001, 3002] == mock_datasource._extract_device_ids_from_userinfo(userinfo)


@pytest.fixture(params=["lgml-pfry", "lgmd-pfry"], scope='module')
def raw_device(request):
  with open("tests/fixtures/jamf/{:s}.json".format(request.param)) as fo:
    data = json.load(fo)
  return data


@pytest.fixture(params=["lgml-pfry", "lgmd-pfry"], scope='function')
def device(request, mock_datasource):
  return mock_datasource._process_device(raw_device(request))


def test_process_basic_information_sanity_checks(device):
  pprint.pprint(device)

  for key in [
    'model',
    'name',
    'platform',
    'serial',
    'source',
    'last_sync',
    'software',
  ]:
    assert key in device

  assert isinstance(device['last_sync'], arrow.Arrow)

  assert device['source'] == 'jamf'


@pytest.mark.parametrize(['device'], [('lgml-pfry',)], indirect=['device'])
def test_process_basic_information_lgml_pfry(device):
  pprint.pprint(device)

  assert device['model'] == '15-inch Retina MacBook Pro (Late 2013)'
  assert device['name'] == 'lgml-pfry'
  assert device['platform'] == 'Mac'
  assert device['serial'] == 'DECAFBAD00'
  assert device['last_sync'].to('utc') == arrow.get('2016-02-26T10:58:57.853-0800')

  for key, value in six.iteritems({
    'serial': 'DECAFBAD00',
    'udid': 'DECAFBAD-DECA-FBAD-DECA-FBAD00000000',
  }):
    assert device['identifiers'][key] == value

  mac_addresses = [
    'DE:CA:FB:AD:00:01',
    'DE:CA:FB:AD:00:00',
  ]
  assert set(device['identifiers']['mac_addresses']) == set(mac_addresses)

  assert device['source'] == 'jamf'


@pytest.mark.parametrize(['device'], [('lgmd-pfry',)], indirect=['device'])
def test_process_basic_information_lgmd_pfry(device):
  pprint.pprint(device)

  assert device['platform'] == 'Mac'
  assert device['model'] == 'MacPro (Late 2013)'
  assert device['name'] == 'lgmd-pfry'
  assert device['serial'] == 'DECAFBAD01'
  assert device['last_sync'].to('utc') == arrow.get('2016-02-28T14:54:40.788-0800')

  for key, value in six.iteritems({
    'serial': 'DECAFBAD01',
    'udid': 'DECAFBAD-DECA-FBAD-DECA-FBAD00000001',
  }):
    assert device['identifiers'][key] == value

  mac_addresses = [
    'DE:CA:FB:AD:00:02',
    'DE:CA:FB:AD:00:03',
  ]
  assert set(device['identifiers']['mac_addresses']) == set(mac_addresses)

  assert device['source'] == 'jamf'
