# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import os

import logbook


LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
LOGFILE = os.environ.get('LOGFILE', 'api.log')

LOGBOOK = logbook.NestedSetup([
    logbook.NullHandler(),
    logbook.MonitoringFileHandler(LOGFILE, mode='a', level=LOGLEVEL,
      format_string=('[{record.time} {record.level_name:<8s} {record.channel:>10s} |'
                     ' {record.filename:s}:{record.lineno:d}] {record.message:s}')),
])

DEBUG = False
TESTING = False
