"""
Various validating functions for use with options.

Each validator should be a sub class of Validator, and be prepared to take the option it will be checking as an argument to it's validate method.

Important attributes:
option.value: The current value of the option.
option.default: The default value for the option.
option.section: The section this option is a part of.

If a value is not valid, the function should raise a subclass of exceptions.ValidationError.
"""

import six
from .exceptions import ValidationError

class Validator(object):
 """The base class from which all validators are derived."""
 
 def validate(self, option):
  """Check option.value."""
  raise NotImplementedError('Use a proper validator.')

class Boolean(Validator):
 def validate(self, option):
  """Checks if the value is True or False."""
  if not isinstance(option.value, bool):
   raise ValidationError('Invalid value for True or False: %s.' % option.value)

class Integer(Validator):
 def __init__(self, min = None, max = None):
  """Set a minimum and a maximum."""
  self.min = min
  self.max = max
 
 def validate(self, option):
  """Check that value is no smaller than self.min and no larger than self.max."""
  v = option.value
  if not isinstance(v, int):
   raise ValidationError('%s is not an integer.' % v)
  if (self.min is not None and v < self.min) or (self.max is not None and v > self.max):
   raise ValidationError('Expecting an integer between %s and %s.' % ('anything' if self.min is None else self.min, 'anything' if self.max is None else self.max))

class String(Validator):
 def validate(self, option):
  """Checks that the value is a string."""
  if not isinstance(option.value, six.string_types):
   raise ValidationError('Expected a string.')

class RestrictedString(String):
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
  super(RestrictedString, self).validate(option)
  if (self.min is not None and len(v) < self.min) or (self.max is not None and len(v) > self.max):
   if self.min == self.max:
    suggest = 'exactly %s %s' % (self.min, self.pluralise(self.min, 'character'))
   else:
    if self.min is None:
     if self.max is None:
      suggest = 'any length' # Should never happen.
     else:
      suggest = 'up to %s %s' % (self.max, self.pluralise(self.max, 'character'))
    else:
     suggest = 'at least %s %s' % (self.min, self.pluralise(self.min, 'character'))
   raise ValidationError('Expected a string of %s.' % suggest)

class Float(Validator):
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

class Option(Validator): 
 def __init__(self, *options):
  """Store the list of possible options."""
  self.options = options
 
 def validate(self, option):
  """Check that option.value is in self.options."""
  if option.value not in self.options:
   raise ValidationError('%s is not in %s.' % (option.value, self.options))

class QuickValidator(Validator):
 """Quickly add a new validator."""
 def __init__(self, func):
  """
  The validate method will use func to check the data against.
  
  If it returns None, the data is assumed to be OK.
  
  Any other value will be turned into a ValidationError via str.
  """
  self.func = func
 
 def validate(self, option):
  res = self.func(option)
  if res is not None:
   raise ValidationError(str(res))
