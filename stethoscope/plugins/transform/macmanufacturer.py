# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import logbook
import netaddr

import stethoscope.configurator


logger = logbook.Logger(__name__)


def get_org(macaddr):
  """Return the IEEE-registered organization for the given MAC address (or `None` if none)."""

  mac = netaddr.EUI(macaddr)

  if mac.is_iab():
    try:
      return mac.iab.registration()['org']
    except netaddr.core.NotRegisteredError:
      pass

  try:
    return mac.oui.registration().org
  except netaddr.core.NotRegisteredError:
    return None


class AddMACManufacturer(stethoscope.configurator.Configurator):
  """Device transform which adds manufacturer information based on MAC addresses."""

  config_keys = ()

  def transform(self, devices):
    """For each device, add manufacturer information (derived from MAC addresses)."""
    for device in devices:
      if device.get('manufacturer') is not None:
        continue

      for mac_address in device.get('identifiers', {}).get('mac_addresses', []):
        manufacturer = get_org(mac_address)
        if manufacturer is not None:
          device['manufacturer'] = manufacturer
          break

    return devices
