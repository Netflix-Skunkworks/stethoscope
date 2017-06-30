# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import pprint

import elasticsearch
import elasticsearch_dsl
import logbook
from twisted.internet import threads

import stethoscope.plugins.mixins.es


logger = logbook.Logger(__name__)


class ElasticSearchNotifications(stethoscope.plugins.mixins.es.ElasticSearchMixin):
  """Example of a notifications plugin which queries an Elasticsearch cluster."""

  def create_query_for_email(self, search, email):
    return search.query(elasticsearch_dsl.Q({"match": {'email': email}}))

  def _get_notifications_by_email(self, email):
    search = elasticsearch_dsl.Search(using=self.client, index=self.config['ELASTICSEARCH_INDEX'],
      doc_type=self.config['ELASTICSEARCH_DOCTYPE'])

    query = self.create_query_for_email(search, email)

    # logger.debug("query:\n{!s}", pprint.pformat(query.to_dict()))

    try:
      response = query.execute()
    except elasticsearch.exceptions.ElasticsearchException:
      logger.exception("Exception caught in Elasticsearch query:\n  index: {!r}\n  doc_type: {!r}\n"
                       "  query: {!s}".format(self.config['ELASTICSEARCH_INDEX'],
                         self.config['ELASTICSEARCH_DOCTYPE'], pprint.pformat(query.to_dict())))

    # logger.debug("response:\n{!s}", pprint.pformat(response.to_dict()))

    return response.hits.hits

  def get_notifications_by_email(self, *args, **kwargs):
    return threads.deferToThread(self._get_notifications_by_email, *args, **kwargs)
