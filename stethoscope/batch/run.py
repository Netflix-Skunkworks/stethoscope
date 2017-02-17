# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import argparse
import collections

from twisted.internet import defer
from twisted.internet import task
import arrow
import logbook
import six
import yaml

import stethoscope.api.factory
import stethoscope.plugins.utils


logger = logbook.Logger(__name__)


def arrow_representer(dumper, data):
  """Represent an `arrow.arrow.Arrow` object as a scalar in ISO format.

  >>> yaml.add_representer(arrow.arrow.Arrow, arrow_representer)
  >>> yaml.dump(arrow.get(1367900664))
  "! '2013-05-07T04:24:24+00:00'\\n"

  """
  return dumper.represent_scalar(u'!', six.text_type(data.isoformat(b'T' if six.PY2 else 'T')))


def dump_to_yaml(devices, filename):
  with open(filename, 'w') as fo:
    fo.write(yaml.safe_dump(devices, default_flow_style=False))
  return devices


def augment_device(device, email):
  if '_raw' in device:
    del device['_raw']
  device['email'] = email
  device['report_date'] = arrow.utcnow().to('US/Pacific')
  return device


def augment_devices(devices, email):
  return list(six.moves.map(lambda dev: augment_device(dev, email), devices))


def gather_statistics(devices_by_user):
  """Gather aggregate statistics on device status from given devices.

  >>> user = [{'practices': {'foo': {'status': 'warn'}, 'bar': {'status': 'nudge'}}}]
  >>> expected = {'foo': {'warn': 2}, 'bar': {'nudge': 2}}
  >>> expected == gather_statistics({'user_a': user, 'user_b': user})
  True

  """
  counts = collections.defaultdict(collections.Counter)
  for user, devices in six.iteritems(devices_by_user):
    for device in devices:
      for practice, practice_data in six.iteritems(device['practices']):
        counts[practice][practice_data['status']] += 1
  return dict((key, dict(val)) for key, val in six.iteritems(counts))


def wrap_hook(func):
  def _hook(devices, *args, **kwargs):
    func(devices, *args, **kwargs)
    return devices
  return _hook


def work_generator(args, config, emails, results):
  device_plugins = stethoscope.plugins.utils.instantiate_plugins(config,
      namespace='stethoscope.plugins.sources.devices')
  predevice_plugins = stethoscope.plugins.utils.instantiate_plugins(config,
      namespace='stethoscope.plugins.sources.predevices')

  hook_iter = stethoscope.plugins.utils.instantiate_plugins(config,
      namespace='stethoscope.batch.plugins.incremental')
  incremental_hooks = [wrap_hook(hook.obj.post) for hook in hook_iter]

  def apply_practices(devices):
    return six.moves.map(stethoscope.api.practices.apply_practices, devices)

  for email in emails:
    deferred = stethoscope.api.factory.get_devices_by_stages(email, predevice_plugins,
        device_plugins)
    deferred.addCallback(stethoscope.api.factory.filter_devices)
    deferred.addCallback(apply_practices)
    deferred.addCallback(stethoscope.api.devices.merge_devices)

    def log_results(devices, _email):
      logger.debug("retrieved {:d} devices for {!s}".format(len(devices), _email))
      return devices
    deferred.addCallback(log_results, email)

    deferred.addCallback(augment_devices, email)

    if not args.collect_only:
      for hook in incremental_hooks:
        deferred.addCallback(hook, email)

    def collect(devices, _email):
      results[_email] = devices
      return devices
    deferred.addCallback(collect, email)

    deferred.addErrback(logger.error)

    # deferred.addCallback(dump_to_yaml, os.path.join('batch', email + '.yaml'))
    logger.info("[{!s}] task generated".format(email))
    yield deferred


def _main(reactor, args, config):
  summary_hooks = stethoscope.plugins.utils.instantiate_plugins(config,
      namespace='stethoscope.batch.plugins.summary')

  if args.input is None:
    emails = config['BATCH_GET_EMAILS']()
  else:
    emails = [email.strip().strip('"') for email in args.input.readlines()]
  logger.info("retrieving devices for {:d} users", len(emails))

  results = dict()
  deferreds = list()
  cooperator = task.Cooperator()
  work = work_generator(args, config, emails, results)
  for idx in six.moves.range(args.limit):
    deferreds.append(cooperator.coiterate(work))

  deferred = defer.gatherResults(deferreds)

  def log_results(_):
    num_devices = sum(len(values) for values in six.itervalues(results))
    logger.info("retrieved {:d} unique devices for {:d} users", num_devices, len(emails))
    return _
  deferred.addCallback(log_results)

  if not args.collect_only:
    for summary_hook in summary_hooks:
      def _hook(_):
        summary_hook.obj.post(results)
        return _
      deferred.addCallback(_hook)

  return deferred


def main():
  parser = argparse.ArgumentParser(
    description="""Pull records for a batch of users and submit to external services."""
  )
  parser.add_argument('--timeout', dest="timeout", type=int, default=10)
  parser.add_argument('--limit', dest="limit", type=int, default=10,
      help="""Retrieve data for at most this many users simultaneously.""")

  parser.add_argument('--log-file', dest='logfile', default='batch.log')

  parser.add_argument('input', nargs='?', type=argparse.FileType('r'), default=None)

  parser.add_argument('--collect-only', dest="collect_only", action="store_true")
  parser.add_argument('--debug', dest="debug", action="store_true", default=False)

  config = stethoscope.api.factory.get_config()
  args = parser.parse_args()

  for plugin in ['BITFIT', 'JAMF']:
    config[plugin + '_TIMEOUT'] = args.timeout

  config['LOGBOOK'] = logbook.NestedSetup([
    logbook.NullHandler(),
    logbook.more.ColorizedStderrHandler(level='INFO', bubble=False,
      format_string='[{record.level_name:<8s} {record.channel:s}] {record.message:s}'),
    logbook.MonitoringFileHandler(args.logfile, mode='w', level='DEBUG', bubble=True,
      format_string=('--------------------------------------------------------------------------\n'
                     '[{record.time} {record.level_name:<8s} {record.channel:>10s}]'
                     ' {record.filename:s}:{record.lineno:d}\n{record.message:s}')),
  ])
  config['LOGBOOK'].push_application()

  config['DEBUG'] = args.debug
  config['TESTING'] = args.debug

  yaml.add_representer(arrow.arrow.Arrow, arrow_representer)
  yaml.SafeDumper.add_representer(arrow.arrow.Arrow, arrow_representer)

  task.react(_main, (args, config))


if __name__ == "__main__":
  main()
