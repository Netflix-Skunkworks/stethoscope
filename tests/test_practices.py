# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import pytest
import six

import stethoscope.plugins.practices


def test_key_existence_practice():
  practice = stethoscope.plugins.practices.KeyExistencePractice({
    'KEY': 'foo',
    'DISPLAY_TITLE': 'The display title',
    'DESCRIPTION': 'The description',
  })

  device = {
    'practices': {
      'foo': {
        'value': True,
      },
    },
  }

  practice.inject_status(device)

  assert device == {
    'practices': {
      'foo': {
        'value': True,
        'display': True,
        'status': 'ok',
        'title': 'The display title',
        'description': 'The description',
      },
    },
  }


@pytest.fixture(scope='function')
def software_practice():
  return stethoscope.plugins.practices.InstalledSoftwarePractice({
    'KEY': 'foo',
    'DISPLAY_TITLE': 'The display title',
    'DESCRIPTION': 'The description',
    'SOFTWARE_NAMES': ['Foobar.app'],
    'SERVICE_NAMES': ['com.foo.bar'],
  })


@pytest.fixture(scope='function')
def expected_device_practices():
  return {
    'foo': {
      'display': True,
      'status': 'ok',
      'title': 'The display title',
      'version': '0.0.1',
      'details': 'Version: 0.0.1',
      'description': 'The description',
    },
  }


def test_installed_software_practice(software_practice, expected_device_practices):
  device = {
    'software': {
      'installed': [
        {
          'name': 'Foobar.app',
          'version': '0.0.1',
        },
      ],
    },
  }

  software_practice.inject_status(device)

  assert device['practices'] == expected_device_practices


def test_running_service_practice(software_practice, expected_device_practices):
  device = {
    'software': {
      'services': [
        {
          'name': 'com.foo.bar',
          'version': '0.0.1',
        },
      ],
    },
  }

  software_practice.inject_status(device)

  assert device['practices'] == expected_device_practices


@pytest.fixture(scope='function')
def software_practice_version_required():
  return stethoscope.plugins.practices.InstalledSoftwarePractice({
    'KEY': 'foo',
    'DISPLAY_TITLE': 'The display title',
    'DESCRIPTION': 'The description',
    'SOFTWARE_NAMES': ['Foobar.app'],
    'SERVICE_NAMES': ['com.foo.bar'],
    'REQUIRED_VERSIONS': {
      'Mac OS X': '1.0',
    },
  })


def test_installed_software_practice_version_required(software_practice_version_required,
                                                      expected_device_practices):
  expected_device_practices['foo']['status'] = 'warn'

  device = {
    'os': 'Mac OS X',
    'software': {
      'installed': [
        {
          'name': 'Foobar.app',
          'version': '0.0.1',
        },
      ],
    },
  }

  software_practice_version_required.inject_status(device)

  assert device['practices'] == expected_device_practices


def test_running_service_practice_recommended(software_practice_version_required,
                                              expected_device_practices):
  expected_device_practices['foo']['status'] = 'warn'

  device = {
    'os': 'Mac OS X',
    'software': {
      'services': [
        {
          'name': 'com.foo.bar',
          'version': '0.0.1',
        },
      ],
    },
  }

  software_practice_version_required.inject_status(device)

  assert device['practices'] == expected_device_practices


def test_software_practice_nudge(software_practice):
  device = {
    'software': {
      'services': [
        {
          'name': 'not the service',
          'version': '0.0.1',
        },
      ],
    },
  }

  software_practice.inject_status(device)

  assert device['practices'] == {
    'foo': {
      'display': True,
      'status': 'nudge',
      'title': 'The display title',
      'description': 'The description',
    },
  }


@pytest.fixture(scope='function')
def uptodate_practice():
  return stethoscope.plugins.practices.UptodatePractice({
    'KEY': 'uptodate',
    'DISPLAY_TITLE': 'The display title',
    'DESCRIPTION': 'The description',
    'RECOMMENDED_VERSIONS': {'iOS': '11.1.1'},
    'REQUIRED_VERSIONS': {'iOS': '11.1.0'},
  })


def test_uptodate_practice_windows_7(uptodate_practice):
  device = {
    'os': 'Microsoft Windows 7'
  }

  uptodate_practice.inject_status(device)

  for key, value in six.iteritems({
    'status': 'warn',
    'details': 'Microsoft Windows 7 is no longer supported.',
  }):
    assert device['practices']['uptodate'][key] == value


def test_uptodate_practice_ios_warn(uptodate_practice):
  device = {
    'os': 'iOS',
    'os_version': '7.0.0',
  }

  uptodate_practice.inject_status(device)

  for key, value in six.iteritems({
    'status': 'warn',
    'details': 'iOS 7.0.0 is no longer supported. The recommended version of iOS is 11.1.1.',
  }):
    assert device['practices']['uptodate'][key] == value


def test_uptodate_practice_ios_nudge(uptodate_practice):
  device = {
    'os': 'iOS',
    'os_version': '11.1.0',
  }

  uptodate_practice.inject_status(device)

  for key, value in six.iteritems({
    'status': 'nudge',
    'details': 'The recommended version of iOS is 11.1.1.',
  }):
    assert device['practices']['uptodate'][key] == value


def test_uptodate_practice_ios_ok(uptodate_practice):
  device = {
    'os': 'iOS',
    'os_version': '11.1.1',
  }

  uptodate_practice.inject_status(device)

  for key, value in six.iteritems({
    'status': 'ok',
  }):
    assert device['practices']['uptodate'][key] == value


def test_directions():
  practice = stethoscope.plugins.practices.UptodatePractice({
    'KEY': 'uptodate',
    'DISPLAY_TITLE': 'The display title',
    'DESCRIPTION': 'The description',
    'RECOMMENDED_VERSIONS': {'iOS': '11.1.1'},
    'REQUIRED_VERSIONS': {'iOS': '11.1.0'},
    'DIRECTIONS': {'iOS': '1. Click the update button.'},
  })

  device = {
    'os': 'iOS',
    'os_version': '11.1.1',
  }

  practice.inject_status(device)
  assert device['practices']['uptodate']['directions'] == '1. Click the update button.'
