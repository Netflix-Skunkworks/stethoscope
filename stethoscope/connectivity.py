# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

from itertools import chain
import argparse
import collections
import operator

from twisted.internet import defer
from twisted.internet import task
import logbook
import six.moves

import stethoscope.api.factory
import stethoscope.plugins.utils
import stethoscope.utils


logger = logbook.Logger(__name__)

DEFAULT_NAMESPACES = (
    # 'stethoscope.plugins.transform.devices',
    'stethoscope.plugins.sources.predevices',
    'stethoscope.plugins.sources.devices',
    'stethoscope.plugins.sources.events',
    # 'stethoscope.plugins.transform.events',
    # 'stethoscope.plugins.sources.userinfo',
    'stethoscope.plugins.sources.accounts',
    'stethoscope.plugins.sources.notifications',
    # 'stethoscope.plugins.feedback',
    # 'stethoscope.plugins.logging.failure',
    'stethoscope.plugins.logging.request',
  )


def initialize_plugins(args, config):
  """Instantiate configured plugins and return a list of those with a `test_connectivity` method."""
  plugins = collections.defaultdict(list)
  for namespace in args.namespaces:
    for plugin in stethoscope.plugins.utils.instantiate_plugins(config, namespace=namespace):
      if hasattr(plugin.obj, 'test_connectivity'):
        plugins[namespace].append(plugin)
      else:
        logger.warning("Plugin has no connectivity test: '{!s}'.", plugin.name)
  return plugins


def handle_success(chain_arg, namespace, plugin_name):
  logger.info("Successful test for {!s}::{!s}.", namespace, plugin_name)
  return chain_arg


def handle_failure(failure, namespace, plugin_name):
  logger.error("Failure in {!s}::{!s}:\n{!s}", namespace, plugin_name, failure.value)
  return failure


def work_generator(args, config):
  namespaced_plugins = initialize_plugins(args, config)

  for namespace, plugins in six.iteritems(namespaced_plugins):
    for plugin in plugins:
      deferred = plugin.obj.test_connectivity()

      callback_args = (namespace, plugin.name)

      deferred.addCallbacks(handle_success, callbackArgs=callback_args,
          errback=handle_failure, errbackArgs=callback_args)

      logger.debug("[{:s}] task generated".format(plugin.name))
      yield deferred


def tabulate_results(results):
  successes = len([success for (success, _) in results if success])
  logger.info("{:d} of {:d} tests concluded successfully.", successes, len(results))


def _main(reactor, args, config):
  deferreds = [deferred for deferred in work_generator(args, config)]
  deferred_list = defer.DeferredList(deferreds)
  deferred_list.addCallback(tabulate_results)
  return deferred_list


def main():
  parser = argparse.ArgumentParser(
    description="""Test connectivity for the plugins which support connectivity tests."""
  )

  parser.add_argument('--log-file', dest='logfile', default='connectivity.log')
  parser.add_argument('--debug', dest="debug", action="store_true", default=False)

  parser.add_argument('--namespaces', dest='namespaces', type=str, nargs='+',
                      default=DEFAULT_NAMESPACES,
                      help='Namespaces containing plugins to instantiate and test.')

  config = stethoscope.api.factory.get_config()
  args = parser.parse_args()

  config['LOGBOOK'] = stethoscope.utils.setup_logbook(args.logfile)
  config['LOGBOOK'].push_application()

  config['DEBUG'] = args.debug
  config['TESTING'] = args.debug

  task.react(_main, (args, config))


if __name__ == "__main__":
  main()
