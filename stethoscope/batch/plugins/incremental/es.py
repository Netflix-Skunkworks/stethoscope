# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import json
import pprint

import arrow
import logbook

import stethoscope.plugins.mixins.es
import stethoscope.utils


logger = logbook.Logger(__name__)


class ElasticSearchBatchLogger(stethoscope.plugins.mixins.es.ElasticSearchMixin):

  config_keys = (
    'ELASTICSEARCH_HOSTS',
    'ELASTICSEARCH_INDEX_PREFIX',
    'ELASTICSEARCH_DOCTYPE',
  )

  def post(self, devices, email):
    logger.debug("ELASTICSEARCH: posting {:d} devices", len(devices))
    index = self.config['ELASTICSEARCH_INDEX_PREFIX'] + arrow.now().format("YYYYMM")
    doc_type = self.config['ELASTICSEARCH_DOCTYPE']

    for device in devices:
      device_json = json.dumps(device, default=stethoscope.utils.json_serialize_datetime)
      result = self.client.index(index=index, doc_type=doc_type, body=device_json)
      # TODO: implement error-checking
      logger.debug("Elasticsearch response: {!s}", pprint.pformat(result))
