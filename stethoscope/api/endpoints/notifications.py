# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import functools
from itertools import chain

import logbook
from twisted.internet import defer

import stethoscope.api.endpoints.utils
import stethoscope.plugins.utils
import stethoscope.validation
from stethoscope.api.endpoints.utils import log_response, log_access, add_get_route


logger = logbook.Logger(__name__)


def sort_notifications(notifications):
  # TODO: replace with generic version
  def get_timestamp(notification):
    return notification['_source']['event_timestamp']
  return sorted(notifications, key=get_timestamp, reverse=True)


def merge_notifications(notifications):
  return sort_notifications(chain.from_iterable(notifs for (status, notifs) in notifications if
    status))


def get_notifications_by_email(email, extensions):
  deferreds = []
  for ext in extensions:
    deferred = ext.obj.get_notifications_by_email(email)
    deferred.addCallback(functools.partial(log_response, 'notifications', ext.name))
    deferreds.append(deferred)

  return defer.DeferredList(deferreds, consumeErrors=True)


@stethoscope.api.endpoints.utils.serialized_endpoint(merge_notifications)
def merged_notifications(*args, **kwargs):
  """Endpoint returning (as JSON) all notifications after merging."""
  return get_notifications_by_email(*args, **kwargs)


def register_notification_api_endpoints(app, config, auth, log_hooks=[]):
  notification_plugins = stethoscope.plugins.utils.instantiate_plugins(config,
      namespace='stethoscope.plugins.sources.notifications')

  if config.get('ENABLE_NOTIFICATION_ENDPOINTS', config['DEBUG']) \
      and len(notification_plugins.names()) > 0:
    notification_plugins.map(add_get_route, app, auth, 'notifications', 'email',
                             log_hooks=log_hooks)

  @auth.match_required
  @stethoscope.validation.check_valid_email
  def _merged_notifications(request, email, **_kwargs):
    userinfo = _kwargs.pop('userinfo')

    # required so that app.route can get a '__name__' attribute from decorated function
    _kwargs['callbacks'] = [
      functools.partial(log_response, 'notification', 'merged'),
      functools.partial(log_access, 'notification', userinfo, email, context='merged'),
    ] + [functools.partial(hook.obj.log, 'notification', userinfo, email, context='merged')
        for hook in log_hooks]
    return merged_notifications(request, email, notification_plugins, **_kwargs)
  app.route('/notifications/merged/<string:email>', endpoint='notifications-merged',
      methods=['GET'])(_merged_notifications)
