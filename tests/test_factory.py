# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import json

import klein
import klein.test.test_resource
import mock
import six
import stevedore
import twisted.internet.defer
import twisted.trial
from klein.resource import KleinResource

import stethoscope.api.endpoints.events
import stethoscope.api.endpoints.utils
import stethoscope.api.factory
import stethoscope.auth
import stethoscope.api.endpoints.accounts


config = {
  'DEBUG': True,
  'TESTING': True,
}


class DummyAuthProvider(object):

  def match_required(self, func):
    @six.wraps(func)
    def decorator(request, *args, **kwargs):
      kwargs['userinfo'] = {'sub': 'test'}
      args = (request, ) + args
      return func(*args, **kwargs)
    return decorator

  token_required = match_required


def get_mock_ext(result, name='foo'):
  ext = mock.MagicMock()
  ext.name = name

  resource_methods = [
      'get_resource_by_email',
      'get_account_by_email',
      'get_devices_by_email',
      'get_devices_by_serial',
      'get_userinfo_by_email',
      'get_events_by_email',
      'get_notifications_by_email',
  ]
  for method in resource_methods:
    setattr(ext.obj, method, lambda _: twisted.internet.defer.succeed(result))

  return ext


class RoutingTestCase(twisted.trial.unittest.TestCase):
  """Tests that routes are set up properly."""

  def check_result(self, app, path, expected, callback=None):
    # see klein's test_resource.py
    request = klein.test.test_resource.requestMock(path)
    deferred = klein.test.test_resource._render(KleinResource(app), request)
    self.assertEqual(self.successResultOf(deferred), None)
    self.assertEqual(request.getWrittenData(), six.b(json.dumps(expected)))

    if callback is not None:
      callback.assert_called_once_with(expected)

  def test_add_route(self):
    app = klein.Klein()
    auth = DummyAuthProvider()

    result = ['foobar']
    ext = get_mock_ext(result)

    callback = mock.Mock(side_effect=lambda x: x)

    stethoscope.api.endpoints.utils.add_get_route(ext, app, auth, 'resource', 'email',
                                                  callbacks=[callback])

    # see klein's test_app.py
    self.assertEqual(
        app.url_map.bind('resource-foo-email').match("/resource/foo/email/user@example.com"),
        ('resource-foo-email', {'email': "user@example.com"}))
    self.assertEqual(len(app.endpoints), 1)

    self.check_result(app, b'/resource/foo/email/user@example.com', result, callback)

  def test_register_userinfo_api_endpoints(self):
    app = klein.Klein()
    auth = DummyAuthProvider()
    result = ['foobar']

    with mock.patch('stethoscope.plugins.utils.instantiate_plugins') as \
        mock_instantiate_plugins:
      mock_instantiate_plugins.return_value = stevedore.ExtensionManager.make_test_instance(
          [get_mock_ext(result)])
      stethoscope.api.factory.register_userinfo_api_endpoints(app, config, auth)

    # see klein's test_app.py
    self.assertEqual(
        app.url_map.bind('userinfo-foo-email').match("/userinfo/foo/email/user@example.com"),
        ('userinfo-foo-email', {'email': "user@example.com"})
    )
    self.assertEqual(len(app.endpoints), 1)

    self.check_result(app, b'/userinfo/foo/email/user@example.com', result)

  def test_register_notification_api_endpoints(self):
    app = klein.Klein()
    auth = DummyAuthProvider()
    result_foo = [{'_source': {'event_timestamp': 0}}]
    result_bar = [{'_source': {'event_timestamp': 1}}]

    mock_hook = mock.Mock()
    mock_hook.obj.transform.side_effect = lambda x: x
    mock_hook_manager = stevedore.ExtensionManager.make_test_instance([mock_hook])
    mock_extension_manager = stevedore.ExtensionManager.make_test_instance(
        [get_mock_ext(result_foo, 'foo'), get_mock_ext(result_bar, 'bar')])

    with mock.patch('stethoscope.plugins.utils.instantiate_plugins') as \
        mock_instantiate_plugins:
      mock_instantiate_plugins.side_effect = [mock_extension_manager, mock_hook_manager]
      stethoscope.api.factory.register_notification_api_endpoints(app, config, auth)

    # see klein's test_app.py
    adapter_foo = app.url_map.bind('notifications-foo-email')
    self.assertEqual(
        adapter_foo.match("/notifications/foo/email/user@example.com"),
        ('notifications-foo-email', {'email': "user@example.com"})
    )

    adapter_bar = app.url_map.bind('notifications-bar-email')
    self.assertEqual(
        adapter_bar.match("/notifications/bar/email/user@example.com"),
        ('notifications-bar-email', {'email': "user@example.com"})
    )

    self.assertEqual(
        app.url_map.bind('notifications-merged').match("/notifications/merged/user@example.com"),
        ('notifications-merged', {'email': "user@example.com"})
    )

    self.assertEqual(len(app.endpoints), 3)

    self.check_result(app, b'/notifications/foo/email/user@example.com', result_foo)
    self.check_result(app, b'/notifications/bar/email/user@example.com', result_bar)

    self.check_result(app, b'/notifications/merged/user@example.com', result_bar + result_foo)

  def test_register_account_api_endpoints(self):
    app = klein.Klein()
    auth = DummyAuthProvider()
    result = ['foobar']

    with mock.patch('stethoscope.plugins.utils.instantiate_plugins') as \
        mock_instantiate_plugins:
      mock_instantiate_plugins.return_value = stevedore.ExtensionManager.make_test_instance(
          [get_mock_ext(result)])
      stethoscope.api.endpoints.accounts.register_account_api_endpoints(app, config, auth)

    # see klein's test_app.py
    self.assertEqual(
        app.url_map.bind('account-foo-email').match("/account/foo/email/user@example.com"),
        ('account-foo-email', {'email': "user@example.com"})
    )
    self.assertEqual(
        app.url_map.bind('accounts-merged').match("/accounts/merged/user@example.com"),
        ('accounts-merged', {'email': "user@example.com"})
    )
    self.assertEqual(len(app.endpoints), 2)

    self.check_result(app, b'/account/foo/email/user@example.com', result)
    self.check_result(app, b'/accounts/merged/user@example.com', [result])

  def test_register_event_api_endpoints(self):
    app = klein.Klein()
    auth = DummyAuthProvider()
    result_foo = [{'timestamp': 0}]
    result_bar = [{'timestamp': 1}]

    mock_hook = mock.Mock()
    mock_hook.obj.transform.side_effect = lambda x: x
    mock_hook_manager = stevedore.ExtensionManager.make_test_instance([mock_hook])
    mock_extension_manager = stevedore.ExtensionManager.make_test_instance(
        [get_mock_ext(result_foo, 'foo'), get_mock_ext(result_bar, 'bar')])

    with mock.patch('stethoscope.plugins.utils.instantiate_plugins') as \
        mock_instantiate_plugins:
      mock_instantiate_plugins.side_effect = [mock_extension_manager, mock_hook_manager]
      stethoscope.api.endpoints.events.register_event_api_endpoints(app, config, auth)

    # see klein's test_app.py
    self.assertEqual(
        app.url_map.bind('events-foo-email').match("/events/foo/email/user@example.com"),
        ('events-foo-email', {'email': "user@example.com"})
    )
    self.assertEqual(
        app.url_map.bind('events-bar-email').match("/events/bar/email/user@example.com"),
        ('events-bar-email', {'email': "user@example.com"})
    )

    self.assertEqual(app.url_map.bind('events-merged').match("/events/merged/user@example.com"),
        ('events-merged', {'email': "user@example.com"}))

    self.assertEqual(len(app.endpoints), 3)

    self.check_result(app, b'/events/foo/email/user@example.com', result_foo)
    self.check_result(app, b'/events/bar/email/user@example.com', result_bar)

    self.check_result(app, b'/events/merged/user@example.com', result_bar + result_foo)

  def test_register_device_api_endpoints(self):
    app = klein.Klein()
    auth = DummyAuthProvider()
    result = ['foobar']

    with mock.patch('stethoscope.plugins.utils.instantiate_plugins') as \
        mock_instantiate_plugins:
      mock_instantiate_plugins.return_value = stevedore.ExtensionManager.make_test_instance(
          [get_mock_ext(result)])
      stethoscope.api.factory.register_device_api_endpoints(app, config, auth)

    # see klein's test_app.py
    self.assertEqual(
        app.url_map.bind('devices-foo-email').match("/devices/foo/email/user@example.com"),
        ('devices-foo-email', {'email': "user@example.com"})
    )
    self.assertEqual(
        app.url_map.bind('devices-foo-macaddr').match("/devices/foo/macaddr/de:ca:fb:ad:00:00"),
        ('devices-foo-macaddr', {'macaddr': "de:ca:fb:ad:00:00"}))
    self.assertEqual(app.url_map.bind('devices-foo-serial').match("/devices/foo/serial/0xDEADBEEF"),
        ('devices-foo-serial', {'serial': "0xDEADBEEF"}))

    self.assertEqual(app.url_map.bind('devices-email').match("/devices/email/user@example.com"),
        ('devices-email', {'email': "user@example.com"}))
    self.assertEqual(app.url_map.bind('devices-serial').match("/devices/serial/0xDECAFBAD"),
        ('devices-serial', {'serial': "0xDECAFBAD"}))
    self.assertEqual(app.url_map.bind('devices-macaddr').match(
        "/devices/macaddr/DE:CA:FB:AD:00:00"),
        ('devices-macaddr', {'macaddr': "DE:CA:FB:AD:00:00"}))
    self.assertEqual(app.url_map.bind('devices-staged').match("/devices/staged/user@example.com"),
        ('devices-staged', {'email': "user@example.com"}))
    self.assertEqual(app.url_map.bind('devices-merged').match("/devices/merged/user@example.com"),
        ('devices-merged', {'email': "user@example.com"}))
    self.assertEqual(len(app.endpoints), 8)

    self.check_result(app, b'/devices/foo/email/user@example.com', result)

    # noop = mock.Mock(side_effect=lambda x: x)
    # with mock.patch('stethoscope.api.devices.merge_devices', noop):
    #   self.check_result(app, b'/devices/email/user@example.com', [result])
    #   self.check_result(app, b'/devices/serial/0xDECAFBAD', [result])
    #   self.check_result(app, b'/devices/staged/user@example.com', [result, result])
    #   self.check_result(app, b'/devices/merged/user@example.com', [result, result])
