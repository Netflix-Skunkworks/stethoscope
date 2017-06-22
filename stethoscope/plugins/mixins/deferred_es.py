# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

from twisted.internet import threads
import logbook

from .es import ElasticSearchMixin


logger = logbook.Logger(__name__)


class DeferredElasticSearchMixin(ElasticSearchMixin):

  def test_connectivity(self):
    return threads.deferToThread(super(DeferredElasticSearchMixin, self).test_connectivity)
