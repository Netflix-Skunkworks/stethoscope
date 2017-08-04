# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import pprint

import pytest

import stethoscope.plugins.practices


def test_key_existence_practice():
  practice = stethoscope.plugins.practices.KeyExistencePractice({
    'KEY': 'foo',
    'DISPLAY_TITLE': 'The display title',
    'DESCRIPTION': 'The description',
  })

  device = {
    'practices': {
      'foo': {
        'value': True,
      },
    },
  }

  practice.inject_status(device)

  assert device == {
    'practices': {
      'foo': {
        'value': True,
        'display': True,
        'status': 'ok',
        'title': 'The display title',
        'description': 'The description',
      },
    },
  }
