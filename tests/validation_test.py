"""Test validators."""

from simpleconf import validators, Option
from inspect import isclass
from warnings import warn


def test_validators():
    """Test all validators using their test methods."""
    o = Option('')
    for x in dir(validators):
        validator = getattr(validators, x)
        if isclass(
            validator
        ) and issubclass(
            validator, validators.Validator
        ) and validator is not validators.Validator:
            validator = validator()
            o.validator = validator
            try:
                validator.test(o)
            except Exception as e:
                warn('Exception found in method test of %r.' % validator)
                raise
