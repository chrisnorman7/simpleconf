"""
This module contains the Option class. This class should be used to define options.
"""

from inspect import isclass
from .validators import String

class Option(object):
 """An option within a section."""
 def __init__(self, default, validator = String, title = None, control = None):
  """
  Initialise the option.
  
  default - The default value for this option.
  validator - The validator which the option will be checked against.
  title - The friendly name for this option which will show up in any GUI.
  control - The control which should be used to set the value of this control.
  """
  self.section = None # The section this option is a member of.
  self.name = None # The name of this option. Set when the section is initialised.
  if isclass(validator):
   self.validator = validator()
  else:
   self.validator = validator
  self.default = default
  self.value = default # The user-defined value for this option.
  self.title = title
  self.control = control
 
 def check(self):
  return self.validator.validate(self)
 
 def restore(self):
  """Return value to default."""
  self.value = self.default
 
 def get_title(self):
  """Return the title of this option."""
  return self.name if self.title is None else self.title
 
 def __str__(self):
  return '%s: %s' % (self.name, self.value)
