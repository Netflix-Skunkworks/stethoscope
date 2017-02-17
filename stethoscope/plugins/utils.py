# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import logbook
import six
import stevedore.named


logger = logbook.Logger(__name__)


def extension_load_failure_callback(manager, entrypoint, exception):
  logger.exception("failed to load extension from entrypoint {!r}".format(entrypoint))
  raise exception


def instantiate_plugins(config, **kwargs):
  kwargs.setdefault('propagate_map_exceptions', True)
  kwargs.setdefault('on_load_failure_callback', extension_load_failure_callback)
  kwargs.setdefault('verify_requirements', True)
  kwargs.setdefault('names', config.get('PLUGINS_ENABLED', six.viewkeys(config.get('PLUGINS', {}))))
  plugins = stevedore.named.NamedExtensionManager(**kwargs)
  logger.debug("'{!s}' plugins: loaded {!s}", kwargs['namespace'], plugins.names())
  for plugin in plugins:
    plugin_config = config.get('PLUGINS', {}).get(plugin.name, {})
    plugin_config.setdefault('DEBUG', config.get('DEBUG', False))
    plugin_config.setdefault('DEFAULT_TIMEOUT', config.get('DEFAULT_TIMEOUT', False))
    plugin.obj = plugin.plugin(plugin_config)
    plugin.obj.plugin_name = plugin.name
  logger.debug("'{!s}' plugins: instantiated {!s}", kwargs['namespace'], plugins.names())
  return plugins


def instantiate_practices(config, **kwargs):
  kwargs.setdefault('propagate_map_exceptions', True)
  kwargs.setdefault('on_load_failure_callback', extension_load_failure_callback)
  kwargs.setdefault('verify_requirements', True)
  kwargs.setdefault('names', config.get('PRACTICES_ENABLED',
    six.viewkeys(config.get('PRACTICES', {}))))
  practices = stevedore.named.NamedExtensionManager(**kwargs)
  logger.debug("'{!s}' practices: loaded {!s}", kwargs['namespace'], practices.names())
  for plugin in practices:
    plugin_config = config.get('PRACTICES', {}).get(plugin.name, {})
    plugin.obj = plugin.plugin(plugin_config)
    plugin.obj.plugin_name = plugin.name
  logger.debug("'{!s}' practices: instantiated {!s}", kwargs['namespace'], practices.names())
  return practices
