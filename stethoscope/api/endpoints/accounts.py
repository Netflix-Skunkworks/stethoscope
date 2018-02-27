# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import functools

import logbook
from twisted.internet import defer

import stethoscope.api.endpoints.utils
import stethoscope.plugins.utils
import stethoscope.validation
from stethoscope.api.endpoints.utils import add_get_route, log_access, log_response


logger = logbook.Logger(__name__)


def merge_accounts(accts):
  return list(acct for (status, acct) in accts if status)


def get_accounts_by_email(email, extensions):
  deferreds = []
  for ext in extensions:
    deferred = ext.obj.get_account_by_email(email)
    deferred.addCallback(functools.partial(log_response, 'account', ext.name))
    deferreds.append(deferred)

  return defer.DeferredList(deferreds, consumeErrors=True)


@stethoscope.api.endpoints.utils.serialized_endpoint(merge_accounts)
def merged_accounts(*args, **kwargs):
  """Endpoint returning (as JSON) all accounts after merging."""
  return get_accounts_by_email(*args, **kwargs)


def register_account_api_endpoints(app, config, auth, log_hooks=[]):
  account_plugins = stethoscope.plugins.utils.instantiate_plugins(config,
      namespace='stethoscope.plugins.sources.accounts')

  if config.get('ENABLE_ACCOUNT_ENDPOINTS', config['DEBUG']) and len(account_plugins.names()) > 0:
    account_plugins.map(add_get_route, app, auth, 'account', 'email', log_hooks=log_hooks)

  @auth.match_required
  @stethoscope.validation.check_valid_email
  def _merged_accounts(request, email, **_kwargs):
    userinfo = _kwargs.pop('userinfo')

    # required so that app.route can get a '__name__' attribute from decorated function
    _kwargs['callbacks'] = [
      functools.partial(log_response, 'account', 'merged'),
      functools.partial(log_access, 'account', userinfo, email, context='merged'),
    ] + [functools.partial(hook.obj.log, 'account', userinfo, email, context='merged')
        for hook in log_hooks]
    return merged_accounts(request, email, account_plugins, **_kwargs)
  app.route('/accounts/merged/<string:email>', endpoint='accounts-merged',
      methods=['GET'])(_merged_accounts)
