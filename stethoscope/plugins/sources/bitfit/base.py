# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import arrow
import logbook

import stethoscope.api.exceptions
import stethoscope.configurator
import stethoscope.plugins.sources.bitfit.utils
import stethoscope.utils
import stethoscope.validation


logger = logbook.Logger(__name__)


def _get_mac_addrs(values):
  mac_addresses = set()
  for value in values:
    try:
      addr = stethoscope.validation.canonicalize_macaddr(value)
    except (KeyError, TypeError, ValueError):
      pass
    else:
      mac_addresses.add(addr)
  return list(stethoscope.validation.filter_macaddrs(mac_addresses))


class BitfitDataSourceBase(stethoscope.configurator.Configurator):

  config_keys = (
      'BITFIT_API_TOKEN',
      'BITFIT_BASE_URL',
  )

  @staticmethod
  def _process_userinfo(userinfo_response, email):
    users = userinfo_response['items']
    for user in users:
      if user['email'] == email:
        return user
    raise stethoscope.api.exceptions.UserNotFoundException(email)

  def _process_fields(self, raw, data):
    fields = stethoscope.plugins.sources.bitfit.utils.parse_field_list(raw['item']['fields'])

    mac_addresses = _get_mac_addrs([fields['mac_address']['value'],
                                    fields['alt_mac_address']['value']])
    if len(mac_addresses) > 0:
      data['identifiers']['mac_addresses'] = mac_addresses

    if 'UDID' in fields:
      value = fields['UDID'].get('value')
      if value is not None:
        data['identifiers']['udid'] = value

    try:
      data['hw_release_date'] = arrow.get(fields['HW Release Date']['value'], 'M/D/YYYY')
    except (TypeError, KeyError):
      pass

    return data

  def _process_device(self, raw):
    # logger.debug("bitfit device:\n{:s}", pprint.pformat(raw))
    data = {'_raw': raw} if self._debug else {}
    data.update(stethoscope.utils.copy_partial_dict(raw['item'], {
      'model': 'model',
      'name': 'name',
    }))

    data['identifiers'] = {}
    serial = raw['item'].get('serial_number')
    if serial is not None:
      data['serial'] = serial
      data['identifiers']['serial'] = serial

    data['photo_url'] = stethoscope.plugins.sources.bitfit.utils.get_photo_url(raw)

    data['type'] = raw['item'].get('type', {}).get('label_single')
    if data['type'] is None:
      data['type'] = raw['item'].get('config', {}).get('type', {}).get('label_single')

    try:
      data['status'] = raw['item']['customerStatus']['label']
    except KeyError:
      pass

    self._process_fields(raw, data)

    data['source'] = 'bitfit'
    return data
