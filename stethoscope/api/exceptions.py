# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import werkzeug.exceptions


class NotFoundException(Exception):

  pass


class DeviceNotFoundException(NotFoundException):
  """Indicates that the device specified by `identifier` was not found by the raising plugin."""

  def __init__(self, identifier, service=None):
    self.identifier = identifier
    self.service = service

  def __str__(self):
    return "{!s}: device ({!s}) not found".format(self.service, self.identifier)


class UserNotFoundException(NotFoundException):
  """Indicates that the user specified by `email` was not found by the raising plugin."""

  def __init__(self, email, service=None):
    self.email = email
    self.service = service

  def __str__(self):
    return "{!s}: user ('{!s}') not found".format(self.service, self.email)


class InvalidResponseException(werkzeug.exceptions.BadGateway):
  """The raising plugin received an invalid HTTP response code from the external service."""

  def __init__(self, response_code, service=None, resource=None):
    msg = ("received invalid response code ({!s}) for {!r} from {!r}"
           "".format(response_code, resource, service))
    super(InvalidResponseException, self).__init__(msg)


class ErrorResponseException(InvalidResponseException):

  pass
