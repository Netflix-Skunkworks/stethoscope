# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import functools
import operator
from itertools import chain

import logbook
from twisted.internet import defer

import stethoscope.api.endpoints.utils
import stethoscope.plugins.utils
import stethoscope.validation
from stethoscope.api.endpoints.utils import log_response, log_access, add_get_route


logger = logbook.Logger(__name__)


def sort_events(events):
  return sorted(events, key=operator.itemgetter('timestamp'), reverse=True)


def merge_events(events):
  return sort_events(chain.from_iterable(_events for (status, _events) in events if status))


def get_events_by_email(email, extensions):
  deferreds = []
  for ext in extensions:
    deferred = ext.obj.get_events_by_email(email)
    deferred.addCallback(functools.partial(log_response, 'event', ext.name))
    deferreds.append(deferred)

  return defer.DeferredList(deferreds, consumeErrors=True)


@stethoscope.api.endpoints.utils.serialized_endpoint(merge_events)
def merged_events(*args, **kwargs):
  """Endpoint returning (as JSON) all events after merging."""
  return get_events_by_email(*args, **kwargs)


def register_event_api_endpoints(app, config, auth, log_hooks=[]):
  event_plugins = stethoscope.plugins.utils.instantiate_plugins(config,
      namespace='stethoscope.plugins.sources.events')

  if config.get('ENABLE_EVENT_ENDPOINTS', config['DEBUG']) and len(event_plugins.names()) > 0:
    event_plugins.map(add_get_route, app, auth, 'events', 'email', callbacks=[sort_events],
        log_hooks=log_hooks)

  # gather hooks to transform events (e.g., by adding geolocation data)
  hooks = stethoscope.plugins.utils.instantiate_plugins(config,
      namespace='stethoscope.plugins.transform.events')

  @auth.match_required
  @stethoscope.validation.check_valid_email
  def _merged_events(request, email, **_kwargs):
    userinfo = _kwargs.pop('userinfo')

    # required so that app.route can get a '__name__' attribute from decorated function
    _kwargs['callbacks'] = [hook.obj.transform for hook in hooks] + [
      functools.partial(log_response, 'event', 'merged'),
      functools.partial(log_access, 'event', userinfo, email, context='merged'),
    ] + [functools.partial(hook.obj.log, 'event', userinfo, email, context='merged')
        for hook in log_hooks]
    return merged_events(request, email, event_plugins, **_kwargs)
  app.route('/events/merged/<string:email>', endpoint='events-merged',
      methods=['GET'])(_merged_events)
