# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import os

import logbook
import logbook.more


LOGFILE = os.environ.get('LOGFILE', 'login.log')

LOGBOOK = logbook.NestedSetup([
    logbook.NullHandler(),
    logbook.more.ColorizedStderrHandler(level='INFO'),
    logbook.FileHandler(LOGFILE, mode='w', level='DEBUG', delay=True, bubble=True,
      format_string=('--------------------------------------------------------------------------\n'
                     '[{record.time} {record.level_name:<8s} {record.channel:>10s}]'
                     ' {record.filename:s}:{record.lineno:d}\n{record.message:s}')),
])

DEBUG = True
TESTING = True

JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_DELTA = 60 * 60 * 24
