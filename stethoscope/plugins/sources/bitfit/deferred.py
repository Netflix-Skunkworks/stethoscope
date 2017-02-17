# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import sys
import json
import operator

import logbook
import treq
from twisted.internet import defer
import txwebretry

import stethoscope.plugins.sources.bitfit.base
import stethoscope.api.utils


logger = logbook.Logger(__name__)


def check_response(response, resource=None):
  return stethoscope.api.utils.check_response(response, service='bitfit', resource=resource)


class DeferredBitfitDataSource(stethoscope.plugins.sources.bitfit.base.BitfitDataSourceBase):

  def get(self, path, **_params):
    url = self.config['BITFIT_BASE_URL'] + path

    kwargs = {'timeout': self.config.get('BITFIT_TIMEOUT', self.config.get('DEFAULT_TIMEOUT', 2))}
    kwargs.setdefault('headers', {'Accept': 'application/json'})
    kwargs.setdefault('params', {'api_token': self.config['BITFIT_API_TOKEN']})
    kwargs['params'].update(_params)

    return txwebretry.ExponentialBackoffRetry(3)(treq.get, url, **kwargs)

  def get_userinfo_by_email(self, email):
    deferred = self.get('users', search=email)
    deferred.addCallback(check_response, resource='userinfo')
    deferred.addCallback(treq.content)
    deferred.addCallback(json.loads)
    deferred.addCallback(self._process_userinfo, email)
    return deferred

  def _get_device_by_id(self, device_id):
    deferred = self.get('/'.join(['assets', str(device_id)]))
    deferred.addCallback(check_response, resource='device')
    deferred.addCallback(treq.content)
    # deferred.addCallback(stethoscope.api.utils.write_to_file,
    #   filename="tmp/asset_response_{:d}.json".format(device_id))
    deferred.addCallback(json.loads)
    deferred.addCallback(self._process_device)
    return deferred

  def _get_device_details(self, devices_response):
    # logger.debug("bitfit devices:\n{!s}", json.dumps(devices_response, indent=2))
    deferreds = [self._get_device_by_id(device['id'])
        for device in devices_response.get('items', [])]
    deferred_list = defer.DeferredList(deferreds, consumeErrors=True)

    # shouldn't fail since we're working off bitfit's own data for the inputs
    deferred_list.addCallback(stethoscope.api.utils.filter_by_status,
        context=sys._getframe().f_code.co_name, level=logbook.ERROR)
    return deferred_list

  def _get_devices_by_userid(self, userid):
    deferred = self.get('/'.join(['users', str(userid), 'assets']))
    deferred.addCallback(check_response, resource='user assets')
    deferred.addCallback(treq.content)
    # deferred.addCallback(stethoscope.api.utils.write_to_file,
    #   filename="tmp/devices_response.json")
    deferred.addCallback(json.loads)
    deferred.addCallback(self._get_device_details)
    return deferred

  def get_devices_by_email(self, email):
    deferred = self.get_userinfo_by_email(email)
    deferred.addCallback(operator.itemgetter('id'))
    deferred.addCallback(self._get_devices_by_userid)
    return deferred
