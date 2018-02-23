# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import functools
import os
import pprint
import sys
from itertools import chain

import flask.config
import klein
import logbook
import treq
from twisted.internet import defer

import stethoscope.api.devices
import stethoscope.api.endpoints.events
import stethoscope.api.endpoints.utils
import stethoscope.api.utils
import stethoscope.auth
import stethoscope.csrf
import stethoscope.plugins.utils
import stethoscope.validation
import stethoscope.api.endpoints.accounts


logger = logbook.Logger(__name__)


def sort_notifications(notifications):
  # TODO: replace with generic version
  def get_timestamp(notification):
    return notification['_source']['event_timestamp']
  return sorted(notifications, key=get_timestamp, reverse=True)


def get_notifications_by_email(email, extensions):
  deferreds = []
  for ext in extensions:
    deferred = ext.obj.get_notifications_by_email(email)
    deferred.addCallback(functools.partial(stethoscope.api.endpoints.utils.log_response, 'notifications', ext.name))
    deferreds.append(deferred)

  return defer.DeferredList(deferreds, consumeErrors=True)


def merge_notifications(notifications):
  return sort_notifications(chain.from_iterable(notifs for (status, notifs) in notifications if
    status))


@stethoscope.api.endpoints.utils.serialized_endpoint(merge_notifications)
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
      deferred.addCallback(functools.partial(stethoscope.api.endpoints.utils.log_response, 'device',
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
      deferred.addCallback(functools.partial(stethoscope.api.endpoints.utils.log_response, 'device',
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
      deferred.addCallback(functools.partial(stethoscope.api.endpoints.utils.log_response, 'device',
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


def register_merged_device_endpoints(app, config, auth, device_plugins, apply_practices,
    transforms, log_hooks=[]):
  """Registers endpoints which provide merged devices without the ownership attribution stage."""

  def setup_endpoint_kwargs(endpoint_type, args, kwargs):
    userinfo = kwargs.pop('userinfo')

    kwargs['callbacks'] = [transform.obj.transform for transform in transforms] + [
      functools.partial(stethoscope.api.endpoints.utils.log_response, 'device', endpoint_type),
      functools.partial(stethoscope.api.endpoints.utils.log_access, 'device', userinfo, *args),
    ] + [functools.partial(hook.obj.log, 'device', userinfo, *args) for hook in log_hooks]

    kwargs.setdefault('debug', config.get('DEBUG', False))
    return kwargs

  @stethoscope.api.endpoints.utils.serialized_endpoint(apply_practices,
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

  @stethoscope.api.endpoints.utils.serialized_endpoint(apply_practices,
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

  @stethoscope.api.endpoints.utils.serialized_endpoint(apply_practices,
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
    predevice_plugins.map(stethoscope.api.endpoints.utils.add_get_route, app, auth, 'devices', 'email', log_hooks=log_hooks)
    predevice_plugins.map(stethoscope.api.endpoints.utils.add_get_route, app, auth, 'devices', 'macaddr', log_hooks=log_hooks)
    predevice_plugins.map(stethoscope.api.endpoints.utils.add_get_route, app, auth, 'devices', 'serial', log_hooks=log_hooks)

  # instantiate the second-stage plugins which provide detailed device data
  device_plugins = stethoscope.plugins.utils.instantiate_plugins(config,
      namespace='stethoscope.plugins.sources.devices')

  if config.get('ENABLE_DEVICE_ENDPOINTS', config['DEBUG']) and len(device_plugins.names()) > 0:
    # individual endpoints for each plugin for device lookup by mac, email, serial
    device_plugins.map(stethoscope.api.endpoints.utils.add_get_route, app, auth, 'devices', 'email', log_hooks=log_hooks)
    device_plugins.map(stethoscope.api.endpoints.utils.add_get_route, app, auth, 'devices', 'macaddr', log_hooks=log_hooks)
    device_plugins.map(stethoscope.api.endpoints.utils.add_get_route, app, auth, 'devices', 'serial', log_hooks=log_hooks)

    # 'merged' endpoints which merge device data across all second-stage device plugins
    # (without the initial ownership-attribution stage) for lookup by mac, email, serial
    register_merged_device_endpoints(app, config, auth, device_plugins, apply_practices,
        transforms=transforms, log_hooks=log_hooks)

  # primary device api endpoint ('merged' or 'staged') which merges device data across all
  # device plugins (both initial and second-stage)
  @stethoscope.api.endpoints.utils.serialized_endpoint(apply_practices,
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
      functools.partial(stethoscope.api.endpoints.utils.log_response, 'device', 'staged'),
      functools.partial(stethoscope.api.endpoints.utils.log_access, 'device', userinfo, email, context='merged'),
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


def register_userinfo_api_endpoints(app, config, auth, log_hooks=[]):
  userinfo_plugins = stethoscope.plugins.utils.instantiate_plugins(config,
      namespace='stethoscope.plugins.sources.userinfo')

  if config['DEBUG']:
    userinfo_plugins.map(stethoscope.api.endpoints.utils.add_get_route, app, auth, 'userinfo', 'email', log_hooks=log_hooks)


def register_notification_api_endpoints(app, config, auth, log_hooks=[]):
  notification_plugins = stethoscope.plugins.utils.instantiate_plugins(config,
      namespace='stethoscope.plugins.sources.notifications')

  if config.get('ENABLE_NOTIFICATION_ENDPOINTS', config['DEBUG']) \
      and len(notification_plugins.names()) > 0:
    notification_plugins.map(stethoscope.api.endpoints.utils.add_get_route, app, auth, 'notifications', 'email', log_hooks=log_hooks)

  @auth.match_required
  @stethoscope.validation.check_valid_email
  def _merged_notifications(request, email, **_kwargs):
    userinfo = _kwargs.pop('userinfo')

    # required so that app.route can get a '__name__' attribute from decorated function
    _kwargs['callbacks'] = [
      functools.partial(stethoscope.api.endpoints.utils.log_response, 'notification', 'merged'),
      functools.partial(stethoscope.api.endpoints.utils.log_access, 'notification', userinfo, email, context='merged'),
    ] + [functools.partial(hook.obj.log, 'notification', userinfo, email, context='merged')
        for hook in log_hooks]
    return merged_notifications(request, email, notification_plugins, **_kwargs)
  app.route('/notifications/merged/<string:email>', endpoint='notifications-merged',
      methods=['GET'])(_merged_notifications)


def register_feedback_api_endpoints(app, config, auth, csrf, log_hooks=[]):
  feedback_plugins = stethoscope.plugins.utils.instantiate_plugins(config,
      namespace='stethoscope.plugins.feedback')

  if config.get('ENABLE_FEEDBACK_ENDPOINTS', config['DEBUG']) \
      and len(feedback_plugins.names()) > 0:
    feedback_plugins.map(stethoscope.api.endpoints.utils.add_post_route, app, config, auth, csrf, 'feedback')


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
    stethoscope.api.endpoints.events.register_event_api_endpoints(app, config, auth, log_hooks=log_hooks)
    stethoscope.api.endpoints.accounts.register_account_api_endpoints(app, config, auth, log_hooks=log_hooks)
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
