# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import werkzeug.exceptions


class ValidationError(werkzeug.exceptions.BadRequest):

  def __init__(self, quantity, value, **kwargs):
    msg = "Invalid {!s}: '{!s}'.".format(quantity, value)
    super(ValidationError, self).__init__(msg, **kwargs)
