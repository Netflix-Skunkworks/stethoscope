# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import functools
import pprint
import sys
from itertools import chain

import logbook
from twisted.internet import defer

import stethoscope.api.devices
import stethoscope.api.endpoints.utils
import stethoscope.api.utils
import stethoscope.plugins.utils
import stethoscope.validation
from stethoscope.api.endpoints.utils import log_response, log_access, add_get_route


logger = logbook.Logger(__name__)


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
    predevice_plugins.map(add_get_route, app, auth, 'devices', 'email', log_hooks=log_hooks)
    predevice_plugins.map(add_get_route, app, auth, 'devices', 'macaddr', log_hooks=log_hooks)
    predevice_plugins.map(add_get_route, app, auth, 'devices', 'serial', log_hooks=log_hooks)

  # instantiate the second-stage plugins which provide detailed device data
  device_plugins = stethoscope.plugins.utils.instantiate_plugins(config,
      namespace='stethoscope.plugins.sources.devices')

  if config.get('ENABLE_DEVICE_ENDPOINTS', config['DEBUG']) and len(device_plugins.names()) > 0:
    # individual endpoints for each plugin for device lookup by mac, email, serial
    device_plugins.map(add_get_route, app, auth, 'devices', 'email', log_hooks=log_hooks)
    device_plugins.map(add_get_route, app, auth, 'devices', 'macaddr', log_hooks=log_hooks)
    device_plugins.map(add_get_route, app, auth, 'devices', 'serial', log_hooks=log_hooks)

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
