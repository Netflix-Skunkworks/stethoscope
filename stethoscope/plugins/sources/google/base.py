# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import arrow
import logbook
import pkg_resources
import six
from apiclient import discovery

import stethoscope.plugins.sources.google.utils as gutils
import stethoscope.validation


logger = logbook.Logger(__name__)


PROPERTIES = {
  "serial": "serialNumber",
  "model": "model",
  "manufacturer": "manufacturer",
  "os_version": "osVersion",
  "last_sync": "lastSync",
  "user_agent": "userAgent",
}

IDENTIFIERS = {
  "imei": "imei",
  "meid": "meid",
  "serial": "serialNumber",
  "google_device_id": "deviceId",
}


def get_nonempty_value(mapping, key):
  """Returns value for `key` if `key` is in `mapping` and not a blank/empty string else `None`."""
  if mapping.get(key, '').strip() != '':
    return mapping[key]
  return None


def copy_nonempty_values(dst, src, key_map):
  """Copy non-empty key/value pairs from `src` to `dst` for source and dest keys in `key_map`."""
  for dst_key, src_key in six.iteritems(key_map):
    value = get_nonempty_value(src, src_key)
    if value is not None:
      dst[dst_key] = value


def parse_os_information(os):
  """Extract platform, OS, and version information from the Google API OS information string.

  >>> sorted(six.iteritems(parse_os_information('iOS 10.2.1')))
  [('os', 'iOS'), ('os_version', '10.2.1'), ('platform', 'iOS')]

  >>> sorted(six.iteritems(parse_os_information('Android 8.0.0')))
  [('os', 'Android'), ('os_version', '8.0.0'), ('platform', 'Android')]

  NOTE: Google sometimes only provides major/minor versions without patch number; we throw that out
  since it's not enough information to know if it's up-to-date or not.
  >>> sorted(six.iteritems(parse_os_information('iOS 9.3')))
  [('os', 'iOS'), ('platform', 'iOS')]
  """
  (os, version) = os.split()
  data = {
    'platform': os,
    'os': os,
  }

  # Google sometimes only provides minor version without patch number; we ignore that case since
  # that's not enough information to know if the device is up-to-date or not.
  try:
    parsed_version = pkg_resources.parse_version(version)
  except Exception:
    logger.exception("Failed to parse version string from {!r}; ignoring.".format(version))
  else:
    # Dirty hack which will probably break some day but there's basically no public API for
    # `pkg_resources.SetuptoolsVersion`.
    if len(parsed_version._version.release) >= 3:
      data['os_version'] = version

  return data


class GoogleDataSourceBase(object):

  def get_events_by_email(self, email, max_results=500, batch_size=500):
    service = discovery.build('admin', 'reports_v1', http=self.connection)
    resource = service.activities()

    request = resource.list(applicationName='login', userKey=email,
        maxResults=min([max_results, batch_size]))
    activities = gutils.execute_batch(resource, request, 'items', max_results=max_results)

    if not activities:
      logger.warn("no google login events found for user '{:s}'", email)
      return []

    return [gutils.parse_activity(activity) for activity in activities]

  def get_userinfo_by_email(self, email):
    directory = discovery.build('admin', 'directory_v1', http=self.connection)
    return gutils.execute_request(directory.users().get(userKey=email))

  def get_account_by_email(self, email):
    reports = self.get_userusage(email)['usageReports'][0]
    usage_parameters = gutils.parse_parameters_list(reports['parameters'])
    usage_parameters['date'] = reports['date']

    return {
      'name': email,
      'type': 'google',
      'source': 'google',
      'user_usage': usage_parameters,
      'last_updated': arrow.utcnow(),
      # 'authorized_apps': self.get_tokens(email)['items'],
    }

  def get_userusage(self, email):
    reports = discovery.build('admin', 'reports_v1', http=self.connection)
    date = arrow.utcnow().replace(days=-3)
    reports_request = reports.userUsageReport().get(userKey=email, date=date.format('YYYY-MM-DD'))
    return gutils.execute_request(reports_request)

  def get_tokens(self, email):
    directory = discovery.build('admin', 'directory_v1', http=self.connection)
    return gutils.execute_request(directory.tokens().list(userKey=email))

  def _check_jailed(self, raw, last_updated):
    value = get_nonempty_value(raw, 'deviceCompromisedStatus')
    if value is None:
      return None

    data = {'last_updated': last_updated}
    if value.lower() == 'compromise detected':
      data['value'] = False
    elif value.lower() == 'no compromise detected':
      data['value'] = True
    return data

  def _check_jailed_chromeos(self, raw, last_updated):
    value = get_nonempty_value(raw, 'bootMode')
    return None if value is None else {
      'last_updated': last_updated,
      'value': (value.lower() in ('validated', 'verified')),
    }

  def _check_encrypted(self, raw, last_updated):
    # TODO: determine what the other possible values are
    value = get_nonempty_value(raw, 'encryptionStatus')
    return None if value is None else {
      'last_updated': last_updated,
      'value': (value.lower() == 'encrypted'),
    }

  def _process_mobile_device(self, raw):
    """

    Identifiers (source_):

    ============ ====== ======================================================================
      Property    Type                              Description
    ============ ====== ======================================================================
    serialNumber string The device's serial number.
    meid         string The device's MEID number.
    imei         string The device's IMEI number.
    deviceId     string The serial number for a Google Sync mobile device. For Android and iOS
                        devices, this is a software generated unique identifier.
    resourceId   string The unique ID the API service uses to identify the mobile device.
    hardwareId   string The IMEI/MEID unique identifier for Android hardware. It is not
                        applicable to Google Sync devices.
    ============ ====== ======================================================================

    .. source_: https://developers.google.com/admin-sdk/directory/v1/reference/mobiledevices
                #resource-representations

    """
    # logger.debug("processing device:\n{!s}", pprint.pformat(raw))
    data = {'_raw': raw} if self._debug else {}
    data['type'] = 'Mobile Device'

    os = get_nonempty_value(raw, 'os')
    if os is not None:
      data.update(parse_os_information(os))

    # prefer 'osVersion' key to parsed key if present
    copy_nonempty_values(data, raw, PROPERTIES)

    data['last_sync'] = arrow.get(data['last_sync'])

    data['practices'] = dict()

    jailed = self._check_jailed(raw, last_updated=data['last_sync'])
    if jailed is not None:
      data['practices']['jailed'] = jailed

    encrypted = self._check_encrypted(raw, last_updated=data['last_sync'])
    if encrypted is not None:
      data['practices']['encryption'] = encrypted

    if raw['type'] != 'ANDROID' or \
        ('os_version' in data and
         pkg_resources.parse_version(data['os_version']) < pkg_resources.parse_version('8.0.0')):
      # 'unknownSourcesStatus' is meaningless on Android 8.X+; equivalent setting is per-app
      data['practices']['unknownsources'] = {
        'last_updated': data['last_sync'],
        'value': not raw['unknownSourcesStatus'],
      }

    data['practices']['adbstatus'] = {
      'last_updated': data['last_sync'],
      'value': not raw['adbStatus'],
    }

    # TODO: check 'devicePasswordStatus'? (what does that represent?)

    # copy all relevant identifiers
    data['identifiers'] = {}
    copy_nonempty_values(data['identifiers'], raw, IDENTIFIERS)

    value = get_nonempty_value(raw, 'wifiMacAddress')
    if value is not None:
      data['identifiers']['mac_addresses'] = [
        stethoscope.validation.canonicalize_macaddr(value)
      ]

    data['source'] = 'google'
    return data

  def _process_chromeos_device(self, raw):
    data = {'_raw': raw} if self._debug else {}
    data['type'] = 'ChromeOS Device'

    copy_nonempty_values(data, raw, PROPERTIES)

    data['last_sync'] = arrow.get(data['last_sync'])

    data['os'] = 'ChromeOS'

    data['practices'] = dict()

    jailed = self._check_jailed_chromeos(raw, last_updated=data['last_sync'])
    if jailed is not None:
      data['practices']['jailed'] = jailed

    # copy all relevant identifiers
    data['identifiers'] = {}
    copy_nonempty_values(data['identifiers'], raw, IDENTIFIERS)

    macs = []
    for key in ['macAddress', 'ethernetMacAddress']:
      value = get_nonempty_value(raw, key)
      if value is not None:
        macs.append(stethoscope.validation.canonicalize_macaddr(value))
    data['identifiers']['mac_addresses'] = macs

    data['source'] = 'google'
    return data

  def _get_mobile_devices_by_email(self, email, batch_size=1000):
    service = discovery.build('admin', 'directory_v1', http=self.connection)
    resource = service.mobiledevices()
    request = resource.list(customerId='my_customer', query='email:{!s}'.format(email),
        projection="FULL", maxResults=batch_size)
    mobile_devices = gutils.execute_batch(resource, request, 'mobiledevices')
    # logger.debug("found {:d} mobile devices", len(mobile_devices))
    # logger.debug("mobile devices:\n{!s}", pprint.pformat(mobile_devices))
    return [self._process_mobile_device(raw) for raw in mobile_devices]

  def _get_chromeos_devices_by_email(self, email, batch_size=1000):
    service = discovery.build('admin', 'directory_v1', http=self.connection)
    resource = service.chromeosdevices()
    request = resource.list(customerId='my_customer', query='user:{!s}'.format(email),
        projection="FULL", maxResults=batch_size)
    chromeos_devices = gutils.execute_batch(resource, request, 'chromeosdevices')
    # logger.debug("found {:d} chrome OS devices", len(chromeos_devices))
    # logger.debug("chrome OS devices:\n{!s}", pprint.pformat(chromeos_devices))
    return [self._process_chromeos_device(raw) for raw in chromeos_devices]

  def get_devices_by_email(self, email, batch_size=1000):
    return self._get_mobile_devices_by_email(email, batch_size=batch_size) + \
      self._get_chromeos_devices_by_email(email, batch_size=batch_size)

  def test_connectivity(self):
    """Executes a basic API call with no side-effects to ensure we can talk to Google."""
    service = discovery.build('discovery', 'v1', http=self.connection)
    request = service.apis().list(name="discovery", preferred=True)
    response = gutils.execute_request(request)
    # logger.debug("connectivity test response:\n{:s}", pprint.pformat(response))
    return response
