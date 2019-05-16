"""
This file contains the wx dialog and Panel for simpleconf.

Any future dialogs will be kept in this directory for convenience.
"""

import wx
from wx.lib.sized_controls import SizedPanel
from wx.lib.agw.floatspin import FloatSpin
from wx.lib.intctrl import IntCtrl
from ..validators import ValidationError


class SimpleConfWxPanel(SizedPanel):
    """A panel for displaying simpleconf sections."""

    def __init__(self, section, *args, **kwargs):
        """Construct a frame from the provided section."""
        self.control_types = {}
        self.control_types[bool] = lambda option, window: wx.CheckBox(window)
        self.control_types[int] = lambda option, window: IntCtrl(window)
        self.control_types[str] = lambda option, window: wx.TextCtrl(window)
        self.control_types[
            float
        ] = lambda option, window: FloatSpin(window, digits=2)
        self.section = section
        # name:control pairs for all the controls on this form:
        self.controls = {}
        super(SimpleConfWxPanel, self).__init__(*args, **kwargs)
        self.SetSizerType('Form')
        for option in section.option_order:
            wx.StaticText(self, label=option.get_title())
            if option.control is None:
                for type, control in self.control_types.items():
                    if isinstance(option.value, type):
                        c = control(option, self)
                        break
                else:
                    raise TypeError(
                        'No appropriate control found for option %s with \
                        value %s.' % (
                            option.name, option.value
                        )
                    )
            else:
                c = option.control(option, self)
            if isinstance(c, (wx.CheckBox, wx.Button)):
                c.SetLabel(option.get_title())
            c.SetValue(option.value)
            self.controls[option.name] = c
        self.ok = wx.Button(self, label='&OK')
        self.ok.SetDefault()
        self.ok.Bind(wx.EVT_BUTTON, self.on_ok)
        self.cancel = wx.Button(self, label='&Cancel')

    def on_error(self, message, title='Error', style=wx.ICON_EXCLAMATION):
        """Display an error message."""
        wx.MessageBox(message, title, style)

    def on_ok(self, event):
        """The OK button was pressed."""
        for option in self.section.option_order:
            control = self.controls[option.name]
            option.set(control.GetValue())
            try:
                option.check()
            except ValidationError as e:
                self.on_error(e.message)
                control.SetFocus()
                return False
        # Signal to any overriding methods that we exited correctly:
        return True


class SimpleConfWxParentFriendlyPanel(SimpleConfWxPanel):
    """Overrides on_ok to call self.parent.on_ok with the result of self.on_ok.
    Also binds EVT_BUTTON to self.cancel to call self.parent.on_cancel."""

    def __init__(self, section, parent, *args, **kwargs):
        super().__init__(
            section, parent, *args, **kwargs
        )
        self.parent = parent
        self.cancel.Bind(
            wx.EVT_BUTTON,
            lambda event: self.parent.on_cancel(event)
        )

    def on_ok(self, event):
        """Close the window - cancel button was pressed."""
        self.parent.on_ok(
            super(SimpleConfWxParentFriendlyPanel, self).on_ok(event)
        )


class SimpleConfWxDialog(wx.Frame):
    """A frame to show a configuration section."""

    def __init__(self, section, *args, **kwargs):
        kwargs.setdefault('title', section.title)
        super(SimpleConfWxDialog, self).__init__(*args, **kwargs)
        self.panel = SimpleConfWxParentFriendlyPanel(section, self)

    def on_ok(self, result):
        """Close the window if result evaluates to True."""
        if result:
            self.Close(True)

    def on_cancel(self, event):
        return self.on_ok(True)  # Close the window.
