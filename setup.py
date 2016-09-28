from setuptools import setup

from simpleconf import __version__

setup(
 name = 'simpleconf',
 version = __version__,
 description = 'The last configuration manager I will ever write (hopefully).',
 url = 'http://github.com/chrisnorman7/simpleconf.git',
 author = 'Chris Norman',
 author_email = 'chris.norman2@googlemail.com',
 license = 'MPL',
 packages = ['simpleconf', 'simpleconf.dialogs'],
 zip_safe = False,
 keywords = ['configuration', 'config', 'saving'],
 long_description_markdown_filename = 'README.md',
 setup_requires = ['setuptools-markdown'],
 install_requires = ['six'], 
)
