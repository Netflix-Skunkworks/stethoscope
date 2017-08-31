# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import json

import klein
import mock
import pytest
import six
import twisted.trial
import twisted.web
from klein.test.test_resource import requestMock

import stethoscope.csrf


class CSRFTestCase(twisted.trial.unittest.TestCase):

  def setUp(self):
    self.csrf = stethoscope.csrf.CSRFProtection({})
    self.app = klein.Klein()

    @self.app.route("/")
    @self.csrf.csrf_protect
    def endpoint(request):
      return mock.sentinel.DEFAULT

  def get_mock_request(self, body={}):
    return requestMock(b"/", method=b"POST", isSecure=True, body=six.b(json.dumps(body)))


class RefererCheckTestCase(CSRFTestCase):

  def test_missing_referer(self):
    with pytest.raises(stethoscope.csrf.CSRFError) as exc:
      self.app.execute_endpoint("endpoint", self.get_mock_request())
    assert exc.value.description == stethoscope.csrf.MSG_MISSING_REFERER

  def test_malformed_referer(self):
    mock_request = self.get_mock_request()
    mock_request.requestHeaders.addRawHeader(b"Referer", b"junk")
    with pytest.raises(stethoscope.csrf.CSRFError) as exc:
      self.app.execute_endpoint("endpoint", mock_request)
    assert exc.value.description == stethoscope.csrf.MSG_MALFORMED_REFERER

  def test_insecure_referer(self):
    mock_request = self.get_mock_request()
    mock_request.requestHeaders.addRawHeader(b"Referer", b"http://www.example.com/bar")
    with pytest.raises(stethoscope.csrf.CSRFError) as exc:
      self.app.execute_endpoint("endpoint", mock_request)
    assert exc.value.description == stethoscope.csrf.MSG_INSECURE_REFERER

  def test_bad_referer(self):
    mock_request = self.get_mock_request()
    mock_request.requestHeaders.addRawHeader(b"Referer", b"https://www.example.com/bar")
    with pytest.raises(stethoscope.csrf.CSRFError) as exc:
      self.app.execute_endpoint("endpoint", mock_request)
    assert exc.value.description.startswith("Bad referer")

  def test_good_referer_x_forwarded_host(self):
    mock_request = self.get_mock_request()
    mock_request.requestHeaders.addRawHeader(b"X-Forwarded-Host", b"https://www.example.com")
    mock_request.requestHeaders.addRawHeader(b"Referer", b"https://www.example.com/bar")
    self.csrf._check_referer(mock_request)

  def test_good_referer_http_host(self):
    mock_request = self.get_mock_request()
    mock_request.requestHeaders.addRawHeader(b"Host", b"https://www.example.com")
    mock_request.requestHeaders.addRawHeader(b"Referer", b"https://www.example.com/bar")
    self.csrf._check_referer(mock_request)


class TokenCheckTestCase(CSRFTestCase):

  def test_missing_token(self):
    mock_request = self.get_mock_request()
    mock_request.args = {}
    with pytest.raises(stethoscope.csrf.CSRFError) as exc:
      self.csrf._check_token(mock_request)
    assert exc.value.description == stethoscope.csrf.MSG_MISSING_TOKEN

  def test_post_with_missing_cookie(self):
    mock_request = self.get_mock_request({'_csrf_token': ['token']})
    with pytest.raises(stethoscope.csrf.CSRFError) as exc:
      self.csrf._check_token(mock_request)
    assert exc.value.description == stethoscope.csrf.MSG_MISSING_COOKIE

  def test_header_with_missing_cookie(self):
    mock_request = self.get_mock_request()
    mock_request.requestHeaders.addRawHeader(b'X-CSRF-Token', b'token')
    with pytest.raises(stethoscope.csrf.CSRFError) as exc:
      self.csrf._check_token(mock_request)
    assert exc.value.description == stethoscope.csrf.MSG_MISSING_COOKIE

  def test_header_bad_token(self):
    mock_request = self.get_mock_request()
    mock_request.requestHeaders.addRawHeader(b'X-CSRF-Token', b'wrong')
    mock_request.received_cookies = {'_csrf_token': b'token'}
    with pytest.raises(stethoscope.csrf.CSRFError) as exc:
      self.csrf._check_token(mock_request)
    assert exc.value.description == stethoscope.csrf.MSG_BAD_TOKEN

  def test_header_good_token(self):
    mock_request = self.get_mock_request()
    mock_request.requestHeaders.addRawHeader(b'X-CSRF-Token', b'token')
    mock_request.received_cookies = {'_csrf_token': b'token'}
    self.csrf._check_token(mock_request)
