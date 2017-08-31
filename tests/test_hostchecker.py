# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import pytest
import werkzeug.exceptions
from klein.test.test_resource import requestMock

import stethoscope.hostchecker


@pytest.fixture(scope='module')
def config():
  return {
    'USE_X_FORWARDED_HOST': True,
  }


@pytest.fixture(scope='function')
def hostchecker(config):
  return stethoscope.hostchecker.HostChecker(config)


def test_get_host_default_http_port(hostchecker):
  request = requestMock(b"/foo", host=b'example.com', port=80)
  request.requestHeaders.removeHeader(b'host')  # force hostchecker to use transport attributes
  assert hostchecker.get_host(request) == 'example.com'


def test_get_host_default_https_port(hostchecker):
  request = requestMock(b"/foo", host=b'example.com', port=443, isSecure=True)
  request.requestHeaders.removeHeader(b'host')  # force hostchecker to use transport attributes
  assert hostchecker.get_host(request) == 'example.com'


def test_get_host_nonstandard_http_port(hostchecker):
  request = requestMock(b"/foo", host=b'example.com', port=8080)
  request.requestHeaders.removeHeader(b'host')  # force hostchecker to use transport attributes
  assert hostchecker.get_host(request) == 'example.com:8080'


def test_get_host_nonstandard_https_port(hostchecker):
  request = requestMock(b"/foo", host=b'example.com', port=8443, isSecure=True)
  request.requestHeaders.removeHeader(b'host')  # force hostchecker to use transport attributes
  assert hostchecker.get_host(request) == 'example.com:8443'


def test_get_host_nonstandard_https_port_ignoring_forwarded():
  hostchecker_ = hostchecker({'USE_X_FORWARDED_HOST': False})
  request = requestMock(b"/foo", host=b'example.com', port=8443, isSecure=True,
      headers={'X-Forwarded-Host': ['example.net']})
  request.requestHeaders.removeHeader(b'host')  # force hostchecker to use transport attributes
  assert hostchecker_.get_host(request) == 'example.com:8443'


def test_get_host_header(hostchecker):
  # klein's requestMock calls Twisted's Request.setHost, which sets the Host header as well as the
  # transport, so we need to override the header value after initialization for this test to work
  request = requestMock(b"/foo")
  request.requestHeaders.setRawHeaders('Host', ['example.com'])
  assert hostchecker.get_host(request) == 'example.com'


def test_get_host_forwarded(hostchecker):
  request = requestMock(b"/foo", headers={'X-Forwarded-Host': ['example.com']})
  assert hostchecker.get_host(request) == 'example.com'


def test_get_host_forwarded_multiple(hostchecker):
  request = requestMock(b"/foo", headers={'X-Forwarded-Host': ['example.net, example.com']})
  assert hostchecker.get_host(request) == 'example.net'


def test_get_host_trusted():
  hostchecker_ = hostchecker({'TRUSTED_HOSTS': ['example.com']})
  request = requestMock(b"/foo", host=b'example.com', port=80)
  assert hostchecker_.get_host(request) == 'example.com'


def test_get_host_untrusted():
  hostchecker_ = hostchecker({'TRUSTED_HOSTS': ['example.net']})
  request = requestMock(b"/foo", host=b'example.com', port=80)
  with pytest.raises(werkzeug.exceptions.SecurityError):
    hostchecker_.get_host(request)
