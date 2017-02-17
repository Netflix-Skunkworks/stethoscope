# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import pprint

import _mssql
import arrow
import logbook
import six

import stethoscope.api.exceptions
import stethoscope.validation
import stethoscope.configurator


logger = logbook.Logger(__name__)

#                A4.TPMENABLE,
#                A4.TPMACTIVE,
# LEFT OUTER JOIN TPMSystem A4 (nolock) ON A0.Computer_Idn = A4.Computer_Idn

DEVICES_FOR_USER = """
SELECT DISTINCT A0.DISPLAYNAME AS name,
                A0.DEVICEID,
                A0.LASTUPDINVSVR AS last_seen,
                A0.HWLASTSCANDATE AS hw_last_scan_date,
                A0.SWLASTSCANDATE AS sw_last_scan_date,
                A0.Computer_Idn,
                A0.TYPE AS type,
                A2.SERIALNUM AS serial,
                A2.SYSTEMVERSION AS model,
                A3.PROTECTIONSTATUS,
                A3.CONVERSIONSTATUS,
                A3.GENENCRYPT,
                A3.ENCRYPTIONPERCENTAGE,
                A5.OSTYPE AS os
FROM Computer A0 (nolock)
LEFT OUTER JOIN LDAPUserAttrV A1 (nolock) ON A0.Computer_Idn = A1.Computer_Idn
LEFT OUTER JOIN CompSystem A2 (nolock) ON A0.Computer_Idn = A2.Computer_Idn
LEFT OUTER JOIN BitLocker A3 (nolock) ON A0.Computer_Idn = A3.Computer_Idn
LEFT OUTER JOIN Operating_System A5 (nolock) ON A0.Computer_Idn = A5.Computer_Idn
{:s}
ORDER BY A0.LASTUPDINVSVR DESC
"""


ATTRIBUTES_TO_COPY = [
    'name',
    'model',
    'os',
    'serial',
    'type',
]


def row_to_dict(row):
  """Convert a `pymssql` row object into a normal dictionary (removing integer keys).

  >>> returned = row_to_dict({1: 'foo', 'one': 'foo', 2: 'bar', 'two': 'bar'})
  >>> returned == {'one': 'foo', 'two': 'bar'}
  True

  """
  retval = dict()
  for key, value in six.iteritems(row):
    if not isinstance(key, int):
      retval[key] = value
  return retval


class LandeskSQLDataSourceBase(stethoscope.configurator.Configurator):

  config_keys = (
      'LANDESK_SQL_USERNAME',
      'LANDESK_SQL_PASSWORD',
      'LANDESK_SQL_HOSTNAME',
      'LANDESK_SQL_HOSTPORT',
      'LANDESK_SQL_DATABASE',
  )

  def __init__(self, *args, **kwargs):
    super(LandeskSQLDataSourceBase, self).__init__(*args, **kwargs)

    self._conn_kwargs = {
      'server': '{:s}:{:d}'.format(self.config['LANDESK_SQL_HOSTNAME'],
        self.config['LANDESK_SQL_HOSTPORT']),
      'user': self.config['LANDESK_SQL_USERNAME'],
      'password': self.config['LANDESK_SQL_PASSWORD'],
      'database': self.config['LANDESK_SQL_DATABASE'],
    }

  def _get_vulnerabilities(self, conn, computer_id):
    conn.execute_query("""SELECT * FROM CVDetectedV (nolock) WHERE Computer_Idn = %d""",
        computer_id)
    return [row_to_dict(row) for row in conn]

  def _get_adapters(self, conn, computer_id):
    # NOTE: firewall information is also stored with network adapters
    conn.execute_query("""SELECT * FROM BoundAdapter (nolock) WHERE Computer_Idn = %d""",
        computer_id)
    return [row_to_dict(row) for row in conn]

  def _normalize_software_row(self, row):
    """Convert row of software information returned from DB to common software list format."""
    return {
      'version': row['Version'],
      'publisher': row['Publisher'],
      'install_date': row['InstallDate'],
      'name': row['SuiteName'],
    }

  def _get_software(self, conn, computer_id):
    """Use our SQL connection to get the list of installed software given the computer ID."""
    conn.execute_query("""SELECT DISTINCT InstallDate, Publisher, SuiteName, Version
                          FROM AppSoftwareSuites (nolock)
                          WHERE Computer_Idn = %d""", computer_id)
    return dict((row['SuiteName'], self._normalize_software_row(row)) for row in conn)

  def _check_screenlock(self, raw):
    data = {'value': True}

    for vuln in raw['vulns']:
      if vuln['Vul_ID'] == 'ST000202':
        data['value'] = False
        data['details'] = vuln['Reason']

    if raw.get('sw_last_scan_date') is not None:
      data['last_updated'] = arrow.get(raw['sw_last_scan_date'], 'US/Pacific')

    return data

  def _check_autoupdate(self, raw):
    data = {'value': True}

    for vuln in raw['vulns']:
      if vuln['Vul_ID'] == 'ST000003v2':
        data['value'] = False
        data['details'] = vuln['Reason']

    if raw.get('sw_last_scan_date') is not None:
      data['last_updated'] = arrow.get(raw['sw_last_scan_date'], 'US/Pacific')

    return data

  def _check_uptodate(self, raw):
    vulns = [vuln for vuln in raw['vulns'] if
        # not vuln['Vul_ID'].startswith('AV-') and
        vuln['VulType'] == 'Vulnerability' and
        vuln['VulSeverity'] in ('Critical', 'High')]

    data = {'value': (len(vulns) == 0)}
    if len(vulns) > 0:
      data['details'] = "Missing Updates:\n"
      for vuln in vulns:
        data['details'] += "    {Title!s}\n".format(**vuln)

    if raw.get('sw_last_scan_date') is not None:
      data['last_updated'] = arrow.get(raw['sw_last_scan_date'], 'US/Pacific')

    return data

  def _check_encryption(self, raw):
    data = {'value': (raw['ENCRYPTIONPERCENTAGE'] == 100) and (raw['PROTECTIONSTATUS'] == '1 - on')}

    if raw['ENCRYPTIONPERCENTAGE'] is not None:
      data['details'] = (
        "  Protection Status: {PROTECTIONSTATUS!s}\n"
        "  Encryption Percentage: {ENCRYPTIONPERCENTAGE!s}\n"
        "  Conversion Status: {CONVERSIONSTATUS!s}\n"
        "  Encryption Method: {GENENCRYPT!s}\n"
      ).format(**raw)

    if raw.get('hw_last_scan_date') is not None:
      data['last_updated'] = arrow.get(raw['hw_last_scan_date'], 'US/Pacific')

    return data

  def _check_firewall(self, raw):
    # adapter information: MACs and firewall determination
    data = {'value': True}

    details = list()
    for adapter in raw['adapters']:
      if adapter['FirewallEnabled'] == 'No':
        data['value'] = False
        try:
          name = stethoscope.validation.canonicalize_macaddr(adapter['PhysAddress'])
        except:
          name = 'unknown'
        details.append("Firewall not enabled for adapter '{!s}'".format(name))
    data['details'] = '\n'.join(details)

    if raw.get('hw_last_scan_date') is not None:
      data['last_updated'] = arrow.get(raw['hw_last_scan_date'], 'US/Pacific')

    return data

  def _process_device(self, raw):
    device = {'_raw': raw} if self._debug else {}
    # logger.debug("raw: {:s}", pprint.pformat(raw))

    # INFORMATION
    for attr in ATTRIBUTES_TO_COPY:
      if raw.get(attr) is not None:
        device[attr] = raw[attr]

    if raw.get('last_seen') is not None:
      device['last_sync'] = arrow.get(raw['last_seen'], 'US/Pacific')

    # SOFTWARE
    device['software'] = {'installed': raw['software']}
    if raw.get('sw_last_scan_date') is not None:
      device['software']['last_scan_date'] = arrow.get(raw['sw_last_scan_date'], 'US/Pacific')

    # PRACTICES
    device['practices'] = dict()
    device['practices']['screenlock'] = self._check_screenlock(raw)
    device['practices']['autoupdate'] = self._check_autoupdate(raw)
    device['practices']['uptodate'] = self._check_uptodate(raw)
    device['practices']['encryption'] = self._check_encryption(raw)
    device['practices']['firewall'] = self._check_firewall(raw)

    # IDENTIFIERS
    device['identifiers'] = {
        'mac_addresses': [stethoscope.validation.canonicalize_macaddr(adapter['PhysAddress'])
          for adapter in raw['adapters'] if adapter['FirewallEnabled'] != 'Not Installed']
    }
    if device.get('serial') is not None:
      device['identifiers']['serial'] = device['serial']

    device['platform'] = 'Windows'
    device['source'] = 'landesk'

    # logger.debug("device: {:s}", pprint.pformat(device))
    return device

  def get_devices_by_serial(self, serial):
    with _mssql.connect(**self._conn_kwargs) as conn:
      conn.execute_query(DEVICES_FOR_USER.format("WHERE A2.SERIALNUM = %s"), serial)
      devices = self._get_devices_by_email(conn)
      if len(devices) == 0:
        raise stethoscope.api.exceptions.DeviceNotFoundException("serial: '{!s}'".format(serial),
            'landesk')
      return devices

  def get_devices_by_macaddr(self, _addr):
    addr = _addr.upper().replace(':', '')  # landesk uses all-uppercase MACs with no delimiters
    with _mssql.connect(**self._conn_kwargs) as conn:
      conn.execute_query("""SELECT Computer_Idn FROM BoundAdapter WHERE PhysAddress = %s""", addr)
      rows = [row_to_dict(row) for row in conn]
      if len(rows) == 0:
        raise stethoscope.api.exceptions.DeviceNotFoundException("macaddr: '{!s}'".format(_addr),
            'landesk')

      idn = rows[0]['Computer_Idn']
      conn.execute_query(DEVICES_FOR_USER.format("WHERE A0.Computer_Idn = %d"), idn)
      devices = self._get_devices_by_email(conn)
      if len(devices) == 0:
        raise stethoscope.api.exceptions.DeviceNotFoundException("idn: '{!s}'".format(idn),
            'landesk')
      return devices

  def _get_devices_by_email(self, conn):
    devices = list()
    for row in conn:
      raw = row_to_dict(row)
      raw['vulns'] = self._get_vulnerabilities(conn, row['Computer_Idn'])
      raw['adapters'] = self._get_adapters(conn, row['Computer_Idn'])
      raw['software'] = self._get_software(conn, row['Computer_Idn'])
      logger.debug("software:\n{!s}", pprint.pformat(raw['software']))
      devices.append(self._process_device(raw))
    return devices

  def get_devices_by_email(self, email):
    with _mssql.connect(**self._conn_kwargs) as conn:
      conn.execute_query(DEVICES_FOR_USER.format("WHERE A1.EMAILADDR = %s"), email)
      return self._get_devices_by_email(conn)
