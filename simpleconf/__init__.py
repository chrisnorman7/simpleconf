"""
simpleconf

A configuration manager written from the ground up using Python 3.

This module aims to remove all the shortcomings of confmanager (https://github.com/chrisnorman7/confmanager.git), and configobj-dialog (https://github.com/chrisnorman7/configobj_dialog).

It will become the defacto configuration manager used by all my programs in the future.
"""

from .section import Section
from .option import Option
from . import exceptions, validators

__version__ = '0.1.1'

__all__ = [
 'Section',
 'Option',
 'exceptions',
 'validators',
 '__version__'
]
