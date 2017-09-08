"""Provides the Filename class. This should be used when setting
Section.filename."""

import os.path
from attr import attrs, attrib, Factory


@attrs
class Filename:
    """
    A filename instance.

    name
    The name of the file (or a file-like object).
    read_flags
    The flags to use when opening the file for reading.
    write_flags
    The flags used when opening the file for writing.
    file_like
    A boolean value specifying whether or not name is a file-like object.
    """

    name = attrib()
    read_flags = attrib(default=Factory(lambda: 'r'))
    write_flags = attrib(default=Factory(lambda: 'w'))
    file_like = attrib(default=Factory(bool))

    def read(self):
        """Load the file and return its contents."""
        if self.file_like:
            data = self.name.read()
            self.name.seek(0)  # We might need to read again.
            return data
        else:
            with open(self.name, self.read_flags) as f:
                return f.read()

    def write(self, data):
        """Write data to this file. You should provide data in the form
        expected by the resulting file-like object."""
        if self.file_like:
            return self.name.write(data)
        else:
            with open(self.name, self.write_flags) as f:
                return f.write(data)

    def exists(self):
        """Returns True if sef.filename is a file or self.file_like is True,
        False otherwise."""
        return self.file_like or (
            self.name is not None and os.path.isfile(self.name)
        )
