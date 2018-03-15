# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import functools
import re
import uuid

import logbook
import six
import six.moves
import validate_email

import stethoscope.exceptions


logger = logbook.Logger(__name__)

MACADDR_PATTERN = re.compile(r'^' + r'\:?'.join([r'([0-9A-F]{1,2})'] * 6) + r'$', re.IGNORECASE)


def _is_valid_macaddr(addr):
  """Check if `addr` is a valid MAC address.

  >>> _is_valid_macaddr('00:00:DE:CA:FB:AD')
  True
  >>> _is_valid_macaddr('0A08CCA544F1')
  True
  >>> _is_valid_macaddr('0000decafbad')
  True
  >>> _is_valid_macaddr('00:00')
  False
  >>> _is_valid_macaddr(u'00:00:DE:CA:FB:AD')
  True

  """
  return MACADDR_PATTERN.match(addr) is not None


def raise_for_invalid_macaddr(macaddr):
  """Raise `ValueError` for invalid MAC address input.

  >>> canonicalize_macaddr('00:00')
  ... # doctest: +IGNORE_EXCEPTION_DETAIL
  ... # above directive is a hack to support 2.X and 3.X at the same time
  Traceback (most recent call last):
    ...
  ValueError: invalid MAC address ('00:00')

  """
  if not _is_valid_macaddr(macaddr):
    raise ValueError("invalid MAC address ({!r})".format(macaddr))


def is_locally_administered_macaddr(macaddr):
  """Certain MAC addresses are "locally administered" rather than a universal identifier.

  A MAC address is "locally administered" if and only if the *second* least-significant bit of the
  first octet is ``1`` [wikipedia-local-mac]_.

  .. [wikipedia-local-mac] https://en.wikipedia.org/wiki/MAC_address#Universal_vs._local

  >>> is_locally_administered_macaddr('02:00:00:00:00:00')
  True
  >>> is_locally_administered_macaddr('00:00:DE:CA:FB:AD')
  False

  """
  return bool(int(canonicalize_macaddr(macaddr)[1], 16) & 0b10)


def is_group_macaddr(macaddr):
  """Certain MAC addresses are for addressing groups and are therefore *not* universal identifiers.

  A MAC address is a group address if and only if the least-significant bit of the first octet is
  ``1`` [wikipedia-group-mac]_. This includes the broadcast address (`FF:FF:FF:FF:FF:FF`), multicast
  addresses, and function addresses for token-ring networks.

  .. [wikipedia-group-mac] https://en.wikipedia.org/wiki/MAC_address#Unicast_vs._multicast

  >>> is_group_macaddr('01:00:00:00:00:00')
  True
  >>> is_group_macaddr('00:00:DE:CA:FB:AD')
  False

  """
  return bool(int(canonicalize_macaddr(macaddr)[1], 16) & 0b1)


def should_filter_macaddr(macaddr, filter_functions=None):
  """Determine if a MAC address can be used for device merging (i.e., is a unique identifier).

  For instance, group addresses and locally administered addresses are not intended to be unique to
  a particular piece of hardware and so can't be used as universal identifiers.

  >>> should_filter_macaddr('01:00:00:00:00:00')  # group address
  True
  >>> should_filter_macaddr('02:00:00:00:00:00')  # locally-administered address
  True
  >>> should_filter_macaddr('03:00:00:00:00:00')  # locally-administered group address
  True
  >>> should_filter_macaddr('00:DE:CA:FB:AD:00')  # neither group nor locally-administered
  False

  """
  if filter_functions is None:
    filter_functions = (is_locally_administered_macaddr, is_group_macaddr)
  return any(f(macaddr) for f in filter_functions)


def filter_macaddrs(macaddrs, filter_functions=None):
  """Filter out any MAC addresses that can't be used as universal identifiers.

  For instance, group addresses and locally administered addresses are not intended to be unique to
  a particular piece of hardware and so can't be used as universal identifiers.

  >>> list(filter_macaddrs(
  ...   ['02:00:00:00:00:00', '01:00:00:00:00:00', '03:00:00:00:00:00', '00:00:DE:CA:FB:AD']
  ... ))
  ['00:00:DE:CA:FB:AD']

  """
  filter_func = functools.partial(should_filter_macaddr, filter_functions=filter_functions)
  return six.moves.filterfalse(filter_func, macaddrs)


def canonicalize_macaddr(addr):
  """Convert a MAC address into canonical format (uppercase with colon separators).

  >>> canonicalize_macaddr('0A08CCA544F1')
  '0A:08:CC:A5:44:F1'
  >>> canonicalize_macaddr('0000decafbad')
  '00:00:DE:CA:FB:AD'
  >>> canonicalize_macaddr('00:00:DE:CA:FB:AD')
  '00:00:DE:CA:FB:AD'
  >>> canonicalize_macaddr('00:00')
  ... # doctest: +IGNORE_EXCEPTION_DETAIL
  ... # above directive is a hack to support 2.X and 3.X at the same time
  Traceback (most recent call last):
    ...
  ValueError: invalid MAC address ('00:00')
  >>> canonicalize_macaddr(u'00:00:DE:CA:FB:AD')
  '00:00:DE:CA:FB:AD'

  """
  raise_for_invalid_macaddr(addr)
  addr = addr.replace(':', '').upper()
  return ':'.join(addr[idx:idx + 2] for idx in range(0, len(addr), 2))


def validate_uuid(uuid_str):
  try:
    uuid.UUID(uuid_str)
  except ValueError:
    raise stethoscope.exceptions.ValidationError("UUID", uuid_str)


def validate_murmurhash(string):
  """
  >>> validate_murmurhash('foobar!')
  ... # doctest: +IGNORE_EXCEPTION_DETAIL
  ... # above directive is a hack to support 2.X and 3.X at the same time
  Traceback (most recent call last):
    ...
  ValidationError: ...

  >>> validate_murmurhash('bc205b0679274b29ec8257ca14b0a6b8')

  """
  if not re.match(r"""^[0-9A-Fa-f]{32}$""", string):
    raise stethoscope.exceptions.ValidationError("ID", string)


def check_valid_email(func):
  @six.wraps(func)
  def decorator(request, email, *args, **kwargs):
    if not validate_email.validate_email(email):
      raise stethoscope.exceptions.ValidationError("email address", email)
    return func(request, email, *args, **kwargs)
  return decorator


def check_valid_serial(func):
  @six.wraps(func)
  def decorator(request, serial, *args, **kwargs):
    if not re.match(r"""[\w-]+$""", serial):
      raise stethoscope.exceptions.ValidationError("serial number", serial)
    return func(request, serial, *args, **kwargs)
  return decorator


def check_valid_macaddr(func):
  @six.wraps(func)
  def decorator(request, macaddr, *args, **kwargs):
    if not _is_valid_macaddr(macaddr):
      raise stethoscope.exceptions.ValidationError("MAC address", macaddr)
    return func(request, macaddr, *args, **kwargs)
  return decorator
