# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import logbook
import netaddr

import stethoscope.configurator


logger = logbook.Logger(__name__)


class VPNFilter(stethoscope.configurator.Configurator):

  config_keys = (
    'VPN_CIDRS',
  )

  def __init__(self, *args, **kwargs):
    super(VPNFilter, self).__init__(*args, **kwargs)
    self._networks = netaddr.IPSet(self.config['VPN_CIDRS'])

  def augment(self, events):
    for event in events:
      event['vpn'] = (netaddr.IPAddress(event['ip_address']) in self._networks)
    return events
