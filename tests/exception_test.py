"""Test exceptions."""

from pytest import raises
from simpleconf import exceptions

def test_message():
 """Make sure the message on the resulting exception is the same as the one that was put in."""
 e = exceptions.SimpleConfError()
 assert e.message == e.__doc__
 message = 'testing'
 assert str(exceptions.SimpleConfError(message)) == message
 assert exceptions.ValidationError(message).message is message
 assert exceptions.DataMissingError('test').message == 'Missing data: test.'
