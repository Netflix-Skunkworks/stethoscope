# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import json

import logbook
import six
import werkzeug.exceptions

import stethoscope.plugins.mixins.deferred_http
import stethoscope.validation
import stethoscope.configurator
import stethoscope.exceptions


logger = logbook.Logger(__name__)


class RESTfulFeedback(
    stethoscope.plugins.mixins.deferred_http.DeferredHTTPMixin,
    stethoscope.configurator.Configurator
  ):
  """Example of a feedback plugin which posts feedback via RESTful HTTP(S) to an external server."""

  def validate(self, payload):
    for field in ('feedback', 'notes', 'id'):
      if field not in payload:
        raise werkzeug.exceptions.BadRequest(description="Field '{:s}' is required.".format(field))

    if not isinstance(payload['feedback'], six.string_types):
      raise stethoscope.exceptions.ValidationError('feedback', payload['feedback'])

    if not isinstance(payload['notes'], six.string_types):
      raise stethoscope.exceptions.ValidationError('notes', payload['notes'])

  def create_feedback_object(self, email, payload):
    return {
      'user_id': email,
      'feedback': payload['feedback'],
      'notes': payload['notes'],
      'id': payload['id'],
      'source': 'stethoscope'
    }

  def post_feedback(self, email, payload):
    self.validate(payload)
    feedback = self.create_feedback_object(email, payload)

    deferred = super(RESTfulFeedback, self).post(feedback)
    deferred.addCallback(json.loads)
    return deferred
