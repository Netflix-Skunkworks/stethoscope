# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import os

import logbook


LOGLEVEL = os.environ.get('STETHOSCOPE_LOGIN_LOGLEVEL', os.environ.get('LOGLEVEL', 'INFO')).upper()
LOGFILE = os.environ.get('STETHOSCOPE_LOGIN_LOGFILE', os.environ.get('LOGFILE', 'login.log'))

LOGBOOK = logbook.NestedSetup([
    logbook.NullHandler(),
    logbook.MonitoringFileHandler(LOGFILE, mode='a', level=LOGLEVEL,
      format_string=('[{record.time} {record.level_name:<8s} {record.channel:>10s} |'
                     ' {record.filename:s}:{record.lineno:d}] {record.message:s}')),
])

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True

CSRF_COOKIE_HTTPONLY = False  # unnecessary
CSRF_COOKIE_SECURE = True

DEBUG = False
TESTING = False
