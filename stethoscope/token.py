# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import argparse

import arrow

import stethoscope.api.factory
import stethoscope.auth


def _main(args):
  config = stethoscope.api.factory.get_config()
  provider = stethoscope.auth.AuthProvider(config)
  print(provider.create_token(**{
    'sub': args.sub,
    'exp': arrow.utcnow().replace(days=+args.days_valid).datetime,
  }))


def main():
  parser = argparse.ArgumentParser(description=(
    "Generate a bearer token for auth with Stethoscope's API."
  ))
  parser.add_argument("--sub", dest="sub", type=str, default='*')
  parser.add_argument("--days-valid-for", dest="days_valid", type=int, default=1)
  _main(parser.parse_args())


if __name__ == "__main__":
  main()
