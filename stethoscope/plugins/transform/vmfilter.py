# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import re

import logbook

import stethoscope.configurator


logger = logbook.Logger(__name__)


def is_virtual_machine(device):
  """Return `True` if the device information represents a virtual machine, `False` otherwise.

  >>> is_virtual_machine({'model': "Virtual Machine"})
  True
  >>> is_virtual_machine({'model': "Virtual Machine"})
  True
  >>> is_virtual_machine({'serial': "VMware-DE CA FB AD"})
  True
  >>> is_virtual_machine({'serial': "Parallels-DE CA FB AD"})
  True

  """
  model = device.get('model')
  if model is not None and re.search('(Virtual Machine|VMware|amazon)', model) is not None:
    return True

  serial = device.get('serial')
  if serial is not None and re.search('(Parallels|VMware)', serial) is not None:
    return True

  return False


class FilterVMs(stethoscope.configurator.Configurator):
  """Device transform which filters out virtual machines."""

  config_keys = ()

  def transform(self, devices):
    """Filter out certain devices (e.g., VMs)."""
    return [device for device in devices if not is_virtual_machine(device)]
