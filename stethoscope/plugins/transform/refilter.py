# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import re

import logbook
import six

import stethoscope.configurator


logger = logbook.Logger(__name__)


class FilterMatching(stethoscope.configurator.Configurator):
  """Device transform which filters out virtual machines."""

  config_keys = (
    'PATTERN_MAP',
  )

  def matches(self, device):
    """Check the device against the configured patterns."""
    for key, pattern in six.iteritems(self.config['PATTERN_MAP']):
      value = device.get(key)
      if value is not None:
        match = re.search(pattern, value)
        if match is not None:
          logger.debug("filtering device ({:s} '{!s}' matched '{!s}')", key, value, match.group())
          return True
    return False

  def transform(self, devices):
    """Filter out devices which match the specified regular expressions."""
    return [device for device in devices if not self.matches(device)]
