# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import copy
import json
import os
import os.path

import logbook
import pytest

import stethoscope.plugins.sources.google.deferred


logger = logbook.Logger(__name__)

DEVICE_NAMES = (
  'android',
  'android_oreo',
  'ios_google-sync',
  'chromeos',
  'chromeos_pixelbook',
)


@pytest.fixture(scope='module')
def basedir():
  return "tests/fixtures/google/devices"


@pytest.fixture(scope='module')
def raw_devices(basedir):
  """Loads files in a directory as JSON; returns `dict` mapping filename (w/o ext) to contents."""
  devices = dict()
  for filename in os.listdir(basedir):
    filepath = os.path.join(basedir, filename)
    if os.path.isfile(filepath):
      shortname = os.path.splitext(filename)[0]
      with open(filepath) as fo:
        devices[shortname] = json.load(fo)
      logger.debug("loaded '{!s}' as '{!s}'", filepath, shortname)
  return devices


@pytest.fixture(params=DEVICE_NAMES, scope='function')
def raw_device(request, raw_devices):
  """Returns a copy of a single device, given name, from the `dict` returned by `raw_devices`."""
  return copy.deepcopy(raw_devices[request.param])


@pytest.fixture(scope='function')
def mock_datasource():
  return stethoscope.plugins.sources.google.deferred.DeferredGoogleDataSource({
    'GOOGLE_API_SECRETS': '',
    'GOOGLE_API_USERNAME': '',
    'GOOGLE_API_SCOPES': '',
    'DEBUG': True,
  })
