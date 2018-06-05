# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import collections
import re

import _mssql
import arrow
import logbook
import six

import stethoscope.api.exceptions
import stethoscope.configurator
import stethoscope.utils
import stethoscope.validation


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
                A1.EMAILADDR AS email,
                A2.MODEL AS model,
                A2.MANUFACTURER AS manufacturer,
                A2.SERIALNUM AS serial,
                A2.SYSTEMVERSION AS systemversion,
                A3.PROTECTIONSTATUS,
                A3.CONVERSIONSTATUS,
                A3.GENENCRYPT,
                A3.ENCRYPTIONPERCENTAGE,
                A4.CURRENTBUILD AS os_build,
                A4.CURRENTVERSION AS os_version,
                A4.RELEASEID AS os_release,
                A5.OSTYPE AS os
FROM Computer A0 (nolock)
LEFT OUTER JOIN LDAPUserAttrV A1 (nolock) ON A0.Computer_Idn = A1.Computer_Idn
LEFT OUTER JOIN CompSystem A2 (nolock) ON A0.Computer_Idn = A2.Computer_Idn
LEFT OUTER JOIN BitLocker A3 (nolock) ON A0.Computer_Idn = A3.Computer_Idn
LEFT OUTER JOIN OSNT A4 (nolock) ON A0.Computer_Idn = A4.Computer_Idn
LEFT OUTER JOIN Operating_System A5 (nolock) ON A0.Computer_Idn = A5.Computer_Idn
{:s}
ORDER BY A0.LASTUPDINVSVR DESC
"""


ATTRIBUTES_TO_COPY = [
    'manufacturer',
    'model',
    'name',
    'os',
    'os_version',
    'os_release',
    'os_build',
    'serial',
    'type',
    'email',
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


# regular expressions for the _reformat_screenlock_reason function below
SCREENLOCK_PATTERNS_RAW = {
  'enabled': r"""The screen saver is not enabled for user (.*)""",
  'timeout': r"""The screen saver time out value for user (.*) is longer than ([0-9]+) minutes""",
  'password': r"""The screen saver password protection setting is not enabled for user (.*)""",
}

SCREENLOCK_PATTERNS = {name: re.compile(pattern, re.UNICODE) for name, pattern in
    six.iteritems(SCREENLOCK_PATTERNS_RAW)}


def _reformat_screenlock_reason(reason_string):
  """Reformat the 'reason' string for screenlock (`ST000202`, which is missing line breaks/spaces).

  >>> print(_reformat_screenlock_reason('''The screen saver is not enabled for user foo.'''))
    • The screen saver is not enabled for user: foo.

  >>> print(_reformat_screenlock_reason(
  ... '''The screen saver is not enabled for user foo.The screen saver password '''
  ... '''protection setting is not enabled for user foo.The screen saver time '''
  ... '''out value for user foo is longer than 10 minutes.The screen saver is '''
  ... '''not enabled for user bar.The screen saver password protection setting is '''
  ... '''not enabled for user bar.The screen saver time out value for user bar is '''
  ... '''longer than 10 minutes.The screen saver is not enabled for user baz.The '''
  ... '''screen saver time out value for user baz is longer than 10 minutes.The '''
  ... '''screen saver is not enabled for user qux.The screen saver password '''
  ... '''protection setting is not enabled for user qux.The screen saver time '''
  ... '''out value for user qux is longer than 10 minutes.'''
  ... ))
    • The screen saver is not enabled for users: bar, baz, foo, qux.
    • The screen saver timeout value is longer than 10 minutes for users: bar, baz, foo, qux.
    • The screen saver password is not enabled for users: bar, foo, qux.

  """

  sentences = reason_string.split('.')

  violators = collections.defaultdict(set)
  for sentence in sentences:
    for name, pattern in six.iteritems(SCREENLOCK_PATTERNS):
      match = pattern.match(sentence)
      if match is not None:
        violators[name].add(match.group(1))

  def __format_user_list(users):
    """Helper that returns a formatted string similar to: 'for users: foo, bar'."""
    return "for user{:s}: {:s}".format("s" if len(users) > 1 else "", ", ".join(sorted(users)))

  reasons = list()
  if len(violators['enabled']) > 0:
    reasons.append("The screen saver is not enabled {:s}."
                   "".format(__format_user_list(violators['enabled'])))

  if len(violators['timeout']) > 0:
    # find the timeout's value (assume it's the same for every user)
    try:
      timeout_value = int(SCREENLOCK_PATTERNS['timeout'].search(reason_string).group(2))
    except (IndexError, ValueError):
      raise ValueError("Failed to find screensaver timeout timeout value.")

    reasons.append("The screen saver timeout value is longer than {:d} minutes {:s}."
                   "".format(timeout_value, __format_user_list(violators['timeout'])))

  if len(violators['password']) > 0:
    reasons.append("The screen saver password is not enabled {!s}."
                   "".format(__format_user_list(violators['password'])))

  return "\n".join("  • " + reason for reason in reasons)


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
    return [self._normalize_software_row(row) for row in conn]

  def _check_screenlock(self, raw):
    data = {'value': True}

    for vuln in raw['vulns']:
      if vuln['Vul_ID'] == 'ST000202':
        data['value'] = False
        data['details'] = _reformat_screenlock_reason(vuln['Reason'])
        logger.debug("screenlock reason:\n{!r}", data['details'])

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
        # "Protection Status: {PROTECTIONSTATUS!s}\n"
        "Encryption Percentage: {ENCRYPTIONPERCENTAGE!s}\n"
        # "Conversion Status: {CONVERSIONSTATUS!s}\n"
        # "Encryption Method: {GENENCRYPT!s}\n"
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
        except Exception:
          name = 'unknown'
        details.append("Firewall not enabled for adapter '{!s}'".format(name))
    data['details'] = '\n'.join(details)

    if raw.get('hw_last_scan_date') is not None:
      data['last_updated'] = arrow.get(raw['hw_last_scan_date'], 'US/Pacific')

    return data

  def _process_device(self, raw):
    device = {'_raw': raw} if self._debug else {}
    # logger.debug("raw: {:s}", stethoscope.utils.json_pp(raw))

    # INFORMATION
    for attr in ATTRIBUTES_TO_COPY:
      if raw.get(attr) is not None:
        device[attr] = raw[attr]

    if raw.get('last_seen') is not None:
      device['last_sync'] = arrow.get(raw['last_seen'], 'US/Pacific')

    # hack to get a readable model string for Lenovo machines
    if device.get('manufacturer') == "LENOVO" and raw.get('systemversion') is not None:
      device['model'] = raw['systemversion']

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
      'mac_addresses': list(stethoscope.validation.filter_macaddrs(set(map(
        lambda adapter: stethoscope.validation.canonicalize_macaddr(adapter['PhysAddress']),
        filter(lambda adapter: adapter['FirewallEnabled'] != 'Not Installed', raw['adapters'])
      ))))
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
      # logger.debug("software:\n{!s}", pprint.pformat(raw['software']))
      devices.append(self._process_device(raw))
    return devices

  def get_devices_by_email(self, email):
    with _mssql.connect(**self._conn_kwargs) as conn:
      conn.execute_query(DEVICES_FOR_USER.format("WHERE A1.EMAILADDR = %s"), email)
      return self._get_devices_by_email(conn)

  def test_connectivity(self):
    with _mssql.connect(**self._conn_kwargs) as conn:
      if not conn.connected:
        raise Exception("Failed to connect to LANDESK's MSSQL server.")
