# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import os

import logbook
import logbook.more

import stethoscope.utils


LOGFILE = os.environ.get('STETHOSCOPE_API_LOGFILE', os.environ.get('LOGFILE', 'api.log'))

LOGBOOK = stethoscope.utils.setup_logbook(LOGFILE, logfile_kwargs={'delay': True})

DEBUG = True
TESTING = True

JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_DELTA = 60 * 60 * 24


def IS_PRIVILEGED_USER(userinfo):
  return userinfo['sub'] == '*'

MOBILE_PLATFORMS = ['Android', 'iOS']
NONMOBILE_PLATFORMS = ['Mac', 'Windows']

PRACTICES = {
  'jailed': {
    'KEY': 'jailed',
    'DISPLAY_TITLE': 'Verified Operating System',
    'DESCRIPTION': (
      "Modifying the basic operating system (known as \"jailbreaking\" or \"rooting\") "
      "of a device increases the risk of infection or compromise by exposing additional "
      "security vulnerabilities."
    ),
    'LINK': '#',
    'STATUS_IF_MISSING': 'warn',
    'NA_PLATFORMS': NONMOBILE_PLATFORMS,
  },

  'encryption': {
    'KEY': 'encryption',
    'DISPLAY_TITLE': 'Disk Encryption',
    'DESCRIPTION': (
      "Full-disk encryption protects data at rest from being accessed by a "
      "party who does not know the password or decryption key."
    ),
    'LINK': '#',
    'STATUS_IF_MISSING': 'warn',
    'PLATFORM_REQUIRED': True,
  },

  'uptodate': {
    'KEY': 'uptodate',
    'DISPLAY_TITLE': 'Up-to-date',
    'DESCRIPTION': (
      "One of the most important things you can do to secure your device(s) is to "
      "keep your operating system and software up to date. New vulnerabilities and "
      "weaknesses are found every day, so frequent updates are essential to ensuring "
      "your device(s) include the latest fixes and preventative measures."
    ),
    'LINK': '#',
    'REQUIRED_VERSIONS': {
        'Mac OS X': '10.11.0',
        'iOS': '9.3.5',
        'Android': '6.0.0',
    },
    'RECOMMENDED_VERSIONS': {
        'Mac OS X': '10.11.6',
        'iOS': '9.3.5',
        'Android': '6.0.1',
    }
  },

  'autoupdate': {
    'KEY': 'autoupdate',
    'DISPLAY_TITLE': 'Automatic Updates',
    'DESCRIPTION': (
      "One of the most important things you can do to secure your device(s) is to "
      "keep your operating system and software up to date. New vulnerabilities and "
      "weaknesses are found every day, so frequent updates are essential to ensuring "
      "your device(s) include the latest fixes and preventative measures. "
      "Enabling automatic updating helps ensure your machine is up-to-date without "
      "having to manually install updates."
    ),
    'LINK': '#',
    'PLATFORM_REQUIRED': True,
    'NA_PLATFORMS': MOBILE_PLATFORMS,
  },

  'firewall': {
    'KEY': 'firewall',
    'DISPLAY_TITLE': 'Firewall',
    'DESCRIPTION': (
      "Firewalls control network traffic into and out of a system. Enabling the firewall on "
      "your device can prevent network-based attacks on your system, and is especially "
      "important if you make use of insecure wireless networks (such as at coffee shops and "
      "airports)."
    ),
    'LINK': '#',
    'STATUS_IF_MISSING': 'warn',
    'PLATFORM_REQUIRED': True,
    'NA_PLATFORMS': MOBILE_PLATFORMS,
  },

  'remotelogin': {
    'KEY': 'remotelogin',
    'DISPLAY_TITLE': 'Remote Login Disabled',
    'DESCRIPTION': (
      "The 'Remote Login' setting on your Mac controls whether users can login remotely "
      "to the system using SSH. If you don't know what this is or why you would want it, "
      "you should disable 'Remote Login'."
    ),
    'LINK': '#',
    'PLATFORM_REQUIRED': True,
    'NA_PLATFORMS': MOBILE_PLATFORMS + ["Windows"],
  },

  'screenlock': {
    'KEY': 'screenlock',
    'DISPLAY_TITLE': 'Screen Lock',
    'DESCRIPTION': (
      "Screen locks, or screen saver locks, prevent unauthorized third-parties from "
      "accessing your laptop when unattended by requiring a password to dismiss the screen "
      "saver or wake from \"sleep\" mode. Setting the timeout, i.e., the length of idle "
      "time before the screen saver takes effect, to 10 minutes or less is also recommended."
    ),
    'LINK': '#',
    'STATUS_IF_MISSING': 'warn',
  },

  'sentinel': {
    'KEY': 'sentinel',
    'SOFTWARE_NAMES': ['Sentinel Agent'],
    'SERVICE_NAMES': ['com.sentinelone.sentineld'],
    'DISPLAY_TITLE': 'SentinelOne',
    'DESCRIPTION': (
      "SentinelOne is part of our approach to preventing and detecting malware "
      "infections. Installing SentinelOne helps protect your system and helps us detect "
      "when a system has been compromised, and how, so we can respond quickly and "
      "effectively."
    ),
    'LINK': '#',
    'PLATFORM_REQUIRED': True,
    'NA_PLATFORMS': MOBILE_PLATFORMS,
  },

  'carbonblack': {
    'KEY': 'carbonblack',
    'SOFTWARE_NAMES': ['Carbon Black Sensor'],
    'SERVICE_NAMES': ['com.carbonblack.daemon'],
    'DISPLAY_TITLE': 'Carbon Black',
    'DESCRIPTION': (
      "Carbon Black is part of our approach to preventing and detecting malware "
      "infections. Installing Carbon Black helps protect your system and helps us "
      "detect when a system has been compromised, and how, so we can respond quickly and "
      "effectively."
    ),
    'LINK': '#',
    'PLATFORM_REQUIRED': True,
    'NA_PLATFORMS': MOBILE_PLATFORMS,
  },

  'unknownsources': {
    'KEY': 'unknownsources',
    'DISPLAY_TITLE': 'Unknown Sources Disabled',
    'DESCRIPTION': (
      "Apps from unknown sources are more likely to contain malware than apps "
      "downloaded from the Play Store. Keeping this setting disabled prevents "
      "the installation of these apps."
    ),
    'PLATFORM_REQUIRED': True,
    'NA_PLATFORMS': ['iOS'] + NONMOBILE_PLATFORMS,
  },

  'adbstatus': {
    'KEY': 'adbstatus',
    'DISPLAY_TITLE': 'Android Debug Bridge Disabled',
    'DESCRIPTION': (
      "The Android Debug Bridge (ADB) is a debugging tool intended for use by Android developers. "
      "Enabling ADB provides enhanced access to a device via both USB and wireless interfaces, "
      "which presents a security risk (one that has been exploited in the past)."
    ),
    'PLATFORM_REQUIRED': True,
    'NA_PLATFORMS': ['iOS'] + NONMOBILE_PLATFORMS,
  },
}
