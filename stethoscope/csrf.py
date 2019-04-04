# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import datetime
import hashlib
import json
import random

import logbook
import six
import six.moves.urllib.parse as urlparse
import werkzeug.exceptions
import werkzeug.security

import stethoscope.configurator
import stethoscope.hostchecker


logger = logbook.Logger(__name__)


_MAX_CSRF_KEY = long(2 << 63) if six.PY2 else 2 << 63


MSG_MISSING_REFERER = u'Missing referer.'
MSG_MALFORMED_REFERER = u'Malformed referer.'
MSG_INSECURE_REFERER = u'Insecure referer.'
MSG_BAD_REFERER = u'Bad referer: {!r}.'
MSG_MISSING_TOKEN = u'Anti-CSRF token missing.'
MSG_MISSING_COOKIE = u'Anti-CSRF cookie missing.'
MSG_BAD_TOKEN = u'Anti-CSRF token incorrect.'


urandom = random.SystemRandom()


def generate_token():
  salt = str(urandom.randrange(0, _MAX_CSRF_KEY)).encode('utf-8')
  return hashlib.sha256(salt).hexdigest()


def _same_origin(url1, url2):
  p1, p2 = urlparse.urlparse(url1), urlparse.urlparse(url2)
  origin1 = p1.scheme, p1.hostname, p1.port
  origin2 = p2.scheme, p2.hostname, p2.port
  return origin1 == origin2


class CSRFError(werkzeug.exceptions.Forbidden):
  pass


class CSRFProtection(stethoscope.configurator.Configurator):

  config_keys = tuple()

  def __init__(self, *args, **kwargs):
    super(CSRFProtection, self).__init__(*args, **kwargs)
    self.init_from_config(self.config)

  def init_from_config(self, config):
    self._host_checker = stethoscope.hostchecker.HostChecker(config)

    self._csrf_disable = config.get('CSRF_DISABLE', config.get('TESTING', False))
    self._csrf_check_referer = config.get('CSRF_CHECK_REFERER', True)
    self._csrf_cookie_name = config.get('CSRF_COOKIE_NAME', '_csrf_token')
    self._csrf_input_name = config.get('CSRF_INPUT_NAME', '_csrf_token')
    self._csrf_header_name = config.get('CSRF_HEADER_NAME', 'X-CSRF-Token')
    self._csrf_cookie_secure = config.get('CSRF_COOKIE_SECURE', False)
    self._csrf_cookie_httponly = config.get('CSRF_COOKIE_HTTPONLY', False)
    self._csrf_cookie_timeout = config.get('CSRF_COOKIE_TIMEOUT', datetime.timedelta(days=5))
    self._csrf_cookie_domain = config.get('CSRF_COOKIE_DOMAIN', None)

  def _check_referer(self, request):
    # TODO: consider checking Origin header
    referer = request.getHeader('Referer')
    if referer is None:
      logger.warning("CSRF Error: {:s}", MSG_MISSING_REFERER)
      raise CSRFError(description=MSG_MISSING_REFERER)

    parsed_referer = urlparse.urlparse(referer)
    if parsed_referer.scheme == '' or parsed_referer.netloc == '':
      logger.warning("CSRF Error: {:s} ({!r})", MSG_MALFORMED_REFERER, parsed_referer)
      raise CSRFError(description=MSG_MALFORMED_REFERER)

    if parsed_referer.scheme != 'https':
      logger.warning("CSRF Error: {:s}", MSG_INSECURE_REFERER)
      raise CSRFError(description=MSG_INSECURE_REFERER)

    good_referer = self._csrf_cookie_domain or self._host_checker.get_host(request)

    if not _same_origin(good_referer, referer):
      msg = MSG_BAD_REFERER.format(referer)
      logger.warning("CSRF Error: {:s}", msg)
      raise CSRFError(description=msg)

  def _check_token(self, request):
    request_csrf_token = None

    if request.method == b"POST":
      content = json.loads(request.content.getvalue().decode('utf-8'))
      request_csrf_token = content.get(self._csrf_input_name, None)

    if request_csrf_token is None:
      request_csrf_token = request.getHeader(self._csrf_header_name)

    if request_csrf_token is None:
      logger.warning("CSRF Error: {:s}", MSG_MISSING_TOKEN)
      raise CSRFError(description=MSG_MISSING_TOKEN)

    cookie_csrf_token = request.getCookie(self._csrf_cookie_name)
    if cookie_csrf_token is None:
      logger.warning("CSRF Error: {:s}", MSG_MISSING_COOKIE)
      raise CSRFError(description=MSG_MISSING_COOKIE)

    if not werkzeug.security.safe_str_cmp(request_csrf_token, cookie_csrf_token):
      logger.warning("CSRF Error: {:s}", MSG_BAD_TOKEN)
      raise CSRFError(description=MSG_BAD_TOKEN)

  def validate_request(self, request):
    if self._csrf_disable or request.method in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
      return

    if request.isSecure() and self._csrf_check_referer:
      self._check_referer(request)

    self._check_token(request)

  def csrf_protect(self, func):
    @six.wraps(func)
    def decorator(request, *args, **kwargs):
      self.validate_request(request)
      return func(request, *args, **kwargs)
    return decorator
