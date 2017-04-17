# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import datetime
import json

from klein.resource import KleinResource
from klein.test.test_resource import requestMock, _render
from twisted.trial import unittest
import jwt
import klein
import logbook
import mock
import pytest
import twisted.web.http
import werkzeug.exceptions

import stethoscope.auth


logger = logbook.Logger(__name__)

JWT_ALGORITHM = 'HS256'
JWT_SECRET_KEY = 'sekret'


def get_auth_provider(**kwargs):
  values = {
    'DEBUG': True,
    'TESTING': True,
    'JWT_SECRET_KEY': JWT_SECRET_KEY,
    'JWT_ALGORITHM': JWT_ALGORITHM,
    'JWT_EXPIRATION_DELTA': 60,
  }
  values.update(kwargs)

  return stethoscope.auth.KleinAuthProvider(values)


class BaseAuthTestCase(unittest.TestCase):

  def setUp(self):
    self.auth = get_auth_provider()

  def check_decoded(self, decoded, claims=('sub', 'iat', 'nbf', 'exp')):
    for claim in claims:
      self.assertIn(claim, decoded, "{!r} missing".format(claim))
    self.assertEqual(decoded['sub'], 'user@example.com')

    for claim in claims:
      del decoded[claim]
    self.assertEqual(len(decoded), 0)


class DecoratorsHeaderTestCase(BaseAuthTestCase):
  """Tests that the auth-related decorators properly wrap decorated functions."""

  def setUp(self):
    """Mock up a provider that just returns a test value for the decoded header value."""
    super(DecoratorsHeaderTestCase, self).setUp()
    self.auth.decode_header_value = mock.create_autospec(self.auth.decode_header_value)
    self.auth.decode_header_value.return_value = {'sub': 'user@example.com'}

  def test_token_required_injects(self):
    """Tests that the token value is appended to the wrapped function's arguments."""
    @self.auth.token_required
    def wrapped(request, userinfo):
      return userinfo

    request = mock.create_autospec(twisted.web.http.Request)
    request.getCookie.return_value = None
    self.assertEqual(wrapped(request), {'sub': 'user@example.com'})

  def test_match_required_injects(self):
    """Tests both that the token value is injected and that that value matches the given email."""
    @self.auth.match_required
    def wrapped(request, userinfo, email=None):
      return userinfo

    request = mock.create_autospec(twisted.web.http.Request)
    request.getCookie.return_value = None
    self.assertEqual(wrapped(request, email='user@example.com'), {'sub': 'user@example.com'})

  def test_match_required_raises(self):
    """Tests that an exception is raised if the token's value doesn't match the given email."""
    @self.auth.match_required
    def wrapped(request, userinfo, email=None):
      return userinfo

    request = mock.create_autospec(twisted.web.http.Request)
    request.getCookie.return_value = None
    with pytest.raises(werkzeug.exceptions.Forbidden):
      with mock.patch.object(self.auth, '_debug', False):  # ensure check actually happens
        wrapped(request, email='baduser@example.com')


class DecoratorsCookieTestCase(BaseAuthTestCase):
  """Tests that the auth-related decorators properly wrap decorated functions."""

  def setUp(self):
    """Mock up a provider that just returns a test value for the decoded header value."""
    super(DecoratorsCookieTestCase, self).setUp()
    self.auth.decode_token = mock.create_autospec(self.auth.decode_token)
    self.auth.decode_token.return_value = {'sub': 'user@example.com'}

  def test_token_required_injects(self):
    """Tests that the token value is appended to the wrapped function's arguments."""
    @self.auth.token_required
    def wrapped(request, userinfo):
      return userinfo

    request = mock.create_autospec(twisted.web.http.Request)
    request.getCookie.return_value = mock.sentinel
    self.assertEqual(wrapped(request), {'sub': 'user@example.com'})

  def test_match_required_injects(self):
    """Tests both that the token value is injected and that that value matches the given email."""
    @self.auth.match_required
    def wrapped(request, userinfo, email=None):
      return userinfo

    request = mock.create_autospec(twisted.web.http.Request)
    request.getCookie.return_value = mock.sentinel
    self.assertEqual(wrapped(request, email='user@example.com'), {'sub': 'user@example.com'})

  def test_match_required_raises(self):
    """Tests that an exception is raised if the token's value doesn't match the given email."""
    @self.auth.match_required
    def wrapped(request, userinfo, email=None):
      return userinfo

    request = mock.create_autospec(twisted.web.http.Request)
    request.getCookie.return_value = mock.sentinel
    with pytest.raises(werkzeug.exceptions.Forbidden):
      with mock.patch.object(self.auth, '_debug', False):  # ensure check actually happens
        wrapped(request, email='baduser@example.com')


class TokenHeadersTestCase(BaseAuthTestCase):
  """Tests for error conditions when decoding the value for the Authorization header."""

  def check_raises(self, header_value, exc_class):
    with pytest.raises(exc_class) as excinfo:
      self.auth.decode_header_value(header_value)
    logger.debug("exception: {!s}", excinfo.value)

  def test_raises_on_missing_headers(self):
    self.check_raises(None, werkzeug.exceptions.Unauthorized)

  def test_raises_on_bad_header(self):
    self.check_raises(b"foobar!", werkzeug.exceptions.BadRequest)

  def test_raises_on_bad_header_type(self):
    self.check_raises(b"Basic foobar!", werkzeug.exceptions.BadRequest)

  def test_raises_on_bad_token(self):
    self.check_raises(b"Bearer foobar!", werkzeug.exceptions.Unauthorized)


class TokenEncodeDecodeTestCase(BaseAuthTestCase):

  def test_encodes_valid_token(self):
    encoded = self.auth.create_token(sub='user@example.com')
    self.check_decoded(jwt.decode(encoded, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM))

  def test_decode_valid_token(self):
    encoded = self.auth.create_token(sub='user@example.com')
    self.check_decoded(self.auth.decode_token(encoded))

  def test_decode_raises_for_expired(self):
    now = datetime.datetime.utcnow() - datetime.timedelta(minutes=60)
    encoded = jwt.encode({'sub': 'user@example.com', 'iat': now, 'nbf': now, 'exp': now},
        JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    with pytest.raises(werkzeug.exceptions.Unauthorized):
      self.auth.decode_token(encoded)

  def test_decode_raises_for_invalid_token_error(self):
    with pytest.raises(werkzeug.exceptions.Unauthorized):
      with mock.patch('jwt.decode', side_effect=jwt.InvalidTokenError):
        self.auth.decode_token(None)


class HeaderDecodeTestCase(BaseAuthTestCase):

  def test_match_required_with_token_injects(self):
    """Tests both that the token value is injected and that that value matches the given email."""
    request = mock.create_autospec(twisted.web.http.Request)
    request.getCookie.return_value = None
    request.getHeader.return_value = b'Bearer ' + self.auth.create_token(sub='user@example.com')

    @self.auth.match_required
    def wrapped(request, userinfo, email):
      return userinfo

    self.check_decoded(wrapped(request, email='user@example.com'))

  def test_match_required_with_token_raises(self):
    """Tests that an exception is raised when the given email doesn't match the token's value."""
    request = mock.create_autospec(twisted.web.http.Request)
    request.getCookie.return_value = None
    request.getHeader.return_value = b'Bearer ' + self.auth.create_token(sub='user@example.com')

    @self.auth.match_required
    def wrapped(request, userinfo, email):
      return userinfo

    with pytest.raises(werkzeug.exceptions.Forbidden):
      with mock.patch.object(self.auth, '_debug', False):  # ensure check actually happens
        wrapped(request, email='baduser@example.com')


class AppTestCase(BaseAuthTestCase):

  def setUp(self):
    super(AppTestCase, self).setUp()
    self.auth.decode_header_value = mock.create_autospec(self.auth.decode_header_value)
    self.auth.decode_header_value.return_value = self.userinfo = {'sub': 'user@example.com'}

  def test_route_token_required(self):
    app = klein.Klein()

    @app.route("/")
    @self.auth.token_required
    def endpoint(request, userinfo):
      return userinfo

    mock_request = mock.create_autospec(twisted.web.http.Request)
    mock_request.getCookie.return_value = None
    returned = app.execute_endpoint("endpoint", mock_request)
    self.assertEqual(returned, self.userinfo)

  def test_route_match_required(self):
    app = klein.Klein()
    kr = KleinResource(app)

    @app.route("/api/<string:email>", endpoint="endpoint")
    @self.auth.match_required
    def endpoint(request, userinfo, email):
      logger.debug("in endpoint: request={!r}, userinfo={!r}, email={!r}", request, userinfo, email)
      return json.dumps(userinfo)

    request = requestMock(b"/api/user@example.com")

    deferred = _render(kr, request)

    self.assertEqual(self.successResultOf(deferred), None)
    self.assertEqual(request.getWrittenData(), json.dumps(self.userinfo).encode('ascii'))
