# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import logbook

import stethoscope.plugins.utils
from stethoscope.api.endpoints.utils import add_post_route


logger = logbook.Logger(__name__)


def register_feedback_api_endpoints(app, config, auth, csrf, log_hooks=[]):
  feedback_plugins = stethoscope.plugins.utils.instantiate_plugins(config,
      namespace='stethoscope.plugins.feedback')

  if config.get('ENABLE_FEEDBACK_ENDPOINTS', config['DEBUG']) \
      and len(feedback_plugins.names()) > 0:
    feedback_plugins.map(add_post_route, app, config, auth, csrf, 'feedback')
