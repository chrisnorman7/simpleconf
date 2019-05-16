"""
simpleconf example.

This takes you through the process of creating a simpleconf object so you can
see how it should be done.
"""

import wx
from simpleconf2 import Section, Option, validators
from simpleconf2.dialogs.wx import SimpleConfWxPanel


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
        p = wx.Panel(self.splitter)  # self.right_panel
        s = wx.BoxSizer(wx.VERTICAL)
        self.load = wx.Button(p, label='&Load')
        self.load.Bind(wx.EVT_BUTTON, self.on_load)
        s.Add(self.load, 1, wx.GROW)
        self.save = wx.Button(p, label='&Save')
        self.save.Bind(wx.EVT_BUTTON, self.on_save)
        s.Add(self.save, 1, wx.GROW)
        p.SetSizerAndFit(s)
        self.right_panel = p
        self.splitter.SplitHorizontally(self.left_panel, self.right_panel)
        self.root = self.tree.AddRoot('Options')
        self.tree.SetItemHasChildren(self.root)
        for section in config.children:
            self.add_section(self.root, section)

    def add_section(self, parent, section):
        """Recursively add a section to self.tree."""
        item = self.tree.AppendItem(parent, section.title)
        if section.sections:
            self.tree.SetItemHasChildren(item)
        self.tree.SetItemData(item, section)
        for subsection in section.children:
            self.add_section(item, subsection)

    def on_change(self, event):
        item = event.GetItem()
        section = self.tree.GetItemData(item)
        old = self.splitter.GetWindow2()
        if section is None:
            new = self.right_panel
            new.Show(True)
            if old is new:
                return  # Nothing to do.
        else:
            new = SimpleConfWxPanel(section, self.splitter)
        self.splitter.ReplaceWindow(old, new)
        if old is self.right_panel:
            old.Hide()
        else:
            old.Destroy()

    def on_load(self, event):
        """Load configuration from disk."""
        config.load()

    def on_save(self, event):
        """Save configuration to disk."""
        config.write()


# Now for showing the actual dialog:
if __name__ == '__main__':
    a = wx.App(False)
    f = ConfigFrame()
    f.Show(True)
    a.MainLoop()
