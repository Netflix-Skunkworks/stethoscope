# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import abc
import collections
import itertools
import operator
import re

import logbook
import pkg_resources
import six

import stethoscope.configurator
import stethoscope.utils


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

  def get_dependent_value(self, key, dependency_key):
    value = self.config.get(key, {})
    if isinstance(value, six.string_types):
      return value
    return value.get(dependency_key)

  @abc.abstractmethod
  def inject_status(self, device):
    pass  # pragma: nocover

  def _inject_status(self, device, status, **kwargs):
    device.setdefault('practices', {})

    practice_data = device['practices'].get(self.config['KEY'], {})

    title = self.get_dependent_value('DISPLAY_TITLE', status)
    if title is not None:
      # logger.debug("setting title to {!r} for status {!r}", title, status)
      practice_data['title'] = title

    if 'os' in device:
      directions = self.get_dependent_value('DIRECTIONS', device['os'])
      if directions is not None:
        # logger.debug("setting directions for status {!r}", status)
        practice_data['directions'] = directions

    practice_data.update({
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


def check_installed_version(os, installed_version, required_versions, recommended_versions):
  """Check the given version against the required/recommended versions.

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

  >>> check_installed_version("Mac OS X", None, REQUIRED, RECOMMENDED) is None
  True
  >>> check_installed_version("Mac OS X", "10.11.6", REQUIRED, RECOMMENDED)
  'ok'
  >>> check_installed_version("Mac OS X", "10.11.5", REQUIRED, RECOMMENDED)
  'nudge'
  >>> check_installed_version("Mac OS X", "10.10.5", REQUIRED, RECOMMENDED)
  'warn'
  >>> check_installed_version("Android", "5.0", REQUIRED, RECOMMENDED)
  'warn'
  >>> check_installed_version("iOS", "9.3.0", REQUIRED, RECOMMENDED)
  'warn'

  """
  if installed_version is None:
    return None

  try:
    version = pkg_resources.parse_version(installed_version)
  except Exception:
    logger.error("failed to parse version string: {!r}", installed_version)
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
      status = check_installed_version(os, os_version, self.config['REQUIRED_VERSIONS'],
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


def _generate_details_for_names(target_names, installed, os, required_versions,
                                recommended_versions):
  for name in target_names:
    details = installed.get(name)
    if details is None:
      continue

    attrs = {}
    if 'version' in details:
      attrs.update({
        'version': details['version'],
        'details': "Version: {!s}".format(details['version']),
      })

    if os is None:
      status = 'ok'
    else:
      status = check_installed_version(os, details.get('version'), required_versions,
                                     recommended_versions)
    if status is None:
      status = 'unknown'

    yield status, attrs


def _status_priority(match):
  return operator.indexOf(['unknown', 'nudge', 'warn', 'ok'], match[0])


class InstalledSoftwarePractice(PracticeBase, PlatformOverrideMixin):
  """Checks whether a specific software/service is installed/running on the system."""

  def inject_status(self, device):
    attrs = dict()
    status = self.override_platform(device.get('platform'))
    if not status and 'software' in device:
      required_versions = self.config.get('REQUIRED_VERSIONS', {})
      recommended_versions = self.config.get('RECOMMENDED_VERSIONS', {})

      software = device['software']

      last_updated = software.get('last_scan_date', device.get('last_sync'))
      if last_updated is not None:
        attrs['last_updated'] = last_updated

      installed_software = dict((entry['name'], entry) for entry in software.get('installed', []))
      target_software_names = self.config.get('SOFTWARE_NAMES', [])

      installed_services = dict((entry['name'], entry) for entry in software.get('services', []))
      target_service_names = self.config.get('SERVICE_NAMES', [])

      matches = list(itertools.chain(
        _generate_details_for_names(target_software_names, installed_software, device.get('os'),
                                    required_versions, recommended_versions),
        _generate_details_for_names(target_service_names, installed_services, device.get('os'),
                                    required_versions, recommended_versions),
      ))

      logger.debug("matches:\n{!s}", stethoscope.utils.json_pp(matches))

      if len(matches) > 0:
        status, _attrs = max(matches, key=_status_priority)
        attrs.update(_attrs)

    if not status:
      status = self.config.get('STATUS_IF_MISSING', 'nudge')

    logger.debug("status: {!r}", status)
    return self._inject_status(device, status, **attrs)
