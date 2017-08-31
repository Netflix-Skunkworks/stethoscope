# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import copy
import json

import arrow
import elasticsearch.exceptions
import logbook
from twisted.internet import threads

import stethoscope.plugins.mixins.es
import stethoscope.utils


logger = logbook.Logger(__name__)


class ElasticSearchAccessLogger(stethoscope.plugins.mixins.es.ElasticSearchMixin):

  config_keys = (
    'ELASTICSEARCH_HOSTS',
    'ELASTICSEARCH_INDEX_PREFIX',
    'ELASTICSEARCH_DOCTYPE',
  )

  def _log(self, record_type, userinfo, target, returned_data, context=None):
    # strip debug information
    returned_data = copy.deepcopy(returned_data)
    if isinstance(returned_data, dict):
      if '_raw' in returned_data:
        del returned_data['_raw']
    else:
      for device in returned_data:
        if '_raw' in device:
          del device['_raw']

    index = self.config['ELASTICSEARCH_INDEX_PREFIX'] + arrow.now().format("YYYYMM")
    doc_type = self.config['ELASTICSEARCH_DOCTYPE']
    body = {
        'accessing_user': userinfo['sub'],
        'target': target,
        'record_type': record_type,
        'context': context,
        'retrieved': arrow.utcnow().to('US/Pacific'),
        'data': returned_data,
    }

    body_json = json.dumps(body, default=stethoscope.utils.json_serialize_datetime)
    try:
      return self.client.index(index=index, doc_type=doc_type, body=body_json)
    except elasticsearch.exceptions.ElasticsearchException:
      logger.exception("Exception logging to Elasticsearch:\n  index: {!r}\n  doc_type: {!r}\n"
                       "  body: {!s}".format(index, doc_type, body_json))
      raise stethoscope.plugins.mixins.es.ElasticSearchException()

  def log(self, record_type, userinfo, target, returned_data, context=None):
    threads.deferToThread(self._log, record_type, userinfo, target, returned_data, context=context)
    return returned_data
