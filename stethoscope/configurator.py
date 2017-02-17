# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import abc

import logbook
import six


logger = logbook.Logger(__name__)


def check_config_values(keys, config):
  """Raise an exception if all keys in `keys` are not represented in `config`.

  >>> check_config_values(['foo', 'bar'], {'foo': 'value'})
  Traceback (most recent call last):
    ...
  KeyError: "Missing configuration value(s): ['bar']"

  >>> check_config_values(['foo'], {'foo': 'value'})


  """
  missing = list()
  for key in keys:
    try:
      config[key]
    except KeyError:
      missing.append(key)
      logger.critical("'{:s}' missing from configuration".format(key))

  if len(missing) > 0:
    raise KeyError("Missing configuration value(s): {!s}".format(missing))


@six.add_metaclass(abc.ABCMeta)
class Configurator(object):

  @abc.abstractproperty
  def config_keys(self):
    pass  # noqa

  def __init__(self, config):
    check_config_values(self.config_keys, config)
    self.config = config

    self._debug = config.get('DEBUG', False)
