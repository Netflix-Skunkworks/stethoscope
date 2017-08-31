# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import mock
import treq
from twisted.internet.defer import succeed
from twisted.trial import unittest

import stethoscope.api.exceptions
import stethoscope.api.utils
import stethoscope.plugins.sources.jamf.deferred


class DeferredJAMFTestCase(unittest.TestCase):

  def setUp(self):
    self.datasource = stethoscope.plugins.sources.jamf.deferred.DeferredJAMFDataSource({
      'JAMF_API_USERNAME': '',
      'JAMF_API_PASSWORD': '',
      'JAMF_API_HOSTADDR': '',
    })

    self.treq = mock.patch('stethoscope.plugins.sources.jamf.deferred.treq', wraps=treq).start()
    self.addCleanup(mock.patch.stopall)

  def set_response(self, body=None, code=200):
    response = mock.Mock()
    response.code = code

    if body is not None:
      self.treq.content.return_value = succeed(body)

    self.treq.get.return_value = succeed(response)
    return response

  def test_userinfo_notfound(self):
    self.set_response(code=404)
    deferred = self.datasource.get_userinfo_by_email('user@example.com')
    return self.failUnlessFailure(deferred, stethoscope.api.exceptions.UserNotFoundException)

  def test_userinfo_remoteerror(self):
    self.set_response(code=500)
    deferred = self.datasource.get_userinfo_by_email('user@example.com')
    return self.failUnlessFailure(deferred, stethoscope.api.exceptions.InvalidResponseException)

  def test_device_notfound(self):
    self.set_response(code=404)
    deferred = self.datasource._get_device_by_id(0)
    return self.failUnlessFailure(deferred, stethoscope.api.exceptions.InvalidResponseException)

  def test_device_remoteerror(self):
    self.set_response(code=500)
    deferred = self.datasource._get_device_by_id(0)
    return self.failUnlessFailure(deferred, stethoscope.api.exceptions.InvalidResponseException)

  def test_devices_userinfo_notfound(self):
    self.set_response(code=404)
    deferred = self.datasource.get_devices_by_email('user@example.com')
    return self.failUnlessFailure(deferred, stethoscope.api.exceptions.UserNotFoundException)

  def test_devices_userinfo_remoteerror(self):
    self.set_response(code=500)
    deferred = self.datasource.get_devices_by_email('user@example.com')
    return self.failUnlessFailure(deferred, stethoscope.api.exceptions.InvalidResponseException)
