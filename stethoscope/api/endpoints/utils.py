# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import functools
import json
import pprint

import logbook
import six
import werkzeug.exceptions

import stethoscope.utils
import stethoscope.validation


logger = logbook.Logger(__name__)


def log_error(name, extension_name, response):
  logger.error("error retrieving {:s}(s) from '{:s}':\n{!s}", name, extension_name, response)
  return response


def log_access(record_type, userinfo, target, response, context=None):
  logger.notice("'{!s}' accessed {!s} records{!s} for '{!s}'", userinfo['sub'], record_type,
      " ({!s})".format(context) if context is not None else "", target)
  return response


def log_response(name, extension_name, response, debug=False):
  msg = "retrieved {:d} {:s}(s) from '{:s}'".format(len(response), name, extension_name)
  if debug:
    msg += ":\n{:s}".format(stethoscope.utils.json_pp(response))
  logger.debug(msg)
  return response


def log_post_response(name, extension_name, result, debug=False):
  msg = "posted '{:s}' to '{:s}'".format(name, extension_name)
  if debug:
    msg += ":\n{:s}".format(pprint.pformat(result))
  logger.debug(msg)
  return result


def log_post_error(name, extension_name, result):
  logger.error("error posting '{:s}' to '{:s}':\n{!s}", name, extension_name, result)
  return result


def add_post_route(ext, app, config, auth, csrf, name, **kwargs):
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


def add_get_route(ext, app, auth, name, argname, **kwargs):
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


def serialized_endpoint(*_callbacks):
  """Decorator which wraps an endpoint by applying callbacks to the results then serializing to JSON.

  First, the decorated function is called and must return a `defer.Deferred`. The callbacks supplied
  to the decorator are then applied followed by any callbacks supplied as keyword arguments to the
  decorated function.  The result is then serialized and returned in the response (with
  ``Content-Type`` set to ``application/json``).
  """
  def decorator(func):
    @six.wraps(func)
    def wrapped(request, *args, **kwargs):
      callbacks = kwargs.pop('callbacks', [])
      # logger.debug("in wrapped:\nargs: {!r}\nkwargs: {!r}", args, kwargs)

      deferred_list = func(*args, **kwargs)

      for callback in list(_callbacks) + callbacks:
        deferred_list.addCallback(callback)

      deferred_list.addCallback(json.dumps, default=stethoscope.utils.json_serialize_datetime)
      request.setHeader('Content-Type', 'application/json')
      return deferred_list
    return wrapped
  return decorator
