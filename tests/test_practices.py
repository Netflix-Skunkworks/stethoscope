# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import pprint

import pytest

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


def test_software_practice_nudge(software_practice, expected_device_practices):
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
