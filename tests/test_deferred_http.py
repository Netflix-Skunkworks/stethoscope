# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import mock

import stethoscope.plugins.mixins.deferred_http
import stethoscope.utils


class HTTPMixinStub(stethoscope.plugins.mixins.deferred_http.DeferredHTTPMixin):
  pass


def test_post():
  mock_url = mock.Mock('url')
  instance = HTTPMixinStub({'URL': mock_url})

  mock_serialized_payload = mock.Mock(name='serialized_payload')
  with mock.patch('json.dumps', return_value=mock_serialized_payload) as mock_json_dumps:
    with mock.patch.object(instance, '_post') as mock_post:
      mock_payload = mock.Mock(name='payload')
      instance.post(mock_payload)
      mock_json_dumps.assert_called_with(mock_payload,
          default=stethoscope.utils.json_serialize_datetime)

  expected_kwargs = {
    'headers': {
        'Content-Type': 'application/json',
        'User-Agent': 'Stethoscope',
    },
    'timeout': None,
  }

  mock_post.assert_called_once_with(mock_url, mock_serialized_payload, **expected_kwargs)
