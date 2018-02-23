# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import functools
import json
import operator
import os
import pprint
import sys
from itertools import chain

import flask.config
import klein
import logbook
import treq
import werkzeug.exceptions
from twisted.internet import defer

import stethoscope.api.devices
import stethoscope.api.endpoints
import stethoscope.api.utils
import stethoscope.auth
import stethoscope.csrf
import stethoscope.plugins.utils
import stethoscope.utils
import stethoscope.validation


logger = logbook.Logger(__name__)


def log_response(name, extension_name, response, debug=False):
  msg = "retrieved {:d} {:s}(s) from '{:s}'".format(len(response), name, extension_name)
  if debug:
    msg += ":\n{:s}".format(stethoscope.utils.json_pp(response))
  logger.debug(msg)
  return response


def log_error(name, extension_name, response):
  logger.error("error retrieving {:s}(s) from '{:s}':\n{!s}", name, extension_name, response)
  return response


def log_access(record_type, userinfo, target, response, context=None):
  logger.notice("'{!s}' accessed {!s} records{!s} for '{!s}'", userinfo['sub'], record_type,
      " ({!s})".format(context) if context is not None else "", target)
  return response


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


@stethoscope.api.endpoints.serialized_endpoint(merge_events)
def merged_events(*args, **kwargs):
  """Endpoint returning (as JSON) all events after merging."""
  return get_events_by_email(*args, **kwargs)


def get_accounts_by_email(email, extensions):
  deferreds = []
  for ext in extensions:
    deferred = ext.obj.get_account_by_email(email)
    deferred.addCallback(functools.partial(log_response, 'account', ext.name))
    deferreds.append(deferred)

  return defer.DeferredList(deferreds, consumeErrors=True)


def merge_accounts(accts):
  return list(acct for (status, acct) in accts if status)


@stethoscope.api.endpoints.serialized_endpoint(merge_accounts)
def merged_accounts(*args, **kwargs):
  """Endpoint returning (as JSON) all accounts after merging."""
  return get_accounts_by_email(*args, **kwargs)


def sort_notifications(notifications):
  # TODO: replace with generic version
  def get_timestamp(notification):
    return notification['_source']['event_timestamp']
  return sorted(notifications, key=get_timestamp, reverse=True)


def get_notifications_by_email(email, extensions):
  deferreds = []
  for ext in extensions:
    deferred = ext.obj.get_notifications_by_email(email)
    deferred.addCallback(functools.partial(log_response, 'notifications', ext.name))
    deferreds.append(deferred)

  return defer.DeferredList(deferreds, consumeErrors=True)


def merge_notifications(notifications):
  return sort_notifications(chain.from_iterable(notifs for (status, notifs) in notifications if
    status))


@stethoscope.api.endpoints.serialized_endpoint(merge_notifications)
def merged_notifications(*args, **kwargs):
  """Endpoint returning (as JSON) all notifications after merging."""
  return get_notifications_by_email(*args, **kwargs)


def get_devices_by_email(email, extensions, debug=False):
  """Returns all devices matching given email."""
  deferreds = []
  for ext in extensions:
    if hasattr(ext.obj, 'get_devices_by_email'):
      deferred = ext.obj.get_devices_by_email(email)
      deferred.addErrback(stethoscope.api.utils.check_user_not_found)
      deferred.addCallback(functools.partial(log_response, 'device',
        ext.name + " ({!s})".format(email), debug=debug))
      deferreds.append(deferred)

  deferred_list = defer.DeferredList(deferreds, consumeErrors=True)
  deferred_list.addCallback(functools.partial(stethoscope.api.utils.filter_keyed_by_status,
    ["{!s}({!s})".format(ext.name, email) for ext in extensions],
    context=sys._getframe().f_code.co_name))
  deferred_list.addCallback(lambda d: chain.from_iterable(d.values()))
  deferred_list.addCallback(list)
  return deferred_list


def get_devices_by_macaddr(macaddr, extensions, debug=False):
  """Returns all devices matching given MAC address."""
  deferreds = []
  for ext in extensions:
    if hasattr(ext.obj, 'get_devices_by_macaddr'):
      deferred = ext.obj.get_devices_by_macaddr(macaddr)
      deferred.addErrback(stethoscope.api.utils.check_device_not_found)
      deferred.addCallback(functools.partial(log_response, 'device',
        ext.name + " ({!s})".format(macaddr), debug=debug))
      deferreds.append(deferred)

  deferred_list = defer.DeferredList(deferreds, consumeErrors=True)
  deferred_list.addCallback(functools.partial(stethoscope.api.utils.filter_keyed_by_status,
    ["{!s}({!s})".format(ext.name, macaddr) for ext in extensions],
    context=sys._getframe().f_code.co_name))
  deferred_list.addCallback(lambda d: chain.from_iterable(d.values()))
  deferred_list.addCallback(list)
  return deferred_list


def get_devices_by_serial(serial, extensions, debug=False):
  """Returns all devices matching given serial number."""
  deferreds = []
  for ext in extensions:
    if hasattr(ext.obj, 'get_devices_by_serial'):
      deferred = ext.obj.get_devices_by_serial(serial)
      deferred.addErrback(stethoscope.api.utils.check_device_not_found)
      deferred.addCallback(functools.partial(log_response, 'device',
        ext.name + " ({!s})".format(serial), debug=debug))
      deferreds.append(deferred)

  deferred_list = defer.DeferredList(deferreds, consumeErrors=True)
  deferred_list.addCallback(functools.partial(stethoscope.api.utils.filter_keyed_by_status,
    ["{!s}({!s})".format(ext.name, serial) for ext in extensions],
    context=sys._getframe().f_code.co_name))
  deferred_list.addCallback(lambda d: chain.from_iterable(d.values()))
  deferred_list.addCallback(list)
  return deferred_list


def _get_devices_by_serials(serials, extensions, debug=False):
  deferred_list = defer.DeferredList([get_devices_by_serial(serial, extensions, debug=debug) for
    serial in serials], consumeErrors=True)
  deferred_list.addCallback(functools.partial(stethoscope.api.utils.filter_keyed_by_status,
    serials, context=sys._getframe().f_code.co_name))
  deferred_list.addCallback(lambda d: chain.from_iterable(d.values()))
  deferred_list.addCallback(list)
  return deferred_list


def _get_devices_by_macaddrs(macaddrs, extensions, debug=False):
  deferred_list = defer.DeferredList([get_devices_by_macaddr(macaddr, extensions, debug=debug) for
    macaddr in macaddrs], consumeErrors=True)
  deferred_list.addCallback(functools.partial(stethoscope.api.utils.filter_keyed_by_status,
    macaddrs, context=sys._getframe().f_code.co_name))
  deferred_list.addCallback(lambda d: chain.from_iterable(d.values()))
  deferred_list.addCallback(list)
  return deferred_list


def apply_device_transforms(devices, transforms):
  for transform in transforms:
    devices = transform.obj.transform(devices)
  return devices


@defer.inlineCallbacks
def get_devices_by_stages(email, pre_extensions, extensions, transforms, debug=False):
  """Return all devices found via two-stage lookup process.

  First, lookup the user in `pre_extensions` by email address. Retrieve all relevant devices and
  extract serials numbers. Merge the results of looking up the serial numbers in compatible
  extensions (from `extensions`) with those from looking up the user's devices in `extensions` by
  email address.
  """
  email_devices_deferred = get_devices_by_email(email, extensions, debug=debug)
  pre_devices = yield get_devices_by_email(email, pre_extensions, debug=debug)
  pre_devices = apply_device_transforms(pre_devices, transforms)

  logger.debug("[{!s}] retrieved {:d} pre-devices", email, len(pre_devices))

  serials = set()
  macaddrs = set()
  for device in pre_devices:
    identifiers = device.get('identifiers', {})
    if 'serial' in identifiers:
      serials.add(identifiers['serial'])
    if 'mac_addresses' in identifiers:
      for macaddr in identifiers['mac_addresses']:
        macaddrs.add(stethoscope.validation.canonicalize_macaddr(macaddr))

  logger.debug("[{!s}] {:d} serials: {!s}", email, len(serials), serials)
  logger.debug("[{!s}] {:d} macaddrs: {!s}", email, len(macaddrs), macaddrs)

  serial_devices_deferred = _get_devices_by_serials(serials, extensions, debug=debug)
  macaddr_devices_deferred = _get_devices_by_macaddrs(macaddrs, extensions, debug=debug)

  deferred_list = defer.DeferredList([defer.succeed(pre_devices), email_devices_deferred,
    serial_devices_deferred, macaddr_devices_deferred], consumeErrors=True)
  deferred_list.addCallback(stethoscope.api.utils.filter_by_status,
      context=sys._getframe().f_code.co_name)
  deferred_list.addCallback(chain.from_iterable)
  deferred_list.addCallback(list)

  devices = yield deferred_list
  logger.info("[{!s}] retrieved {:d} devices", email, len(devices))

  defer.returnValue(devices)


def _add_route(ext, app, auth, name, argname, **kwargs):
  """Add a GET route to Klein app `app` which calls `ext.obj.get_{name}`.

  The route takes the form `/{name}/{ext.name}/<string:email>`, e.g.,
  `/devices/google/<string:email>`.
  """
  method_name = 'get_' + name + "_by_" + argname
  if not hasattr(ext.obj, method_name):
    return None

  callbacks = kwargs.pop('callbacks', [])
  log_hooks = kwargs.pop('log_hooks', [])

  @auth.match_required
  @getattr(stethoscope.validation, 'check_valid_' + argname)
  def _get(request, arg, **kwargs):
    """Return a `Deferred` which calls an extension'a `get_{name}` method with the given `email`
    and gives the result as a JSON resource."""
    userinfo = kwargs.pop('userinfo')
    if len(kwargs) > 0:
      raise werkzeug.exceptions.BadRequest("unexpected parameters: {:s}",
          stethoscope.utils.html_escape(str(kwargs)))

    deferred = getattr(ext.obj, method_name)(arg)
    deferred.addCallback(functools.partial(log_response, name, ext.name))
    # deferred.addCallback(functools.partial(log_access, name, userinfo, arg, context=ext.name))
    for hook in log_hooks:
      deferred.addCallback(functools.partial(hook.obj.log, name, userinfo, arg, context=ext.name))
    deferred.addErrback(functools.partial(log_error, name, ext.name))

    for callback in callbacks:
      deferred.addCallback(callback)

    deferred.addCallback(json.dumps, default=stethoscope.utils.json_serialize_datetime)
    request.setHeader('Content-Type', 'application/json')
    return deferred

  # note: setting the endpoint manually is necessary for Klein to direct flows properly
  kwargs['endpoint'] = '-'.join([name, ext.name, argname])
  kwargs.setdefault('methods', ['GET'])

  url = '/' + '/'.join([name, ext.name, argname, '<string:{:s}>'.format(argname)])

  logger.debug("registering extension:\n  extension: {!r}\n  object: {!r}\n  function: {!r}\n"
               "  url: {!r}\n  kwargs: {!r}".format(ext, ext.obj, _get, url, kwargs))
  app.route(url, **kwargs)(_get)


def register_merged_device_endpoints(app, config, auth, device_plugins, apply_practices,
    transforms, log_hooks=[]):
  """Registers endpoints which provide merged devices without the ownership attribution stage."""

  def setup_endpoint_kwargs(endpoint_type, args, kwargs):
    userinfo = kwargs.pop('userinfo')

    kwargs['callbacks'] = [transform.obj.transform for transform in transforms] + [
      functools.partial(log_response, 'device', endpoint_type),
      functools.partial(log_access, 'device', userinfo, *args),
    ] + [functools.partial(hook.obj.log, 'device', userinfo, *args) for hook in log_hooks]

    kwargs.setdefault('debug', config.get('DEBUG', False))
    return kwargs

  @stethoscope.api.endpoints.serialized_endpoint(apply_practices,
                                                 stethoscope.api.devices.merge_devices)
  def merged_devices_by_email(*args, **kwargs):
    """Endpoint returning (as JSON) all devices for given email after merging."""
    return get_devices_by_email(*args, **kwargs)

  @auth.match_required
  @stethoscope.validation.check_valid_email
  def __get_devices_by_email(request, email, **_kwargs):
    # actual function is required so that app.route can get a '__name__' attribute
    _kwargs = setup_endpoint_kwargs('email', (email,), _kwargs)
    return merged_devices_by_email(request, email, device_plugins, **_kwargs)
  app.route('/devices/email/<string:email>', endpoint='devices-email',
      methods=['GET'])(__get_devices_by_email)

  @stethoscope.api.endpoints.serialized_endpoint(apply_practices,
                                                 stethoscope.api.devices.merge_devices)
  def merged_devices_by_serial(*args, **kwargs):
    """Endpoint returning (as JSON) all devices for given serial after merging."""
    return get_devices_by_serial(*args, **kwargs)

  @auth.token_required
  @stethoscope.validation.check_valid_serial
  def __get_devices_by_serial(request, serial, **_kwargs):
    # actual function is required so that app.route can get a '__name__' attribute
    _kwargs = setup_endpoint_kwargs('serial', (serial,), _kwargs)
    return merged_devices_by_serial(request, serial, device_plugins, **_kwargs)
  app.route('/devices/serial/<string:serial>', endpoint='devices-serial',
      methods=['GET'])(__get_devices_by_serial)

  @stethoscope.api.endpoints.serialized_endpoint(apply_practices,
                                                 stethoscope.api.devices.merge_devices)
  def merged_devices_by_macaddr(*args, **kwargs):
    """Endpoint returning (as JSON) all devices for given macaddr after merging."""
    return get_devices_by_macaddr(*args, **kwargs)

  @auth.token_required
  @stethoscope.validation.check_valid_macaddr
  def __get_devices_by_macaddr(request, macaddr, **_kwargs):
    # actual function is required so that app.route can get a '__name__' attribute
    _kwargs = setup_endpoint_kwargs('macaddr', (macaddr,), _kwargs)
    return merged_devices_by_macaddr(request, macaddr, device_plugins, **_kwargs)
  app.route('/devices/macaddr/<string:macaddr>', endpoint='devices-macaddr',
      methods=['GET'])(__get_devices_by_macaddr)


def register_device_api_endpoints(app, config, auth, log_hooks=[]):
  practices = stethoscope.plugins.utils.instantiate_practices(config,
      namespace='stethoscope.plugins.practices.devices')

  # for use by endpoints to apply each practice to each device
  def apply_practices(devices):
    for device in devices:
      practices.map_method('inject_status', device)
    return devices

  # transforms to apply to device lists
  transforms = stethoscope.plugins.utils.instantiate_plugins(config,
      namespace='stethoscope.plugins.transform.devices')

  # initial-stage plugins provide ownership attribution
  predevice_plugins = stethoscope.plugins.utils.instantiate_plugins(config,
      namespace='stethoscope.plugins.sources.predevices')

  if config.get('ENABLE_PREDEVICE_ENDPOINTS', config['DEBUG']) and \
      len(predevice_plugins.names()) > 0:
    # individual endpoints for each plugin for device lookup by mac, email, serial
    predevice_plugins.map(_add_route, app, auth, 'devices', 'email', log_hooks=log_hooks)
    predevice_plugins.map(_add_route, app, auth, 'devices', 'macaddr', log_hooks=log_hooks)
    predevice_plugins.map(_add_route, app, auth, 'devices', 'serial', log_hooks=log_hooks)

  # instantiate the second-stage plugins which provide detailed device data
  device_plugins = stethoscope.plugins.utils.instantiate_plugins(config,
      namespace='stethoscope.plugins.sources.devices')

  if config.get('ENABLE_DEVICE_ENDPOINTS', config['DEBUG']) and len(device_plugins.names()) > 0:
    # individual endpoints for each plugin for device lookup by mac, email, serial
    device_plugins.map(_add_route, app, auth, 'devices', 'email', log_hooks=log_hooks)
    device_plugins.map(_add_route, app, auth, 'devices', 'macaddr', log_hooks=log_hooks)
    device_plugins.map(_add_route, app, auth, 'devices', 'serial', log_hooks=log_hooks)

    # 'merged' endpoints which merge device data across all second-stage device plugins
    # (without the initial ownership-attribution stage) for lookup by mac, email, serial
    register_merged_device_endpoints(app, config, auth, device_plugins, apply_practices,
        transforms=transforms, log_hooks=log_hooks)

  # primary device api endpoint ('merged' or 'staged') which merges device data across all
  # device plugins (both initial and second-stage)
  @stethoscope.api.endpoints.serialized_endpoint(apply_practices,
                                                 stethoscope.api.devices.merge_devices)
  def merged_devices_by_stages(*args, **kwargs):
    """Endpoint returning (as JSON) all devices for given email (including second-stage lookups)."""
    return get_devices_by_stages(*args, **kwargs)

  @auth.match_required
  @stethoscope.validation.check_valid_email
  def __get_devices_by_stages(request, email, **_kwargs):
    userinfo = _kwargs.pop('userinfo')

    # required so that app.route can get a '__name__' attribute from decorated function
    _kwargs['callbacks'] = [transform.obj.transform for transform in transforms] + [
      functools.partial(log_response, 'device', 'staged'),
      functools.partial(log_access, 'device', userinfo, email, context='merged'),
    ] + [functools.partial(hook.obj.log, 'device', userinfo, email, context='merged')
        for hook in log_hooks]
    logger.debug("callbacks:\n{!s}", pprint.pformat(_kwargs['callbacks']))
    _kwargs.setdefault('debug', config.get('DEBUG', False))
    return merged_devices_by_stages(request, email, predevice_plugins, device_plugins, transforms,
        **_kwargs)
  app.route('/devices/staged/<string:email>', endpoint='devices-staged',
      methods=['GET'])(__get_devices_by_stages)
  app.route('/devices/merged/<string:email>', endpoint='devices-merged',
      methods=['GET'])(__get_devices_by_stages)


def register_event_api_endpoints(app, config, auth, log_hooks=[]):
  event_plugins = stethoscope.plugins.utils.instantiate_plugins(config,
      namespace='stethoscope.plugins.sources.events')

  if config.get('ENABLE_EVENT_ENDPOINTS', config['DEBUG']) and len(event_plugins.names()) > 0:
    event_plugins.map(_add_route, app, auth, 'events', 'email', callbacks=[sort_events],
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


def register_userinfo_api_endpoints(app, config, auth, log_hooks=[]):
  userinfo_plugins = stethoscope.plugins.utils.instantiate_plugins(config,
      namespace='stethoscope.plugins.sources.userinfo')

  if config['DEBUG']:
    userinfo_plugins.map(_add_route, app, auth, 'userinfo', 'email', log_hooks=log_hooks)


def register_account_api_endpoints(app, config, auth, log_hooks=[]):
  account_plugins = stethoscope.plugins.utils.instantiate_plugins(config,
      namespace='stethoscope.plugins.sources.accounts')

  if config.get('ENABLE_ACCOUNT_ENDPOINTS', config['DEBUG']) and len(account_plugins.names()) > 0:
    account_plugins.map(_add_route, app, auth, 'account', 'email', log_hooks=log_hooks)

  @auth.match_required
  @stethoscope.validation.check_valid_email
  def _merged_accounts(request, email, **_kwargs):
    userinfo = _kwargs.pop('userinfo')

    # required so that app.route can get a '__name__' attribute from decorated function
    _kwargs['callbacks'] = [
      functools.partial(log_response, 'account', 'merged'),
      functools.partial(log_access, 'account', userinfo, email, context='merged'),
    ] + [functools.partial(hook.obj.log, 'account', userinfo, email, context='merged')
        for hook in log_hooks]
    return merged_accounts(request, email, account_plugins, **_kwargs)
  app.route('/accounts/merged/<string:email>', endpoint='accounts-merged',
      methods=['GET'])(_merged_accounts)


def register_notification_api_endpoints(app, config, auth, log_hooks=[]):
  notification_plugins = stethoscope.plugins.utils.instantiate_plugins(config,
      namespace='stethoscope.plugins.sources.notifications')

  if config.get('ENABLE_NOTIFICATION_ENDPOINTS', config['DEBUG']) \
      and len(notification_plugins.names()) > 0:
    notification_plugins.map(_add_route, app, auth, 'notifications', 'email', log_hooks=log_hooks)

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


def log_post_response(name, extension_name, result, debug=False):
  msg = "posted '{:s}' to '{:s}'".format(name, extension_name)
  if debug:
    msg += ":\n{:s}".format(pprint.pformat(result))
  logger.debug(msg)
  return result


def log_post_error(name, extension_name, result):
  logger.error("error posting '{:s}' to '{:s}':\n{!s}", name, extension_name, result)
  return result


def _add_post_route(ext, app, config, auth, csrf, name, **kwargs):
  method_name = 'post_' + name
  if not hasattr(ext.obj, method_name):
    return None

  callbacks = kwargs.pop('callbacks', [])
  # log_hooks = kwargs.pop('log_hooks', [])

  @auth.token_required  # TODO: consider auth
  @csrf.csrf_protect
  def _post(request, **kwargs):
    """Return a `Deferred` which calls an extension'a `post_{name}` method with the POST data
    and gives the result as a JSON resource."""
    userinfo = kwargs.pop('userinfo')
    if len(kwargs) > 0:
      raise werkzeug.exceptions.BadRequest("unexpected parameters: {:s}",
          stethoscope.utils.html_escape(str(kwargs)))

    content = json.loads(request.content.getvalue().decode('utf-8'))
    deferred = getattr(ext.obj, method_name)(userinfo['sub'], content)
    deferred.addCallback(functools.partial(log_post_response, name, ext.name))
    deferred.addErrback(functools.partial(log_post_error, name, ext.name))

    for callback in callbacks:
      deferred.addCallback(callback)

    deferred.addCallback(json.dumps, default=stethoscope.utils.json_serialize_datetime)
    request.setHeader('Content-Type', 'application/json')
    return deferred

  # note: setting the endpoint manually is necessary for Klein to direct flows properly
  kwargs['endpoint'] = '-'.join([name, ext.name])
  kwargs.setdefault('methods', ['POST'])

  url = '/' + '/'.join([name, ext.name])

  logger.debug("registering extension:\n  extension: {!r}\n  object: {!r}\n  function: {!r}\n"
               "  url: {!r}\n  kwargs: {!r}".format(ext, ext.obj, _post, url, kwargs))
  app.route(url, **kwargs)(_post)


def register_feedback_api_endpoints(app, config, auth, csrf, log_hooks=[]):
  feedback_plugins = stethoscope.plugins.utils.instantiate_plugins(config,
      namespace='stethoscope.plugins.feedback')

  if config.get('ENABLE_FEEDBACK_ENDPOINTS', config['DEBUG']) \
      and len(feedback_plugins.names()) > 0:
    feedback_plugins.map(_add_post_route, app, config, auth, csrf, 'feedback')


def get_config():
  config = flask.config.Config(os.environ.get('STETHOSCOPE_API_INSTANCE_PATH', './instance/'))

  # load default config from package
  config.from_object('stethoscope.api.defaults')

  # load config specified via env var
  # should be absolute path to a config file
  config.from_envvar('STETHOSCOPE_API_CONFIG', silent=True)

  # load instance config (config.py from instance/)
  config.from_pyfile('config.py')

  return config


def register_error_handlers(app, config, auth):
  plugins = stethoscope.plugins.utils.instantiate_plugins(config,
      namespace='stethoscope.plugins.logging.failure')
  logger.debug("loaded failure logging plugins: {!r}", [hook.name for hook in plugins])

  @app.handle_errors(Exception)
  def check_authorization(request, failure):
    logger.error("Exception while handling request:\n{!s}\n{:s}", request, failure.getTraceback())

    # log to, e.g., a metrics backend like atlas
    for plugin in plugins:
      plugin.obj.log_failure(request, failure)

    # does this lead to infinite recursion?
    # will raise AuthError if token is invalid
    auth.check_token(request)
    return failure


@defer.inlineCallbacks
def check_upstream_response(response, request):
  content = yield treq.content(response)
  if response.code != 200:
    request.setResponseCode(502)
    defer.returnValue("Upstream response code: {:d}\n{!s}".format(response.code, content))
  else:
    defer.returnValue(content)


def handle_upstream_error(failure, request):
  request.setResponseCode(502)
  logger.error("Error connecting to upstream: {!s}\n{:s}", failure.value, failure.getTraceback())
  return "Error connecting to upstream:\n{:s}".format(failure.getErrorMessage())


def register_endpoints(app, config, auth, csrf):
  @app.route('/healthcheck')
  def healthcheck(request):
    upstream = 'http://{!s}/healthcheck'.format(os.getenv("STETHOSCOPE_LOGIN_HOST",
      "127.0.0.1:5002"))
    deferred = treq.get(upstream, timeout=0.1, headers={'Host': request.getHost().host})
    deferred.addCallback(check_upstream_response, request)
    deferred.addErrback(handle_upstream_error, request)
    return deferred

  # gather hooks to external loggers
  log_hooks = stethoscope.plugins.utils.instantiate_plugins(config,
      namespace='stethoscope.plugins.logging.request')
  logger.debug("loaded request logging hooks: {!r}", [hook.name for hook in log_hooks])

  with app.subroute('/api/v1'):
    register_device_api_endpoints(app, config, auth, log_hooks=log_hooks)
    register_event_api_endpoints(app, config, auth, log_hooks=log_hooks)
    register_account_api_endpoints(app, config, auth, log_hooks=log_hooks)
    register_notification_api_endpoints(app, config, auth, log_hooks=log_hooks)
    register_feedback_api_endpoints(app, config, auth, csrf, log_hooks=log_hooks)
    # temporarily disabled: userinfo is not in use
    # register_userinfo_api_endpoints(app, config, auth, log_hooks=log_hooks)


def create_app():
  config = get_config()

  config['LOGBOOK'].push_application()

  if "PLUGINS" not in config or len(config["PLUGINS"]) < 1:
    logger.warn("Missing or invalid PLUGINS configuration!")

  app = klein.Klein()
  auth = stethoscope.auth.KleinAuthProvider(config)
  csrf = stethoscope.csrf.CSRFProtection(config)

  register_error_handlers(app, config, auth)
  register_endpoints(app, config, auth, csrf)

  logger.info("Shields up, weapons online.")

  return app
