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
 
 def __init__(self, filename = None, parent = None, title = None, load = True, **kwargs):
  """
  Initialise the section.
  
  filename - Where this section should load it's data from (if anywhere).
  parent - The parent of this section.
  title - The friendly name of this section (will be used as the window title).
  load - If True, load when all sections and options have been added.
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
  else: # The user didn't specify an order. Infer.
   option_order = []
  for name in dir(self):
   if name.startswith('_'):
    continue # Don't want to mess with __class__.
   thing = getattr(self, name)
   if isinstance(thing, Option):
    self.add_option(name, thing)
    if not self.option_order:
     option_order.append(thing)
   elif isclass(thing) and issubclass(thing, Section):
    thing = thing(parent = self)
    self.add_section(name, thing)
  self.option_order = option_order
  if load:
   try:
    self.load()
   except NoFileError:
    pass # There is no filename.
 
 def add_option(self, name, thing):
  """Add thing as an option named name of this section."""
  if not isinstance(thing, Option):
   raise TypeError('Option %s (%r) is not of type Option.' % (name, thing))
  if hasattr(self, name) and not (getattr(self, name) is thing or (isclass(getattr(self, name)) and isinstance(thing, getattr(self, name)))):
   raise AttributeError('There is already an attribute named %s on section %r.' % (name, self))
  thing.section = self
  thing.name = name
  self._options[name] = thing
  setattr(self, name, thing)
 
 def add_section(self, name, thing):
  """Add thing as a subsection named name of this section."""
  if not isinstance(thing, Section):
   raise TypeError('Section %s (%r) is not of type Section.' % (name, thing))
  if hasattr(self, name) and not (getattr(self, name) is thing or (isclass(getattr(self, name)) and isinstance(thing, getattr(self, name)))):
   raise AttributeError('There is already an attribute named %s on section %r.' % (name, self))
  self._sections[name] = thing
  setattr(self, name, thing)
 
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
   if hasattr(self, option):
    o = getattr(self, option)
    if isinstance(o, Option):
     self._options
   raise NoOptionError(option, self)
 
 def __setitem__(self, option, value):
  """Set self[option] = value."""
  if option in self._options:
   self._options[option].set(value)
  else:
   raise NoOptionError(option, self)
 
 def __str__(self):
  return self.title
 
 def __repr__(self):
  return '{0.__class__.__name__}(title = {0.title}, sections = {0.sections}, options = {0.options}, option_order = {0.option_order})'.format(self)
