"""
This file contains the section class.
"""

import os, os.path, six
from inspect import isclass
from json import loads, dump
from .option import Option
from .exceptions import NoSectionError, NoOptionError, NoFileError, ValidationError

class Section(object):
 """
 A configuration section.
 
 Sections can be stacked to sort configuration options more intuatively.
 """
 
 option_order = []
 filename = None
 parent = None
 title = 'Untitled Section'
 visible = True # Use this to hide system configuration.
 
 @property
 def sections(self):
  """Return the children of this section as a list of strings."""
  return list(self._sections.keys())
 
 @property
 def children(self):
  """Return the section objects that make up this section's children."""
  return list(self._sections.values())
 
 @property
 def options(self):
  """Return options as a list of names."""
  return list(self._options.keys())
 
 def __init__(self, filename = None, parent = None, title = None, **kwargs):
  """
  Initialise the section.
  
  filename - Where this section should load it's data from (if anywhere).
  parent - The parent of this section.
  title - The friendly name of this section (will be used as the window title).
  kwargs - The initial options and values.
  """
  if filename is not None:
   self.filename = filename
  if parent is not None:
   self.parent = parent
  if title is not None:
   self.title = title
  self._sections = {} # a dictionary of name: section pairs.
  self._options = {}
  if self.option_order:
   option_order = self.option_order
  else: # The user didn't specify an order.
   option_order = []
  for name in dir(self):
   if name.startswith('_'):
    continue # Don't want to mess with __class__.
   thing = getattr(self, name)
   if isinstance(thing, Option):
    thing.section = self
    thing.name = name
    self._options[name] = thing
    if not self.option_order:
     option_order.append(thing)
   elif isclass(thing) and issubclass(thing, Section):
    thing = thing(parent = self)
    self._sections[name] = thing
    setattr(self, name, thing)
  self.option_order = option_order
  try:
   self.load()
  except NoFileError:
   pass # There is no filename.
 
 def load(self):
  """Load configuration from disk."""
  if self.filename is None:
   raise NoFileError() # Don't try and load anything.
  if isinstance(self.filename, six.string_types):
   if os.path.isfile(self.filename):
    with open(self.filename, 'r') as f:
     json = f.read()
   else:
    json = '{}'
  else:
   json = self.filename.read()
  j = loads(json)
  self.update(j)
 
 def update(self, data, ignore_missing_sections = True, ignore_missing_options = True):
  """Update self from data. If ignore_missing_* evaluates to True don't raise an error when missing sections or options are found."""
  assert isinstance(data, dict), 'Data must be a dictionary.'
  for key, value in data.get('sections', {}).items():
   if key in self.sections:
    self._sections[key].update(value, ignore_missing_sections = ignore_missing_sections, ignore_missing_options = ignore_missing_options)
   else:
    if not ignore_missing_sections:
     raise NoSectionError((key, self))
  for key, value in data.get('options', {}).items():
   try:
    self[key] = value
   except NoOptionError as e:
    if not ignore_missing_options:
     raise e
 
 def restore(self, recurse = True):
  """Restore this section to defaults. If recursive evaluates to True, restore all children."""
  for o in self._options.values():
   o.restore()
  if recurse:
   for s in self.children:
    s.restore(True)
 
 def json(self, full = False):
  """Return this section as a dictionary If full evaluates to True, dump everything, not just anything that has changed."""
  sections = {}
  options = {}
  for name, section in self._sections.items():
   j = section.json()
   if j or full:
    sections[name] = j
  for name, option in self._options.items():
   if option.value != option.default or full:
    options[name] = option.value
  stuff = {}
  if sections:
   stuff['sections'] = sections
  if options:
   stuff['options'] = options
  return stuff
 
 def write(self, **kwargs):
  """Write this section to disk if filename is provided."""
  if self.filename is None:
   raise NoFileError()
  if isinstance(self.filename, six.string_types):
   with open(self.filename, 'w') as f:
    dump(self.json(), f, **kwargs)
  else:
   dump(self.json(), self.filename, **kwargs)
 
 def get(self, option, default = None):
  """Get a config option."""
  try:
   return self[option]
  except NoOptionError:
   return default
 
 def validate(self):
  """Return a dictionary of name: reason pairs yielded from validating every option on this section. Successfully-validated options will be left out so an empty dictionary can be counted as a successful validation."""
  errors = {}
  for name, option in self._options.items():
   try:
    option.check()
   except ValidationError as e:
    errors[name] = e.message
  return errors
 
 def __getitem__(self, option):
  """Get an option by subscripting."""
  if option in self._options:
   return self._options[option].value
  else:
   raise NoOptionError((option, self))
 
 def __setitem__(self, option, value):
  """Set self[option] = value."""
  if option in self._options:
   self._options[option].set(value)
  else:
   raise NoOptionError(option, self)
 
 def __str__(self):
  return 'Sections:%s\nOptions:%s' % (self.sections, self.options)
