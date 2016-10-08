"""
All exception classes.
"""

class SimpleConfError(Exception):
 """The base from which all simpleconf errors are derived."""
 def __init__(self, message = None):
  """Initialise the exception."""
  self.message = self.__doc__ if message is None else message
  super(SimpleConfError, self).__init__(self.message)
 
 def __str__(self):
  """Print this as a string."""
  return self.message

class ValidationError(SimpleConfError):
 """Validation error."""

class DataMissingError(SimpleConfError):
 """Missing data."""

class NoSectionError(DataMissingError):
 """No section named %s on section %s."""
 def __init__(self, option, section):
  return super(NoSectionError, self).__init__(self.__doc__ % (option, section))

class NoOptionError(DataMissingError):
 """No option named %s on section %s."""
 def __init__(self, option, section):
  return super(NoOptionError, self).__init__(self.__doc__ % (option, section))

class NoFileError(SimpleConfError):
 """No file was provided."""

