# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import logbook
from twisted.internet import threads

import stethoscope.plugins.sources.duo.base
import stethoscope.configurator


logger = logbook.Logger(__name__)


class DeferredDuoDataSource(
    stethoscope.plugins.sources.duo.base.DuoDataSourceBase,
    stethoscope.configurator.Configurator,
  ):

  @property
  def connection(self):
    # TODO: fix so that every request doesn't require a new connection
    return self.connect()

  def get_events_by_email(self, email):
    return threads.deferToThread(super(DeferredDuoDataSource, self).get_events_by_email, email)
