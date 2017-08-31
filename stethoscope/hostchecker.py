# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import twisted.python.compat
import werkzeug.exceptions
import werkzeug.wsgi

import stethoscope.configurator


class HostChecker(stethoscope.configurator.Configurator):

  config_keys = tuple()

  def __init__(self, *args, **kwargs):
    super(HostChecker, self).__init__(*args, **kwargs)
    self._use_x_forwarded_host = self.config.get('USE_X_FORWARDED_HOST', True)
    self._use_x_forwarded_port = self.config.get('USE_X_FORWARDED_PORT', True)
    self._use_x_forwarded_proto = self.config.get('USE_X_FORWARDED_PROTO', True)

  def _get_raw_port(self, request):
    """Return the port for the request (as an int), taking into account HTTP header values.

    Prefers the value of the `X-Forwarded-Port` header (or, if the header value is a comma-separated
    list, the first value in the list). If not set, defaults to the port the server is listening on.
    """
    if self._use_x_forwarded_port and request.getHeader('X-Forwarded-Port'):
      return int(request.getHeader('X-Forwarded-Port').split(',', 1)[0].strip())
    else:
      return request.getHost().port

  def _get_raw_proto(self, request):
    """Return the protocol ("https" or "http"), taking HTTP header values into account.

    Prefers the value of the `X-Forwarded-Proto` header, if set. If not, defaults to "https" if
    the server is connected via SSL/TLS and "http" otherwise.
    """
    if self._use_x_forwarded_proto and request.getHeader('X-Forwarded-Proto'):
      return request.getHeader('X-Forwarded-Proto')
    else:
      return 'https' if request.isSecure() else 'http'

  def _get_raw_host(self, request):
    """Return the host for the request, taking into account HTTP header values.

    Uses the first of:

    1. If the configuration value `USE_X_FORWARDED_HOST` is set to `True`, the value of the
      `X-Forwarded-Host` header (or, if the header value is a comma-separated list, the first value
      in the list) if set.

    2. The value of the `Host` header, if set.

    3. The host the server is listening on.

    """
    if self._use_x_forwarded_host and request.getHeader('X-Forwarded-Host'):
      return request.getHeader('X-Forwarded-Host').split(',', 1)[0].strip()
    elif request.getHeader('Host'):
      return request.getHeader('Host')
    else:
      host = twisted.python.compat.nativeString(request.getHost().host)
      port = self._get_raw_port(request)
      proto = self._get_raw_proto(request)

      if (proto, port) not in [('https', 443), ('http', 80)]:
        host = '{:s}:{:d}'.format(host, port)

      return host

  def get_host(self, request):
    """Return the (validated) host for the request, taking into account HTTP header values.

    Prefers the value of the `X-Forwarded-Host` header (and corresponding `X-Forwarded-Port`) then
    the `Host` header. If neither is set, defaults to the host (and port) the server is listening
    on.

    Raises `~werkzeug.exceptions.SecurityError` if the `TRUSTED_HOSTS` configuration value is set
    but the host does not match one of it's entries.
    """
    host = self._get_raw_host(request)

    if self.config.get('TRUSTED_HOSTS'):
      if not werkzeug.wsgi.host_is_trusted(host, self.config.get('TRUSTED_HOSTS')):
        raise werkzeug.exceptions.SecurityError('Host "{:s}" is not trusted'.format(host))
    return host
