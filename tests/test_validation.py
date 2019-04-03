# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import json

import klein
import logbook
import six
from klein.resource import KleinResource
from klein.test.test_resource import _render, requestMock
from twisted.trial import unittest

import stethoscope.api.factory
import stethoscope.validation


logger = logbook.Logger(__name__)


class DummyAuthProvider(object):

  def check_token(self, request):
    return {'sub': 'test'}

  def match_required(self, func):
    @six.wraps(func)
    def decorator(request, *args, **kwargs):
      kwargs['userinfo'] = self.check_token(request)
      args = (request, ) + args
      return func(*args, **kwargs)
    return decorator

  token_required = match_required


class HTMLEscapeMixin(object):

  def test_html_escape(self):
    request = requestMock(b"/api/not-a-valid-<anything>")
    deferred = _render(KleinResource(self.app), request)

    self.assertEqual(self.successResultOf(deferred), None)
    self.assertEqual(request.code, 400)
    self.assertTrue(b"'not-a-valid-&lt;anything&gt;'" in request.getWrittenData())


class ValidationBase(unittest.TestCase):

  def setUp(self):
    self.app = app = klein.Klein()
    self.auth = auth = DummyAuthProvider()
    self.config = config = {
      'DEBUG': True,
      'TESTING': True,
    }

    stethoscope.api.factory.register_error_handlers(app, config, auth)


class ValidateMACTestCase(HTMLEscapeMixin, ValidationBase):

  def setUp(self):
    super(ValidateMACTestCase, self).setUp()

    @self.app.route("/api/<string:macaddr>", endpoint="endpoint")
    @stethoscope.validation.check_valid_macaddr
    def endpoint(request, macaddr):
      return json.dumps(macaddr)

  def test_invalid_macaddr(self):
    request = requestMock(b"/api/not-a-valid-mac")
    deferred = _render(KleinResource(self.app), request)

    self.assertEqual(self.successResultOf(deferred), None)
    self.assertEqual(request.code, 400)
    self.assertTrue(b"Invalid MAC address: 'not-a-valid-mac'." in request.getWrittenData())

  def test_valid_macaddr(self):
    request = requestMock(b"/api/00:00:DE:CA:FB:AD")
    deferred = _render(KleinResource(self.app), request)

    self.assertEqual(self.successResultOf(deferred), None)
    self.assertEqual(request.code, 200)
    self.assertEqual(request.getWrittenData(), six.b(json.dumps("00:00:DE:CA:FB:AD")))

  def test_valid_long_macaddr(self):
    request = requestMock(b"/api/00:00:DE:CA:FB:AD:AB:CD")
    deferred = _render(KleinResource(self.app), request)

    self.assertEqual(self.successResultOf(deferred), None)
    self.assertEqual(request.code, 200)
    self.assertEqual(request.getWrittenData(), six.b(json.dumps("00:00:DE:CA:FB:AD:AB:CD")))

class ValidateEmailTestCase(HTMLEscapeMixin, ValidationBase):

  def setUp(self):
    super(ValidateEmailTestCase, self).setUp()

    @self.app.route("/api/<string:email>", endpoint="endpoint")
    @stethoscope.validation.check_valid_email
    def endpoint(request, email):
      return json.dumps(email)

  def test_invalid_email(self):
    request = requestMock(b"/api/not-a-valid-email")
    deferred = _render(KleinResource(self.app), request)

    self.assertEqual(self.successResultOf(deferred), None)
    self.assertEqual(request.code, 400)
    self.assertTrue(b"Invalid email address: 'not-a-valid-email'." in request.getWrittenData())

  def test_valid_email(self):
    request = requestMock(b"/api/user@example.com")
    deferred = _render(KleinResource(self.app), request)

    self.assertEqual(self.successResultOf(deferred), None)
    self.assertEqual(request.code, 200)
    self.assertEqual(request.getWrittenData(), six.b(json.dumps("user@example.com")))


class ValidateSerialTestCase(HTMLEscapeMixin, ValidationBase):

  def setUp(self):
    super(ValidateSerialTestCase, self).setUp()

    @self.app.route("/api/<string:serial>", endpoint="endpoint")
    @stethoscope.validation.check_valid_serial
    def endpoint(request, serial):
      return json.dumps(serial)

  def test_invalid_serial(self):
    request = requestMock(b"/api/not a valid serial")
    deferred = _render(KleinResource(self.app), request)

    self.assertEqual(self.successResultOf(deferred), None)
    self.assertEqual(request.code, 400)
    self.assertTrue(b"Invalid serial number: 'not a valid serial'." in request.getWrittenData())

  def test_valid_serial(self):
    request = requestMock(b"/api/0xDECAFBAD")
    deferred = _render(KleinResource(self.app), request)

    self.assertEqual(self.successResultOf(deferred), None)
    self.assertEqual(request.code, 200)
    self.assertEqual(request.getWrittenData(), six.b(json.dumps("0xDECAFBAD")))
