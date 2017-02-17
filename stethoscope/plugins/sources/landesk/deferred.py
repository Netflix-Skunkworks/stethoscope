# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

from twisted.internet import threads
import logbook

import stethoscope.plugins.sources.landesk.base


logger = logbook.Logger(__name__)


class DeferredLandeskSQLDataSource(
    stethoscope.plugins.sources.landesk.base.LandeskSQLDataSourceBase,
  ):

  def get_devices_by_email(self, email):
    return threads.deferToThread(super(DeferredLandeskSQLDataSource, self).get_devices_by_email,
        email)

  def get_devices_by_serial(self, serial):
    return threads.deferToThread(super(DeferredLandeskSQLDataSource, self).get_devices_by_serial,
        serial)

  def get_devices_by_macaddr(self, macaddr):
    return threads.deferToThread(super(DeferredLandeskSQLDataSource, self).get_devices_by_macaddr,
        macaddr)
