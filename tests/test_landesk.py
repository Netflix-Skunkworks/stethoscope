# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import datetime

import arrow
import pytest

import stethoscope.plugins.sources.landesk.base
import stethoscope.plugins.sources.landesk.deferred


@pytest.fixture(scope='module')
def adapters():
  return [
    {
      "FirewallEnabled": "Not Installed",
      "PhysAddress": "00:00:DE:CA:FB:AD",
    },
    {
      "FirewallEnabled": "No",
      "PhysAddress": "0000F005BA11",
    },
    {
      "FirewallEnabled": "Yes",
      "PhysAddress": "000000DDBA11",
    },
  ]


@pytest.fixture(scope='module')
def vulns():
  return [
    {
      "Vul_ID": "JAVAv8u92",
      "VulSeverity": "Critical",
      "VulType": "Vulnerability",
      "Title": "Java SE Runtime Environment 8 Update 92 (JRE 8u92)"
    },
    {
      "Vul_ID": "ST000202",
      "VulSeverity": "High",
      "VulType": "Security Threat",
      "Reason": "The screen saver is not enabled for user zoidberg.",
      "Title": "Screen Saver with Password enabled setting check",
    },
  ]


@pytest.fixture(scope='module')
def software():
  return {
    'BIG-IP Edge Client': {'install_date': '20161019',
                          'name': 'BIG-IP Edge Client',
                          'publisher': 'F5 Networks, Inc.',
                          'version': '71.2016.0603.0048'},
    'Carbon Black Sensor': {'install_date': None,
                            'name': 'Carbon Black Sensor',
                            'publisher': 'Carbon Black, Inc.',
                            'version': '6.0.061114'},
    'Sentinel Agent': {'install_date': '20161004',
                       'name': 'Sentinel Agent',
                       'publisher': 'SentinelOne',
                       'version': '1.6.2.5020'},
  }


@pytest.fixture(scope='module')
def raw_row():
  return {
    "0": "LGWL-ZOIDBERG",
    "1": "{DECAFBAD-DECA-FBAD-DECA-FBADDECAFBAD}",
    "10": 100,
    "11": "Yes",
    "12": "Yes",
    "13": "Microsoft Windows 10 Professional Edition, 64-bit",
    "2": "2016-04-27T08:14:34",
    "3": 12345,
    "4": "Portable",
    "5": "0xDECAFBAD",
    "6": "ThinkPad T450s",
    "7": "1 - on",
    "8": "1 - fully encrypted",
    "9": "6 - unknown",
    "CONVERSIONSTATUS": "1 - fully encrypted",
    "Computer_Idn": 12345,
    "DEVICEID": "{DECAFBAD-DECA-FBAD-DECA-FBADDECAFBAD}",
    "ENCRYPTIONPERCENTAGE": 100,
    "GENENCRYPT": "6 - unknown",
    "PROTECTIONSTATUS": "1 - on",
    "TPMACTIVE": "Yes",
    "TPMENABLE": "Yes",
    "last_seen": datetime.datetime(2016, 6, 3, 14, 35, 13),
    "sw_last_scan_date": datetime.datetime(2016, 6, 2, 14, 44, 39),
    "hw_last_scan_date": datetime.datetime(2016, 6, 3, 14, 34, 59),
    "model": "ThinkPad T450s",
    "name": "LGWL-ZOIDBERG",
    "os": "Microsoft Windows 10 Professional Edition, 64-bit",
    "serial": "0xDECAFBAD",
    "type": "Portable"
  }


@pytest.fixture(scope='module')
def raw_dict(raw_row, adapters, vulns, software):
  d = stethoscope.plugins.sources.landesk.base.row_to_dict(raw_row)
  d["adapters"] = adapters
  d["vulns"] = vulns
  d["software"] = software
  return d


@pytest.fixture(scope='module')
def mock_datasource():
  return stethoscope.plugins.sources.landesk.deferred.DeferredLandeskSQLDataSource({
    'LANDESK_SQL_USERNAME': '',
    'LANDESK_SQL_PASSWORD': '',
    'LANDESK_SQL_HOSTNAME': '',
    'LANDESK_SQL_HOSTPORT': 12345,
    'LANDESK_SQL_DATABASE': '',
    'DEBUG': True,
    'TESTING': True,
  })


def check_processed_device(device):
  keys = [
    'model',
    'name',
    'serial',
    'source',
    'type',
    'last_sync',
  ]
  for key in keys:
    assert key in device

  assert isinstance(device['last_sync'], arrow.Arrow)
  assert device['serial'] == '0xDECAFBAD'
  assert device['source'] == 'landesk'


def test_process_device(raw_dict, mock_datasource):
  check_processed_device(mock_datasource._process_device(raw_dict))


# def test_get_devices_by_email(raw_row, mock_datasource):
#   conn = mock.Mock(side_effect=[raw_row, None, adapters, None, vulns])
#   returned = mock_datasource.get_devices_by_email(conn)
#   assert returned['serial'] == '0xDECAFBAD'
