"""
Various validating functions for use with options.

Each validator should be a sub class of Validator, and be prepared to take the option it will be checking as an argument to it's validate method.

Important attributes:
option.value: The current value of the option.
option.default: The default value for the option.
option.section: The section this option is a part of.

If a value is not valid, the function should raise a subclass of exceptions.ValidationError.

To implement tests for your validators, create a test method which accepts an option argument.

You can use the provided option for testing, altering it's properties to suit your needs. By default it will have self as it's validator.

To test with exceptions, use the Validator.raises context manager. By default it expects ValidationError, so you can do:
with self.raises():
 <code>

Or:
with self.raises(ValueError):
 <code>
"""

import six, re
from .exceptions import ValidationError
from contextlib import contextmanager

class Validator(object):
 """The base class from which all validators are derived."""
 
 def validate(self, option):
  """Check option.value."""
  raise NotImplementedError('Use a proper validator.')
 
 def test(self, *args, **kwargs):
  """Run tests on this validator."""
  raise NotImplementedError
 
 @contextmanager
 def raises(self, error_type = ValidationError):
  """Check whether code raises error_type."""
  try:
   yield
  except error_type:
   return None

class Boolean(Validator):
 """Ensure the provided value is a boolean."""
 
 def validate(self, option):
  """Checks if the value is True or False."""
  if not isinstance(option.value, bool):
   raise ValidationError('Invalid value for True or False: %r.' % option.value)
 
 def test(self, o):
  o.value = True
  o.check()
  o.value = False
  o.check()
  o.value = 5
  with self.raises():
   o.check()

class Integer(Validator):
 """Ensure the provided value is an integer. If min and or max are provided, ensure the value is in that range."""
 
 def __init__(self, min = None, max = None):
  """Set a minimum and a maximum."""
  self.min = min
  self.max = max
 
 def validate(self, option):
  """Check that value is no smaller than self.min and no larger than self.max."""
  v = option.value
  if not isinstance(v, int):
   raise ValidationError('Not an integer: %r.' % v)
  if (self.min is not None and v < self.min) or (self.max is not None and v > self.max):
   raise ValidationError('Expecting an integer between %s and %s.' % ('anything' if self.min is None else self.min, 'anything' if self.max is None else self.max))
 
 def test(self, o):
  o.value = 'hello world'
  with self.raises():
   o.check()
  o.value = 1
  o.check()
  self.min = 2
  with self.raises():
   o.check()
  self.min = None
  self.max = 0
  with self.raises():
   o.check()
  self.min = 2
  with self.raises():
   o.check()

class String(Validator):
 """Ensure the provided value is a string."""
 
 def validate(self, option):
  """Checks that the value is a string."""
  if not isinstance(option.value, six.string_types):
   raise ValidationError('Expected a string, not %r.' % option.value)
 
 def test(self, o):
  o.value = 'hello world'
  o.check()
  o.value = 5
  with self.raises():
   o.check()

class RestrictedString(String):
 """Ensure the provided value is a string which conforms to the provided restrictions."""
 
 def __init__(self, min = None, max = None):
  """Set the min and max lengths."""
  self.min = min
  self.max = max
 
 def pluralise(self, value, single, plural = None):
  """Get a string with the proper pluralisation."""
  if plural is None:
   plural = single + 's'
  if value == 1:
   return single
  else:
   return plural
 
 def validate(self, option):
  """Ensures that the string is no shorter than self.min, and no longer than self.max."""
  v = option.value
  super(RestrictedString, self).validate(option) # Ensure it's actually a string.
  if (self.min is not None and len(v) < self.min) or (self.max is not None and len(v) > self.max):
   if self.min == self.max:
    suggest = 'exactly %d %s' % (self.min, self.pluralise(self.min, 'character'))
   else:
    if self.min is None:
     if self.max is None:
      suggest = 'any length' # Should never happen.
     else:
      suggest = 'up to %d %s' % (self.max, self.pluralise(self.max, 'character'))
    else:
     suggest = 'at least %d %s' % (self.min, self.pluralise(self.min, 'character'))
   raise ValidationError('Expected a string of %s.' % suggest)
 
 def test(self, o):
  o.value = 'hello'
  o.check()
  self.min = 9
  with self.raises():
   o.check()
  self.max = 1
  with self.raises():
   o.check()
  self.min = None
  with self.raises():
   o.check()

class RegexpString(String):
 """Ensure the provided value conforms to a regular expression."""
 
 def __init__(self, pattern = '.*', message = 'Value "{}" does not match the pattern: "{}".'):
  """Pattern can be either a plain old string or a compiled regular expression."""
  if isinstance(pattern, six.string_types):
   pattern = re.compile(pattern)
  self.pattern = pattern
  self.message = message
 
 def validate(self, option):
  """Check the option against self.pattern."""
  super(RegexpString, self).validate(option) # Ensure the value is actually a string.
  if self.pattern.match(option.value) is None:
   raise ValidationError(self.message.format(option.value, self.pattern.pattern))
 
 def test(self, o):
  self.pattern = re.compile('.+')
  o.value = 'hello'
  o.check()
  o.value = ''
  with self.raises():
   o.check()
  o.value = None
  with self.raises():
   o.check()

class Float(Validator):
 """Ensure the provided value is a float."""
 
 def __init__(self, min = None, max = None):
  """Set a min and max."""
  self.min = min
  self.max = max
 
 def validate(self, option):
  """Ensure that option.value is between self.min and self.max."""
  v = option.value
  if not isinstance(option.value, float):
   raise ValidationError('%s is not a floating point number.' % v)
  if (self.min is not None and v < self.min) or (self.max is not None and v > self.max):
   raise ValidationError('Expecting a floating point number between %s and %s.' % ('anything' if self.min is None else self.min, 'anything' if self.max is None else self.max))
 
 def test(self, o):
  o.value = 1.0
  o.check()
  o.value = 1
  with self.raises():
   o.check()
  o.value = 1.0
  self.min = 2.0
  with self.raises():
   o.check()
  self.max = 0.0
  with self.raises():
   o.check()
  self.min = None
  with self.raises():
   o.check()

class Option(Validator): 
 """Ensure the provided value is in options."""
 
 def __init__(self, *options):
  """Store the list of possible options."""
  self.options = options
 
 def validate(self, option):
  """Check that option.value is in self.options."""
  if option.value not in self.options:
   raise ValidationError('%s is not in %s.' % (option.value, self.options))
 
 def test(self, o):
  o.value = 1
  self.options = [1, 2, 3]
  o.check()
  o.value = None
  with self.raises():
   o.check()

class QuickValidator(Validator):
 """Quickly add a new validator."""
 
 def __init__(self, func = lambda option: 'This function will always fail.'):
  """
  The validate method will use func to check the data.
  
  If it returns None, the data is assumed to be OK.
  
  Any other value will be turned into a ValidationError via str.
  """
  self.func = func
 
 def validate(self, option):
  res = self.func(option)
  if res is not None:
   raise ValidationError(str(res))
 
 def test(self, o):
  self.func = lambda option: None if option.value is None else 'Not None.'
  o.value = None
  o.check()
  o.value = 1
  with self.raises():
   o.check()

class List(Validator):
 """Ensure the provided value is a list."""
 
 def __init__(self, min = None, max = None):
  """Set a minimum and maximum length."""
  self.min = min
  self.max = max
 
 def validate(self, option):
  if not isinstance(option.value, list):
   raise ValidationError('Not a list: %r.' % option.value)
  v = len(option.value)
  if (self.min is not None and v < self.min) or (self.max is not None and v > self.max):
   raise ValidationError('Expecting a list between %s and %s long.' % ('anything' if self.min is None else self.min, 'anything' if self.max is None else self.max))
 
 def test(self, o):
  o.value = ['hello', 'world']
  o.check()
  o.value = 1
  with self.raises():
   o.check()
  o.value = [1, 2, 3]
  self.min = 5
  with self.raises():
   o.check()
  self.max = 2
  with self.raises():
   o.check()
  self.min = None
  with self.raises():
   o.check()

class Dict(Validator):
 """Ensure the provided value is a dictionary."""
 
 def __init__(self, min = None, max = None):
  """Provide a min and a max."""
  self.min = min
  self.max = max
 
 def validate(self, option):
  if not isinstance(option.value, dict):
   raise ValidationError('Not a dictionary: %r.' % option.value)
  v = len(option.value)
  if (self.min is not None and v < self.min) or (self.max is not None and v > self.max):
   raise ValidationError('Expecting a dictionary between %s and %s big.' % ('anything' if self.min is None else self.min, 'anything' if self.max is None else self.max))
 
 def test(self, o):
  o.value = {}
  o.check()
  o.value = []
  with self.raises():
   o.check()
  o.value = {'hello': 'world'}
  self.min = 2
  with self.raises():
   o.check()
  self.max = 2
  with self.raises():
   o.check()
  self.min = None
  with self.raises():
   o.check()
