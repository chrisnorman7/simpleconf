"""
This module contains the Option class. This class should be used to define
options.
"""

from inspect import isclass
from attr import attrs, attrib, Factory
from .validators import String


@attrs
class Option:
    """
    An option within a section.

    Initialise the option.

    default - The default value for this option.
    validator - The validator which the option will be checked against.
    title - The friendly name for this option which will show up in any GUI.
    control - The control which should be used to set the value of this control
    (called as control(option, window).
    """

    default = attrib()
    value = attrib(default=Factory(String))
    validator = attrib(default=Factory(String))
    title = attrib(default=Factory(lambda: None))
    control = attrib(default=Factory(lambda: None))
    section = attrib(default=Factory(lambda: None), init=False)
    name = attrib(default=Factory(lambda: None), init=False)

    def __attrs_post_init__(self):
        if isclass(self.validator):
            self.validator = self.validator()
        self.set(self.default)

    def set(self, value):
        """Set self.value = value."""
        self.value = value

    def check(self):
        """Validate the value of this option."""
        return self.validator.validate(self)

    def restore(self):
        """Return value to default."""
        self.value = self.default

    def get_title(self):
        """Return the title of this option."""
        return self.name if self.title is None else self.title

    def __str__(self):
        return self.get_title()
