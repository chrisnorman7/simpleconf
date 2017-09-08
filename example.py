"""
simpleconf example.

This takes you through the process of creating a simpleconf object so you can
see how it should be done.
"""

import wx
from simpleconf import Section, Option, validators
from simpleconf.dialogs.wx import SimpleConfWxPanel


class Config(Section):
    """Top-level config."""
    filename = 'config.json'

    class login(Section):
        """Login configuration."""
        title = 'Login Configuration'
        username = Option('test', title='&Username')
        password = Option(
            'password123', title='&Password',
            control=lambda option, window: wx.TextCtrl(
                window, style=wx.TE_PASSWORD
            ),
            validator=validators.RestrictedString(min=5)
        )
        remember = Option(
            True, title='&Remember Credentials', validator=validators.Boolean)
        option_order = [username, password, remember]

    class interface(Section):
        """Interface configuration."""
        title = 'Interface Configuration'
        width = Option(
            1024, title='Screen &Width', validator=validators.Integer(min=0)
        )
        height = Option(
            768, title='Screen &Height', validator=validators.Integer(min=0)
        )
        opacity = Option(
            1.0, title='Screen &Opacity',
            validator=validators.Float(min=0.0, max=5.0)
        )
        option_order = [width, height, opacity]


config = Config()


class ConfigFrame(wx.Frame):
    """Create a tree view."""
    def __init__(self):
        super(ConfigFrame, self).__init__(None, title='Simpleconf Example')
        self.splitter = wx.SplitterWindow(self)
        self.left_panel = wx.Panel(self.splitter)
        left_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.tree = wx.TreeCtrl(self.left_panel)
        self.Bind(wx.EVT_TREE_SEL_CHANGING, self.on_change)
        left_sizer.Add(
            wx.StaticText(self.left_panel, label='&Sections'),
            0, wx.GROW
        )
        left_sizer.Add(self.tree, 1, wx.GROW)
        self.left_panel.SetSizerAndFit(left_sizer)
        self.splitter.SplitHorizontally(
            self.left_panel, self.make_right_panel()
        )
        self.root = self.tree.AddRoot('Options')
        self.tree.SetItemHasChildren(self.root)
        for s in config.sections:
            section = getattr(config, s)
            self.add_section(self.root, section)

    def make_right_panel(self):
        """Create a panel for the right hand side of the screen."""
        p = wx.Panel(self.splitter)
        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(
            wx.StaticText(
                p,
                label='Select a configuration section to view the options'
            ),
            0, wx.GROW
        )
        return p

    def add_section(self, parent, section):
        """Recursively add a section to self.tree."""
        item = self.tree.AppendItem(parent, section.title)
        if section.sections:
            self.tree.SetItemHasChildren(item)
        self.tree.SetItemData(item, section)
        for name in section.sections:
            self.add_section(item, getattr(section, name))

    def on_change(self, event):
        item = event.GetItem()
        section = self.tree.GetItemData(item)
        old = self.splitter.GetWindow2()
        if section is None:
            new = self.make_right_panel()
        else:
            new = SimpleConfWxPanel(section, self.splitter)
        self.splitter.ReplaceWindow(old, new)
        old.Destroy()


# Now for showing the actual dialog:
if __name__ == '__main__':
    a = wx.App(False)
    f = ConfigFrame()
    f.Show(True)
    a.MainLoop()
