# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

from datetime import datetime

import arrow
import logbook


logger = logbook.Logger(__name__)

DUO_BATCH_SIZE = 1000


def get_auth_log(admin_api, start, end):
  """Connect to Duo's admin API and retrieve authentication log entries."""
  logger.debug("retrieving entries for period {:s} to {:s}",
      datetime.fromtimestamp(start).isoformat(), datetime.fromtimestamp(end).isoformat())

  auth_log = list()
  timestamp = start
  while timestamp < end:
    try:
      new_entries = admin_api.get_authentication_log(mintime=timestamp)
    except RuntimeError as exc:
      logger.error("error retrieving Duo authentication data: {!s}", exc)
      break

    logger.debug("retrieved {:d} entries for timestamp {:d} ({:s})", len(new_entries), timestamp,
        datetime.fromtimestamp(timestamp).isoformat())
    auth_log.extend(new_entries)
    if len(new_entries) < DUO_BATCH_SIZE:
        break
    timestamp = new_entries[-1]['timestamp']

  logger.debug("retrieved {:d} new entries", len(auth_log))
  return auth_log


def parse_duo_auth_log(auth_log):
  """Parse entries in Duo's authentication log format."""
  events = list()
  for entry in auth_log:
    dt = arrow.get(entry['timestamp'])
    event = {
      'source': 'duo',
      'type': entry['factor'],
      'reason': entry['reason'],
      'timestamp': dt,
      'ip_address': entry['ip'],
      'username': entry['username'],
      'success': True if entry['result'] == "SUCCESS" else False,
      'content': (
        "Duo Authentication: {dt!s}<br/>"
        "IP: {ip!s}<br/>"
        "Event Type: {eventtype!s}<br/>"
        "Device: {device!s}<br/>"
        "Factor: {factor!s}<br/>"
        "Integration: {integration!s}<br/>"
        "Result: {result!s}<br/>"
        "Reason: {reason!s}<br/>"
        "Enrollment: {new_enrollment!s}<br/>"
      ).format(dt=dt, **entry),
      '_raw': entry,
    }
    # logger.debug("DUO AUTH LOG ENTRY: {!s}\n  entry: {!r}\n  event: {!r}", dt, entry, event)
    events.append(event)
  return events
