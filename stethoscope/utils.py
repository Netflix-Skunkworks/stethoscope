# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import datetime
import json

import arrow
import logbook
import six
import six.moves


try:
  # python 3.x
  from html import escape as html_escape
except ImportError:
  # python 2.x
  import cgi

  def html_escape(s):
    return cgi.escape(s, quote=True)


def copy_partial_dict(old_dict, key_mapping):
  """Copy values from `old_dict` into new `dict`, updating keys as in `key_mapping`.

  >>> copy_partial_dict({'old': 'foo'}, {'new': 'old'})
  {'new': 'foo'}

  """
  rv = dict()
  for key, old_key in six.iteritems(key_mapping):
    rv[key] = old_dict[old_key]
  return rv


def json_serialize_datetime(obj):
  """Serialize a `datetime.datetime` or `arrow.Arrow` by converting to string in ISO format.

  >>> import json
  >>> json.dumps(arrow.get("2015-05-16 10:37"), default=json_serialize_datetime)
  '"2015-05-16T10:37:00+00:00"'
  >>> json.dumps(datetime.datetime.utcfromtimestamp(1431772620), default=json_serialize_datetime)
  '"2015-05-16T10:37:00"'

  """
  if isinstance(obj, (datetime.datetime, arrow.Arrow)):
    return obj.isoformat(b'T' if six.PY2 else 'T')
  raise TypeError("{!r} is not JSON serializable".format(obj))


def json_pp(obj):
  """Encodes the given object as pretty-printed JSON and returns the resulting string."""
  return json.dumps(obj, sort_keys=True, indent=4, separators=(',', ': '),
      default=json_serialize_datetime)


def grouper(iterable, n, fillvalue=None):
  """Collect data into fixed-length chunks or blocks

  See https://docs.python.org/2/library/itertools.html.

  >>> [''.join(subiter) for subiter in grouper('ABCDEFG', 3, 'x')]
  ['ABC', 'DEF', 'Gxx']

  """
  # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
  args = [iter(iterable)] * n
  return six.moves.zip_longest(fillvalue=fillvalue, *args)


def setup_logbook(logfile, logfile_kwargs=None):
  """Return a basic `logbook` setup which logs to `stderr` and to file."""

  if logfile_kwargs is None:
    logfile_kwargs = {}

  logfile_kwargs.setdefault('level', 'DEBUG')
  logfile_kwargs.setdefault('mode', 'w')
  logfile_kwargs.setdefault('bubble', True)
  logfile_kwargs.setdefault('format_string',
      ('--------------------------------------------------------------------------\n'
       '[{record.time} {record.level_name:<8s} {record.channel:>10s}]'
       ' {record.filename:s}:{record.lineno:d}\n{record.message:s}'))

  logbook_setup = logbook.NestedSetup([
    logbook.NullHandler(),
    logbook.more.ColorizedStderrHandler(level='INFO', bubble=False,
      format_string='[{record.level_name:<8s} {record.channel:s}] {record.message:s}'),
    logbook.FileHandler(logfile, **logfile_kwargs),
  ])

  return logbook_setup
