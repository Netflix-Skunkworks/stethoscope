# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import datetime
import functools

import jwt
import logbook
import six
import werkzeug.exceptions

import stethoscope.configurator


logger = logbook.Logger(__name__)


class AuthProvider(stethoscope.configurator.Configurator):
  """Basic auth provider for handling JWTs and HTTP authorization."""

  config_keys = (
    'JWT_SECRET_KEY',
    'JWT_ALGORITHM',
    'JWT_EXPIRATION_DELTA',
  )

  def create_token(self, **kwargs):
    now = datetime.datetime.utcnow()
    claims = {
        'iat': now,
        'nbf': now,
        'exp': now + datetime.timedelta(seconds=self.config['JWT_EXPIRATION_DELTA']),
    }
    claims.update(**kwargs)
    return jwt.encode(claims, self.config['JWT_SECRET_KEY'],
      algorithm=self.config['JWT_ALGORITHM'])

  def decode_token(self, token):
    try:
      decoded = jwt.decode(token, self.config['JWT_SECRET_KEY'],
          algorithms=[self.config['JWT_ALGORITHM']], leeway=self.config.get('JWT_LEEWAY', 0))
    except jwt.ExpiredSignatureError:
      raise werkzeug.exceptions.Unauthorized("JWT Error: Token is expired.")
    except jwt.DecodeError:
      raise werkzeug.exceptions.Unauthorized("JWT Error: Token could not be decoded.")
    except jwt.InvalidTokenError:
      raise werkzeug.exceptions.Unauthorized("JWT Error: Token is invalid.")
    return decoded

  def decode_header_value(self, header_value):
    if header_value is None:
      raise werkzeug.exceptions.Unauthorized("Authorization Required: No authorization provided.")

    parts = header_value.split()

    if len(parts) != 2:
      raise werkzeug.exceptions.BadRequest("Invalid Authorization Header: "
                                           "Header is improperly formatted.")
    elif parts[0] != b'Bearer':
      raise werkzeug.exceptions.BadRequest("Invalid Authorization Header: "
                                           "Authorization type ({!s}) is invalid."
                                           "".format(parts[0]))
    token = self.decode_token(parts[1])

    return token


class KleinAuthProvider(AuthProvider):
  """Provides decorators for use with Klein endpoints."""

  def check_token(self, request):
    token = request.getCookie('token')
    if token is not None:
      # logger.debug("using cookie token...")
      userinfo = self.decode_token(token)
    else:
      # logger.debug("using authorization header...")
      userinfo = self.decode_header_value(request.getHeader('Authorization'))
    return userinfo

  def token_required(self, func=None, callback=None):
    """Decorator for endpoints which require a verified user."""
    # logger.debug("token_required received func={!r}, callback={!r}", func, callback)
    if func is None:
      # called with optional arguments; return value will be called without, so pass them through
      return functools.partial(self.token_required, callback=callback)

    @six.wraps(func)
    def decorator(request, *args, **kwargs):
      userinfo = self.check_token(request)

      kwargs['userinfo'] = userinfo
      args = (request,) + args

      if callback is not None:
        # logger.debug("calling {!r} with args={!r} and kwargs={!r}", callback, args, kwargs)
        callback(*args, **kwargs)

      # logger.debug("calling {!r} with args={!r} and kwargs={!r}", func, args, kwargs)
      return func(*args, **kwargs)

    return decorator

  def match_required(self, func):
    """Decorator for endpoints which require the argument to match the verified user's email."""

    def check_email(request, email, **kwargs):
      userinfo = kwargs.pop('userinfo')

      is_privileged_user = self.config.get('IS_PRIVILEGED_USER', lambda _: False)
      if not self._debug and email != userinfo['sub'] and not is_privileged_user(userinfo):
        raise werkzeug.exceptions.Forbidden("Access Denied: "
                                            "User is not allowed to access resource.")

    return self.token_required(callback=check_email)(func)
