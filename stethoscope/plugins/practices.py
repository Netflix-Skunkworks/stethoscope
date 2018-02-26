# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import abc
import collections
import re

import logbook
import pkg_resources
import six

import stethoscope.configurator


logger = logbook.Logger(__name__)


def _check_exists(data, key, false_value='nudge'):
  try:
    installed = data.get('practices', {})[key]
  except KeyError:
    return 'unknown'

  if isinstance(installed, collections.Mapping):
    installed = installed.get('value')

  if installed is None:
    return 'unknown'

  return 'ok' if installed else false_value


@six.add_metaclass(abc.ABCMeta)
class PracticeBase(stethoscope.configurator.Configurator):

  config_keys = (
    'KEY',
    'DISPLAY_TITLE',
    'DESCRIPTION',
  )

  @abc.abstractmethod
  def inject_status(self, device):
    pass  # pragma: nocover

  def _inject_status(self, device, status, **kwargs):
    device.setdefault('practices', {})

    practice_data = device['practices'].get(self.config['KEY'], {})

    practice_data.update({
      'title': self.config['DISPLAY_TITLE'],
      'display': self.config.get('DISPLAY', True),
      'status': status,
      'description': self.config['DESCRIPTION'],
    })

    practice_data.update(kwargs)

    if self.config.get('LINK'):
      practice_data['link'] = self.config['LINK']

    device['practices'][self.config['KEY']] = practice_data


class PlatformOverrideMixin(object):
  """Provides the `override_platform` method to subclasses."""

  def override_platform(self, platform):
    """Stub for plugins which need to do overrides on a per-platform basis."""
    if platform is None and self.config.get('PLATFORM_REQUIRED', False):
      return 'na'  # TODO: should be unknown?
    if platform in self.config.get('NA_PLATFORMS', []):
      return 'na'
    if platform in self.config.get('OK_PLATFORMS', []):
      return 'ok'
    return None


class KeyExistencePractice(PracticeBase, PlatformOverrideMixin):
  """Checks for the existence of a particular key in the device's data dictionary.

  .. note:: This is used mostly as a temporary bridge between a real future implementation and the
  older, non-plugin based system.
  """

  def inject_status(self, device):
    status = self.override_platform(device.get('platform'))

    if not status:
      status = _check_exists(device, self.config['KEY'],
          false_value=self.config.get('STATUS_IF_MISSING', 'nudge'))

    return self._inject_status(device, status)


def check_os_version(os, os_version, required_versions, recommended_versions):
  """Check the given OS version against the required/recommended versions.

  >>> REQUIRED = {
  ...   'Mac OS X': '10.11.0',
  ...   'iOS': '9.3.5',
  ...   'Android': '6.0.0',
  ... }

  >>> RECOMMENDED = {
  ...   'Mac OS X': '10.11.6',
  ...   'iOS': '9.3.5',
  ...   'Android': '6.0.1',
  ... }

  >>> check_os_version("Mac OS X", None, REQUIRED, RECOMMENDED) is None
  True
  >>> check_os_version("Mac OS X", "10.11.6", REQUIRED, RECOMMENDED)
  'ok'
  >>> check_os_version("Mac OS X", "10.11.5", REQUIRED, RECOMMENDED)
  'nudge'
  >>> check_os_version("Mac OS X", "10.10.5", REQUIRED, RECOMMENDED)
  'warn'
  >>> check_os_version("Android", "5.0", REQUIRED, RECOMMENDED)
  'warn'
  >>> check_os_version("iOS", "9.3.0", REQUIRED, RECOMMENDED)
  'warn'

  """
  if os_version is None:
    return None

  try:
    version = pkg_resources.parse_version(os_version)
  except Exception:
    logger.error("failed to parse version string: {!r}", os_version)
  else:
    if os in required_versions and version < pkg_resources.parse_version(required_versions[os]):
      return 'warn'
    elif (os in recommended_versions and
          version < pkg_resources.parse_version(recommended_versions[os])):
      return 'nudge'
    elif os in required_versions or os in recommended_versions:
      return 'ok'

  return None


class UptodatePractice(PracticeBase):
  """Checks OS versions against configured values for recommended and unsupported versions."""

  def __init__(self, *args, **kwargs):
    super(PracticeBase, self).__init__(*args, **kwargs)
    self.config.setdefault('UNSUPPORTED_MSG', '{!s} is no longer supported.')
    self.config.setdefault('RECOMMENDED_MSG', 'The recommended version of {!s} is {!s}.')

  @property
  def config_keys(self):
    return super(UptodatePractice, self).config_keys + (
      'REQUIRED_VERSIONS',
      'RECOMMENDED_VERSIONS',
    )

  def check_uptodate(self, data):
    data.setdefault('practices', {})

    os = data.get('os')
    if os is not None:
      match = re.match('Microsoft Windows [78]', os)
      if match is not None:
        uptodate = data['practices'].get('uptodate', {})
        uptodate['details'] = self.config['UNSUPPORTED_MSG'].format(match.group(0))
        data['practices']['uptodate'] = uptodate
        return 'warn'

      os_version = data.get('os_version')
      status = check_os_version(os, os_version, self.config['REQUIRED_VERSIONS'],
          self.config['RECOMMENDED_VERSIONS'])

      if status is not None:
        details = []
        if status == 'warn':
          details.append(self.config['UNSUPPORTED_MSG'].format(os + ' ' + os_version))
        details.append(self.config['RECOMMENDED_MSG'].format(os,
          self.config['RECOMMENDED_VERSIONS'][os]))
        uptodate = data['practices'].setdefault('uptodate', {})
        uptodate['details'] = ' '.join(details)

        return status

    return _check_exists(data, 'uptodate', false_value='warn')

  def inject_status(self, device):
    return self._inject_status(device, self.check_uptodate(device))


class InstalledSoftwarePractice(PracticeBase, PlatformOverrideMixin):
  """Checks whether a specific software/service is installed/running on the system."""

  def inject_status(self, device):
    attrs = dict()
    status = self.override_platform(device.get('platform'))
    if not status:
      software = device.get('software', {})

      if 'last_scan_date' in device:
        attrs['last_updated'] = software['last_scan_date']

      installed = dict((entry['name'], entry) for entry in software.get('installed', []))
      for name in self.config.get('SOFTWARE_NAMES', []):
        details = installed.get(name)
        if details is not None:
          status = 'ok'
          if 'version' in details:
            attrs['version'] = details['version']
            attrs['details'] = "Version: {!s}".format(details['version'])

      services = dict((entry['name'], entry) for entry in software.get('services', []))
      for name in self.config.get('SERVICE_NAMES', []):
        details = services.get(name)
        if details is not None:
          status = 'ok'
          if 'version' in details:
            attrs['version'] = details['version']
            attrs['details'] = "Version: {!s}".format(details['version'])

    if not status:
      status = self.config.get('STATUS_IF_MISSING', 'nudge')

    return self._inject_status(device, status, **attrs)
