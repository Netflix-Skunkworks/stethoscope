# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import copy
import json
import sys

import logbook
import treq
from twisted.internet import defer
import txwebretry

import stethoscope.api.exceptions
import stethoscope.api.utils
import stethoscope.plugins.sources.jamf.base
import stethoscope.utils


logger = logbook.Logger(__name__)


def check_response(response, resource=None):
  return stethoscope.api.utils.check_response(response, service='jamf', resource=resource)


def check_device_response(response, identifier):
  if response.code == 404:
    raise stethoscope.api.exceptions.DeviceNotFoundException(identifier, service='jamf')
  return check_response(response, resource='device')


def check_userinfo_response(response, email):
  if response.code == 404:
    raise stethoscope.api.exceptions.UserNotFoundException(email, service='jamf')
  return check_response(response, resource='userinfo')


def _check_connectivity_response(response):
  logger.debug("connectivity response code: {:d}", response.code)
  if response.code == 401:
    raise Exception("JAMF authentication failure; check credentials.")
  if response.code != 200:
    raise Exception("JAMF connection failure; response code: {:d}.".format(response.code))
  return response


def _log_server_information(data):
  logger.debug("connectivity response data:\n{!s}", stethoscope.utils.json_pp(data))
  return data


class DeferredJAMFDataSource(stethoscope.plugins.sources.jamf.base.JAMFDataSourceBase):

  def __init__(self, *args, **kwargs):
    super(DeferredJAMFDataSource, self).__init__(*args, **kwargs)

    self.kwargs = {
      'timeout': self.config.get('JAMF_TIMEOUT', self.config.get('DEFAULT_TIMEOUT', 2)),
      'auth': (self.config['JAMF_API_USERNAME'], self.config['JAMF_API_PASSWORD']),
      'headers': {'Accept': 'application/json'},
    }

  def get(self, path, **_kwargs):
    url = self.config['JAMF_API_HOSTADDR'] + path

    kwargs = copy.deepcopy(self.kwargs)
    kwargs.update(_kwargs)

    logger.debug("GET '{:s}'", url)
    return txwebretry.ExponentialBackoffRetry(3)(treq.get, url, **kwargs)

  def get_userinfo_by_email(self, email):
    deferred = self.get('/users/name/{:s}'.format(email.split('@')[0]))
    deferred.addCallback(check_userinfo_response, email)
    deferred.addCallback(treq.content)
    deferred.addCallback(json.loads)
    return deferred

  def _process_device_response(self, deferred):
    deferred.addCallback(check_response, resource='device')
    deferred.addCallback(treq.content)
    # deferred.addCallback(stethoscope.api.utils.write_to_file, filename="device.json")
    deferred.addCallback(json.loads)
    deferred.addCallback(self._process_device)
    return deferred

  def _get_device_by_id(self, device_id):
    deferred = self.get('/computers/id/{:d}'.format(device_id))
    deferred = self._process_device_response(deferred)
    return deferred

  def _get_devices_by_id(self, device_ids):
    deferred_list = defer.DeferredList([self._get_device_by_id(device_id) for device_id in
      device_ids], consumeErrors=True)

    # working off JAMF's own data, so shouldn't fail
    deferred_list.addCallback(stethoscope.api.utils.filter_by_status,
        context=sys._getframe().f_code.co_name, level=logbook.ERROR)
    return deferred_list

  def get_devices_by_serial(self, serial):
    deferred = self.get('/computers/serialnumber/{!s}'.format(serial))
    deferred.addCallback(check_device_response, "serial: '{!s}'".format(serial))
    deferred = self._process_device_response(deferred)
    deferred.addCallback(lambda x: [x])
    return deferred

  def get_devices_by_macaddr(self, addr):
    deferred = self.get('/computers/macaddress/{!s}'.format(addr))
    deferred.addCallback(check_device_response, "macaddr: '{!s}'".format(addr))
    deferred = self._process_device_response(deferred)
    deferred.addCallback(lambda x: [x])
    return deferred

  def get_devices_by_email(self, email):
    deferred = self.get_userinfo_by_email(email)
    deferred.addCallback(self._extract_device_ids_from_userinfo)
    deferred.addCallback(self._get_devices_by_id)
    return deferred

  def test_connectivity(self):
    deferred = self.get('/jssuser')
    deferred.addCallback(_check_connectivity_response)
    deferred.addCallback(treq.content)
    deferred.addCallback(json.loads)
    deferred.addCallback(_log_server_information)
    return deferred
