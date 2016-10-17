"""Test validators."""

from simpleconf import validators, Option
from pytest import raises

def test_quick_validator():
 """Test the QuickValidator class."""
 o = Option('http://www.google.com', title = '&URL', validator = validators.QuickValidator(lambda option: None if '://' in option.value else '%s does not look like a proper URL.' % option.value))
 assert o.check() is None
 with raises(validators.ValidationError):
  o.value = 'not a valid URL'
  o.check()
