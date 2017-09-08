"""Test sections."""

import os
import os.path
from pytest import raises
from simpleconf import Section, Option, validators, exceptions

user_name = 'Joseph Test'
dog_name = 'Jimmy'


class User(Section):
    name = Option(
        'test', title='&Name', validator=validators.String()
    )
    password = Option(
        'password123', title='&Password',
        validator=validators.RestrictedString(min=8)
    )
    age = Option(
        18, title='&Age', validator=validators.Integer(min=16, max=95)
    )
    testing = Option(
        True, title='&Testing With Pytest', validator=validators.Boolean()
    )
    height = Option(
        1.5, title='&Height (In Metres)', validator=validators.Float(
            min=0.5, max=2.5
        )
    )

    class dog(Section):  # Sub section.
        name = Option('Fido', title='&IName', validator=validators.String)
        colour = Option(
            'black', title='Dog &Colour', validator=validators.Option(
                'black', 'grey', 'golden', 'ugly'
            )
        )


user = User()


def test_setters():
    """Test setting several options."""
    for name in ['name', 'password', 'age', 'testing', 'height']:
        assert name in user.options
        option = getattr(user, name)
        assert option.section is user
        assert user[name] == option.value
    assert user.get('name', 'testing') is user['name']
    assert user.get('asdf', 'testing') == 'testing'
    with raises(exceptions.NoOptionError):
        user['not really an option.']
    user['name'] = user_name
    assert user.name.value is user_name


def test_attributes():
    """Test the attributes of the section."""
    assert user.parent is None
    assert user.dog in user.children
    assert len(user.children) == 1
    assert user.dog.parent is user


def test_dump():
    """Test reading and writing dumps."""
    j = user.as_dictionary(full=True)
    assert isinstance(j, dict)
    assert len(list(j.keys())) == 2
    assert 'options' in j
    assert 'sections' in j
    assert 'name' in j['options']
    fname = 'test.json'
    user.filename = fname
    if os.path.isfile(fname):
        os.remove(fname)
    user.dog['name'] = dog_name
    user['name'] = user_name
    user.write(indent=1)
    user.restore()
    assert user['name'] is user.name.default
    assert user.dog['name'] is user.dog.name.default
    user.load()
    assert user['name'] == user_name
    assert user.dog['name'] == dog_name
    assert os.path.isfile(fname)
    os.remove(fname)


def test_validate():
    """Test validating the object."""
    assert user.validate() == {}
    user['name'] = 5
    assert 'name' in user.validate()


def test___str__():
    name = 'Testing 1, 2, 3.'
    c = Section(title=name)
    assert c.title == name


def test_add_section():
    c = Section()
    s = Section()
    c.add_section('test', s)
    assert c.test is s
    with raises(TypeError):
        c.add_section('testing', 'Not a Section.')
    with raises(AttributeError):  # Already an attribute named 'test'.
        c.add_section('test', Section())


def test_add_option():
    c = Section()
    o = Option('default')
    c.add_option('test', o)
    assert o not in c.option_order
    assert c.test is o
    assert c['test'] == o.value
    with raises(TypeError):
        c.add_option('testing', 'Not an Option.')
    with raises(AttributeError):
        c.add_option('test', Option('Already got an attribute named test.'))
    o = Option('')
    c.add_option('include', o, include=True)
    assert o in c.option_order
    assert c.include is o
