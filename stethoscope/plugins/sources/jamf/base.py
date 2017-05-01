# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import arrow
import logbook

import stethoscope.plugins.sources.jamf.utils as jutils
import stethoscope.validation
import stethoscope.configurator
import stethoscope.utils


logger = logbook.Logger(__name__)


def inject_last_updated(data, last_updated):
  data['last_updated'] = last_updated
  return data


class JAMFDataSourceBase(stethoscope.configurator.Configurator):

  config_keys = (
    'JAMF_API_USERNAME',
    'JAMF_API_PASSWORD',
    'JAMF_API_HOSTADDR',
  )

  def _check_uptodate(self, raw):
    updates = raw['computer']['software']['available_software_updates']

    data = {'value': (len(updates) == 0)}
    if len(updates) > 0:
      data['details'] = "Missing Updates:\n"
      for update in updates:
        data['details'] += "    {!s}\n".format(update)
    return data

  def _check_autoupdate(self, attributes):
    attrs = [
      ('1 Auto Check For Updates Enabled', 'True', 'Automatically check for updates'),
      ('2 Get New Updates in Background Enabled', 'True',
          'Download newly available updates in background'),
      ('3 Install App Updates Enabled', 'False', 'Install app updates'),
      ('4 Install OS X Updates Enabled', 'False', 'Install OS X updates'),
      ('5 Install Security Updates Enabled', 'True', 'Install security updates'),
      ('6 Install System Data Files Enabled', 'True', 'Install system data files'),
    ]

    values = list()
    for (attr, default, _) in attrs:
      value = attributes.get(attr)
      values.append(value if value in ['True', 'False'] else default)

    data = {'value': all(value == "True" for value in values)}
    if not data['value']:
      data['details'] = "Disabled settings:\n" + "\n".join("    {!s}".format(label)
          for value, (_, _, label) in zip(values, attrs) if value != 'True')
    return data

  def _check_encryption(self, raw):
    data = {}

    try:
      storage = raw['computer']['hardware']['storage']
    except KeyError:
      pass
    else:
      details = list()
      encrypted = list()
      for drive in storage:
        if drive['drive_capacity_mb'] > 0 and 'partition' in drive:
          # hack to work around bug in JAMF
          if drive['partition']['name'] == 'Recovery HD':
            continue

          encrypted.append(drive['partition']['filevault2_status'] == "Encrypted")

          # hack to work around bug in JAMF
          status = drive['partition']['filevault2_status']
          if status == "Not Supported":
            status = "Not Encrypted"

          details.append("{name!s}: {status:s} ({filevault2_percent:d}%)"
                         "".format(status=status, **drive['partition']))

      data['value'] = all(encrypted)
      data['details'] = '\n'.join(details)

    return data

  def _normalize_software_entry(self, entry):
    """Convert software information returned from JAMF to common software list format."""
    return entry

  def _process_device(self, raw):
    if raw is None:
      return None
    data = {'_raw': raw} if self._debug else {}

    computer = raw['computer']
    # logger.debug("computer:\n{:s}".format(pprint.pformat(computer)))

    attributes = jutils._parse_parameter_list(computer['extension_attributes'])
    # logger.debug("extension attributes:\n{:s}".format(pprint.pformat(attributes)))

    # INFORMATION
    data['model'] = computer['hardware']['model']

    data.update(stethoscope.utils.copy_partial_dict(computer['general'], {
      'platform': 'platform',
      'serial': 'serial_number',
      'name': 'name',
    }))

    data.update(stethoscope.utils.copy_partial_dict(computer['hardware'], {
      'os': 'os_name',
      'os_version': 'os_version',
    }))

    try:
      last_updated = arrow.get(computer['general']['report_date_utc'])
    except arrow.parser.ParserError:
      last_updated = None

    data['last_sync'] = last_updated

    # PRACTICES
    data['practices'] = dict()
    data['practices']['encryption'] = inject_last_updated(self._check_encryption(raw), last_updated)
    data['practices']['uptodate'] = inject_last_updated(self._check_uptodate(raw), last_updated)
    data['practices']['autoupdate'] = inject_last_updated(self._check_autoupdate(attributes),
        last_updated)

    data['software'] = {'last_scan_date': last_updated}
    data['software']['installed'] = dict((entry['name'], self._normalize_software_entry(entry))
        for entry in raw['computer']['software']['applications'])
    data['software']['services'] = dict((service, {'name': service}) for service in
        raw['computer']['software']['running_services'])

    try:
      practice = {'value': int(attributes['Firewall Status']) > 0}
    except (KeyError, ValueError):
      practice = {}
    data['practices']['firewall'] = inject_last_updated(practice, last_updated)

    for key, attr, ok_value in [
      ('screenlock', 'Screen Saver Lock Enabled', 'Enabled'),
      ('remotelogin', 'Remote Login', 'Off'),
    ]:
      practice = {} if attr not in attributes else {'value': attributes[attr] == ok_value}
      data['practices'][key] = inject_last_updated(practice, last_updated)

    # IDENTIFIERS
    possible_macs = [
      computer['general'].get('mac_address', ''),
      computer['general'].get('alt_mac_address', ''),
      attributes.get('Wireless Mac Address', ''),
    ]
    mac_addresses = set(stethoscope.validation.canonicalize_macaddr(addr)
        for addr in possible_macs if addr != '')

    data['identifiers'] = {
        'serial': computer['general']['serial_number'],
        'mac_addresses': list(mac_addresses),
        'udid': computer['general']['udid'],
    }

    data['source'] = 'jamf'
    # logger.debug("returned info:\n{:s}".format(pprint.pformat(data)))
    return data

  @staticmethod
  def _extract_device_ids_from_userinfo(userinfo_response):
    return JAMFDataSourceBase._extract_device_ids_from_response(
        userinfo_response.get('user', {}).get('links', {})
    )

  @staticmethod
  def _extract_device_ids_from_response(search_response):
    return [computer['id'] for computer in search_response.get('computers', [])]
