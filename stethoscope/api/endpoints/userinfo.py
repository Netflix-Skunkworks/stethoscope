# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import logbook

import stethoscope.plugins.utils
from stethoscope.api.endpoints.utils import add_get_route


logger = logbook.Logger(__name__)


def register_userinfo_api_endpoints(app, config, auth, log_hooks=[]):
  userinfo_plugins = stethoscope.plugins.utils.instantiate_plugins(config,
      namespace='stethoscope.plugins.sources.userinfo')

  if config['DEBUG']:
    userinfo_plugins.map(add_get_route, app, auth, 'userinfo', 'email', log_hooks=log_hooks)
