#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import io
import os.path
import sys
from itertools import chain

import setuptools


def parse_file(filename, encoding='utf-8'):
  """Return contents of the given file using the given encoding."""
  path = os.path.join(os.path.abspath(os.path.dirname(__file__)), filename)
  with io.open(path, encoding=encoding) as fo:
    contents = fo.read()
  return contents


extras_require = {
  'google': [
    'google-api-python-client',
    'httplib2',
    'oauth2client',
  ],
  'duo': ['duo_client'],
  'jamf': [],
  'landesk': [
    'pymssql',  # requires freetds (`brew install freetds`)
  ],
  'bitfit': [],
  'es_logger': [
    'elasticsearch>=2.0.0,<3.0.0',
  ],
  'es_notifications': [
    'elasticsearch_dsl>=2.0.0,<3.0.0',
  ],
  'restful_feedback': [],
  'batch': [
    'pyyaml',
    'requests[security]',
    'elasticsearch>=2.0.0,<3.0.0',
  ],
  'oidc': [
    'requests[security]',
    'requests-oauthlib',
  ],
  'vpn_labeler': ['netaddr'],
  're_filter': [],
  'mac_manufacturer': ['netaddr'],
  'atlas': [],
  'batch_es': ['elasticsearch>=2.0.0,<3.0.0'],
  'batch_restful_summary': ['requests'],
}

install_requires = [
  'Flask>=0.10',  # 0.10 introduced better security for session cookies
  'Flask-Script',
  'arrow',
  'klein',
  'logbook',
  'PyJWT>=1.4.2',  # 1.4.2 contains a bugfix for a parsing issue in JWT decoding
  'PyOpenSSL',
  'six',
  'service-identity',
  # 39.0.0 removed `SetuptoolsVersion` in favor of `packaging.version.Version`
  # See: https://github.com/pypa/setuptools/commit/eeeb9b27fa48fccf2b5d52919eff1c75c4ad1718
  'setuptools>=39.0.0',
  'stevedore',
  'treq',
  'Twisted',
  'txretry>=1.0.1',  # 1.0.1 introduced support for Python 3
  'txwebretry',
  'validate-email',
  'werkzeug>=0.9',  # 0.9 added werkzeug.wsgi.host_is_trusted
]

if sys.version_info < (2, 7, 9):
  # SSL connection fixes for Python 2.7
  install_requires.extend([
    'ndg-httpsclient',
    'pyasn1',
  ])

setup_params = dict(
  name='Stethoscope',
  version='0.1.1',
  author='Andrew M. White',
  author_email='andreww@netflix.com',
  license='Apache License, Version 2.0',
  description=("""Collection and display of best practice adoption for securing user devices """
               """and accounts."""),
  long_description=parse_file('README.md'),
  classifiers=[
    'Development Status :: 4 - Beta',
    'Intended Audience :: Information Technology',
    'Framework :: Flask',
    'Framework :: Twisted',
    'License :: OSI Approved :: Apache Software License',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Topic :: Education',
    'Topic :: Security',
  ],
  keywords=['security education'],
  packages=setuptools.find_packages(),
  zip_safe=False,
  include_package_data=True,
  setup_requires=[
    'setuptools-git',  # >=0.3
    'pytest-runner',
  ],
  tests_require=[
    'mock',
    'pytest-cov',
    'pytest-logbook',
    'pytest>=2.8',
    'setuptools>=17.1',
  ] + list(chain.from_iterable(extras_require.values())) + install_requires,
  extras_require=extras_require,
  install_requires=install_requires,
  dependency_links=[
    'git+https://github.com/duosecurity/duo_client_python.git@1cc71f80927b02e75773094c9dd77af1fc8e4064.zip#egg=duo_client-3.0',  # noqa
    'git+https://github.com/wrapp/txwebretry.git@df5014019cf3a5d501bc755b9ce46509c1b31351#egg=txwebretry-0.1.1',  # noqa
  ],
  entry_points={
    'console_scripts': [
      'stethoscope-login = stethoscope.login.manage:main',
      'stethoscope-batch = stethoscope.batch.run:main [batch]',
      'stethoscope-token = stethoscope.token:main',
      'stethoscope-connectivity = stethoscope.connectivity:main',
    ],
    'stethoscope.plugins.login': [
      # authentication drivers
      'oidc = stethoscope.login.plugins.oidc:OpenIDConnectLogin [oidc]',
      'null = stethoscope.login.plugins.base:NullLogin',
    ],
    'stethoscope.plugins.sources.events': [
      # event gathering plugins
      'google = stethoscope.plugins.sources.google.deferred:DeferredGoogleDataSource [google]',
      'duo = stethoscope.plugins.sources.duo.deferred:DeferredDuoDataSource [duo]',
    ],
    'stethoscope.plugins.sources.devices': [
      # device gathering plugins
      'google = stethoscope.plugins.sources.google.deferred:DeferredGoogleDataSource [google]',
      'jamf = stethoscope.plugins.sources.jamf.deferred:DeferredJAMFDataSource [jamf]',
      # 'bitfit = stethoscope.plugins.sources.bitfit.deferred:DeferredBitfitDataSource [bitfit]',
      'landesk = stethoscope.plugins.sources.landesk.deferred:DeferredLandeskSQLDataSource [landesk]',  # noqa
    ],
    'stethoscope.plugins.sources.predevices': [
      # device gathering plugins to which should run first to gather, e.g., MAC addresses
      'bitfit = stethoscope.plugins.sources.bitfit.deferred:DeferredBitfitDataSource [bitfit]',
    ],
    'stethoscope.plugins.sources.userinfo': [
      # userinfo gathering plugins
      'google = stethoscope.plugins.sources.google.deferred:DeferredGoogleDataSource [google]',
      'jamf = stethoscope.plugins.sources.jamf.deferred:DeferredJAMFDataSource [jamf]',
      'bitfit = stethoscope.plugins.sources.bitfit.deferred:DeferredBitfitDataSource [bitfit]',
    ],
    'stethoscope.plugins.sources.accounts': [
      # account information gathering plugins
      'google = stethoscope.plugins.sources.google.deferred:DeferredGoogleDataSource [google]',
    ],
    'stethoscope.plugins.sources.notifications': [
      'es_notifications = stethoscope.plugins.sources.esnotifications:ElasticSearchNotifications [es_notifications]',  # noqa
    ],
    'stethoscope.plugins.practices.devices': [
      'autoupdate = stethoscope.plugins.practices:KeyExistencePractice',
      'encryption = stethoscope.plugins.practices:KeyExistencePractice',
      'firewall = stethoscope.plugins.practices:KeyExistencePractice',
      'remotelogin = stethoscope.plugins.practices:KeyExistencePractice',
      'jailed = stethoscope.plugins.practices:KeyExistencePractice',
      'screenlock = stethoscope.plugins.practices:KeyExistencePractice',
      'unknownsources = stethoscope.plugins.practices:KeyExistencePractice',
      'adbstatus = stethoscope.plugins.practices:KeyExistencePractice',
      'uptodate = stethoscope.plugins.practices:UptodatePractice',
      # installed software
      'carbonblack = stethoscope.plugins.practices:InstalledSoftwarePractice',
      'sentinel = stethoscope.plugins.practices:InstalledSoftwarePractice',
    ],
    'stethoscope.plugins.feedback': [
      'restful_feedback = stethoscope.plugins.feedback.restful:RESTfulFeedback [restful_feedback]',
    ],
    'stethoscope.plugins.transform.events': [
      # hooks to transform events (e.g., by adding geolocation data)
      'vpn_labeler = stethoscope.plugins.transform.vpnlabeler:VPNLabeler [vpn_labeler]',
    ],
    'stethoscope.plugins.transform.devices': [
      # hooks to transform devices (e.g., by adding manufacturer information from MAC addresses)
      'mac_manufacturer = stethoscope.plugins.transform.macmanufacturer:AddMACManufacturer [mac_manufacturer]',  # noqa
      're_filter = stethoscope.plugins.transform.refilter:FilterMatching [re_filter]',
    ],
    'stethoscope.plugins.logging.request': [
      # hooks to log api requests (e.g., accesses) externally
      'es_logger = stethoscope.plugins.logging.eslogger:ElasticSearchAccessLogger [es_logger]',
    ],
    'stethoscope.plugins.logging.failure': [
      # hooks to log api failures externally
      'atlas = stethoscope.plugins.logging.atlas:AtlasLogger [atlas]',
    ],
    'stethoscope.batch.plugins.incremental': [
      # plugins for handling (e.g., logging) entries one-at-a-time during batch processing
      'batch_es = stethoscope.batch.plugins.incremental.es:ElasticSearchBatchLogger [batch_es]',
    ],
    'stethoscope.batch.plugins.summary': [
      # plugins for summarizing all entries after batch processing
      'batch_restful_summary = stethoscope.batch.plugins.summary.restful:RESTfulSummary [batch_restful_summary]',  # noqa
    ]
  },
)

if __name__ == "__main__":
  setuptools.setup(**setup_params)
