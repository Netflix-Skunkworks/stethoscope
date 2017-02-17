# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import elasticsearch
import werkzeug.exceptions

import stethoscope.configurator


class ElasticSearchException(werkzeug.exceptions.BadGateway):

  def __init__(self):
    super(ElasticSearchException, self).__init__("Request to external service failed.")


class ElasticSearchMixin(stethoscope.configurator.Configurator):

  config_keys = (
    'ELASTICSEARCH_HOSTS',
    'ELASTICSEARCH_INDEX',
    'ELASTICSEARCH_DOCTYPE',
  )

  def __init__(self, *args, **kwargs):
    super(ElasticSearchMixin, self).__init__(*args, **kwargs)
    kwargs = {
      'verify_certs': True,
    }
    kwargs.update(self.config.get('ELASTICSEARCH_KWARGS', {}))
    self.client = elasticsearch.Elasticsearch(self.config['ELASTICSEARCH_HOSTS'], **kwargs)
