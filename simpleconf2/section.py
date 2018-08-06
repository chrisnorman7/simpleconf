"""
This file contains the section class.
"""

from inspect import isclass
from json import loads, dumps
from attr import attrs
from .option import Option
from .exceptions import NoSectionError, NoOptionError, NoFileError, \
     ValidationError
from .filename import Filename


@attrs(init=False)
class Section:
    """
    A configuration section.

    Sections can be stacked to sort configuration options more intuatively.

    Loader and dumper are responsible for loading and dumping data. They
    default to json.loads and json.dumps respectively.

    loader should expect a string (and any optional arguments passed to
    Section.load) and return a dictionary.
    dumper should expect a dictionary (and any optional arguments passed to
    Section.dump) and return a string.
    """

    option_order = []
    filename = None
    parent = None
    title = 'Untitled Section'
    visible = True  # Use this to hide system configuration.

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

    def __init__(
        self, filename=None, parent=None, title=None, load=True, **kwargs
    ):
        """
        Initialise the section.

        filename - Where this section should load it's data from (if anywhere).
        You should either provide an instance of Filename or a string (which
        will be passed to Filename).
        Note: By default self.write and self.load run self.fix_filename before
        they run to ensure that self.filename is an instance of Filename. If
        you do not wish to use the Filename class you must either create your
        own load and write methods, or else override fix_filename to use a
        class better suited to your needs.
        Just ensure this new class has read and write methods as well as a name
        attribute.
        parent - The parent of this section.
        title - The friendly name of this section (will be used as the window
        title).
        load - If True, load when all sections and options have been added.
        kwargs - The initial options and values.
        """
        if filename is not None:
            self.filename = filename
        if parent is not None:
            self.parent = parent
        if title is not None:
            self.title = title
        self._sections = {}  # a dictionary of name: section pairs.
        self._options = {}
        if self.option_order:
            option_order = self.option_order
        else:  # The user didn't specify an order. Infer.
            option_order = []
        for name in dir(self):
            if name.startswith('_'):
                continue  # Don't want to mess with __class__.
            thing = getattr(self, name)
            if isinstance(thing, Option):
                self.add_option(name, thing)
                if not self.option_order:
                    option_order.append(thing)
            elif isclass(thing) and issubclass(thing, Section):
                thing = thing(parent=self)
                self.add_section(name, thing)
        self.option_order = option_order
        if load:
            try:
                self.load()
            except NoFileError:
                pass  # There is no filename.

    def loader(self, *args, **kwargs):
        """Should expect the string resulting from reading self.filename, and
        return a dictionary. By default we use json.dumps, but you can override
        this method to use any loader or dumper you want."""
        return loads(*args, **kwargs)

    def dumper(self, *args, **kwargs):
        """Should expect a dictionary as returned by self.as_dictionary and
        return a string suitable for writing to self.filename. By default we
        use json.dumps, but you can override this method to use any system you
        like."""
        return dumps(*args, **kwargs)

    def add_option(self, name, thing, include=False):
        """Add thing as an option named name of this section. If include is
        True, add thing to option_order as well."""
        if not isinstance(thing, Option):
            raise TypeError(
                'Option %s (%r) is not of type Option.' % (
                    name, thing
                )
            )
        if hasattr(
            self, name
        ) and not (
            getattr(
                self, name
            ) is thing or (
                isclass(
                    getattr(
                        self, name
                    )
                ) and isinstance(
                    thing, getattr(
                        self, name
                    )
                )
            )
        ):
            raise AttributeError(
                'There is already an attribute named %s on section %r.' % (
                    name, self
                )
            )
        thing.section = self
        thing.name = name
        self._options[name] = thing
        setattr(self, name, thing)
        if include:
            self.option_order.append(thing)

    def add_section(self, name, thing):
        """Add thing as a subsection named name of this section."""
        if not isinstance(thing, Section):
            raise TypeError(
                'Section %s (%r) is not of type Section.' % (
                    name, thing
                )
            )
        if hasattr(
            self, name
        ) and not (
            getattr(
                self, name
            ) is thing or (
                isclass(
                    getattr(
                        self, name
                    )
                ) and isinstance(
                    thing, getattr(
                        self, name
                    )
                )
            )
        ):
            raise AttributeError(
                'There is already an attribute named %s on section %r.' % (
                    name, self
                )
            )
        self._sections[name] = thing
        setattr(self, name, thing)

    def fix_filename(self):
        """Ensures self.filename is an instance of Filename."""
        if not isinstance(self.filename, Filename):
            self.filename = Filename(self.filename)

    def load(self, *args, **kwargs):
        """Load configuration from disk."""
        self.fix_filename()
        if self.filename.name is None:
            raise NoFileError()  # Don't try and load anything.
        if self.filename.exists():
            data = self.filename.read()
        else:
            return  # Nothing to do.
        d = self.loader(data, *args, **kwargs)
        self.update(d)

    def update(
        self, data, ignore_missing_sections=True, ignore_missing_options=True
    ):
        """Update self from data. If ignore_missing_* evaluates to True don't
        raise an error when missing sections or options are found."""
        assert isinstance(data, dict), 'Data must be a dictionary.'
        for key, value in data.get('sections', {}).items():
            if key in self.sections:
                self._sections[key].update(
                    value, ignore_missing_sections=ignore_missing_sections,
                    ignore_missing_options=ignore_missing_options
                )
            else:
                if not ignore_missing_sections:
                    raise NoSectionError((key, self))
        for key, value in data.get('options', {}).items():
            try:
                self[key] = value
            except NoOptionError as e:
                if not ignore_missing_options:
                    raise e

    def restore(self, recurse=True):
        """Restore this section to defaults. If recursive evaluates to True,
        restore all children."""
        for o in self._options.values():
            o.restore()
        if recurse:
            for s in self.children:
                s.restore(True)

    def as_dictionary(self, full=False):
        """Return this section as a dictionary If full evaluates to True,
        dump everything, not just anything that has changed."""
        sections = {}
        options = {}
        for name, section in self._sections.items():
            data = section.as_dictionary()
            if data or full:
                sections[name] = data
        for name, option in self._options.items():
            if option.value != option.default or full:
                options[name] = option.value
        stuff = {}
        if sections:
            stuff['sections'] = sections
        if options:
            stuff['options'] = options
        return stuff

    def write(self, *args, **kwargs):
        """Write this section to disk if filename is provided. Pass all args
        and kwargs to self.dumper."""
        self.fix_filename()
        if self.filename.name is None:
            raise NoFileError()
        data = self.dumper(self.as_dictionary(), *args, **kwargs)
        self.filename.write(data)

    def get(self, option, default=None):
        """Get a config option."""
        try:
            return self[option]
        except NoOptionError:
            return default

    def validate(self):
        """Return a dictionary of name: reason pairs yielded from validating
        every option on this section. Successfully-validated options will be
        left out so an empty dictionary can be counted as a successful
        validation."""
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
