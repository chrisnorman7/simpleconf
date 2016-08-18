"""
This file contains the wx dialog for simpleconf.

Any future dialogs will be kept in this directory for convenience.
"""

import wx, six
from wx.lib.sized_controls import SizedFrame
from wx.lib.agw.floatspin import FloatSpin
from wx.lib.intctrl import IntCtrl
from wxgoodies.keys import add_accelerator

class SimpleConfWxDialog(SizedFrame):
 """A dialog for displaying simpleconf sections."""
 control_types = {
  bool: lambda option, window: wx.CheckBox(window.panel),
  int: lambda option, window: IntCtrl(window.panel),
  six.string_types: lambda window, option: wx.TextCtrl(window.panel),
  float: lambda option, window: FloatSpin(window.panel, digits = 2, name = option.get_title())
 }
 
 def __init__(self, section):
  """Construct a frame from the provided section."""
  self.section = section
  self.controls = {} # name:control pairs for all the controls on this form.
  super(SimpleConfWxDialog, self).__init__(None, title = section.title)
  add_accelerator(self, 'ESCAPE', lambda event: self.Close(True))
  self.panel = self.GetContentsPane()
  self.panel.SetSizerType('Form')
  for option in section.option_order:
   wx.StaticText(self.panel, label = option.get_title())
   if option.control is None:
    for type, control in self.control_types.items():
     if isinstance(option.value, type):
      c = control(option, self)
      break
    else:
     raise TypeError('No appropriate control found for option %s with value %s.' % (o, option.value))
   else:
    c = option.control(option, self)
   try:
    c.SetLabel(option.get_title())
   except AttributeError:
    pass # Not possible with this control.
   c.SetValue(option.value)
   self.controls[option.name] = c
  self.ok = wx.Button(self.panel, label = '&OK')
  self.ok.Bind(wx.EVT_BUTTON, self.on_ok)
  self.cancel = wx.Button(self.panel, label = '&Cancel')
  self.cancel.Bind(wx.EVT_BUTTON, lambda event: self.Close(True))
 
 def on_ok(self, event):
  """The OK button was pressed."""
  self.Close(True)
