# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import os

import stethoscope.utils


LOGFILE = os.environ.get('STETHOSCOPE_LOGIN_LOGFILE', os.environ.get('LOGFILE', 'login.log'))

LOGBOOK = stethoscope.utils.setup_logbook(LOGFILE, logfile_kwargs={'delay': True})

DEBUG = True
TESTING = True

JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_DELTA = 60 * 60 * 24
