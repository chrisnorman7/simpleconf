"""
simpleconf example.

This takes you through the process of creating a simpleconf object so you can see how it should be done.
"""

import wx
from simpleconf import Section, Option, validators

class Config(Section):
 """Top-level config."""
 filename = 'config.json'
 class login(Section):
  """Login configuration."""
  title = 'Login Configuration'
  username = Option('test', title = '&Username')
  password = Option('password123', title = '&Password', control = lambda option, window: wx.TextCtrl(window.panel, style = wx.TE_PASSWORD))
  remember = Option(True, title = '&Remember Credentials', validator = validators.Boolean)
  option_order = [username, password, remember]
 
 class interface(Section):
  """Interface configuration."""
  title = 'Interface Configuration'
  width = Option(1024, title = 'Screen &Width', validator = validators.Integer(min = 0))
  height = Option(768, title = 'Screen &Height', validator = validators.Integer(min = 0))
  opacity = Option(1.0, title = 'Screen &Opacity', validator = validators.Float(min = 0.0, max = 5.0))
  option_order = [width, height, opacity]

config = Config()

from wx.lib.sized_controls import SizedFrame
from simpleconf.dialogs.wx import SimpleConfWxDialog as WXDLG

class ConfigFrame(SizedFrame):
 """This should show buttons to load a panel for every configuration section."""
 def __init__(self):
  super(ConfigFrame, self).__init__(None, title = 'Simpleconf Example')
  p = self.GetContentsPane()
  p.SetSizerType('form')
  for s in config.sections:
   section = getattr(config, s)
   wx.Button(p, label = '&%s' % section.title).Bind(wx.EVT_BUTTON, lambda event, section = section: WXDLG(section).Show(True))

# Now for showing the actual dialog:
if __name__ == '__main__':
 a = wx.App(False)
 f = ConfigFrame()
 f.Show(True)
 a.MainLoop()
