import os

_basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = True

# Setup default locations for website data
_basedir = os.path.abspath(os.path.dirname(__file__))

STATIC_ROOT = os.path.join(_basedir, 'assets')
CONTENT_ROOT = os.path.join(_basedir, 'content')
CONFIG_ROOT = os.path.join(_basedir, 'config')

CONTENT_EXTENSION = '.yml'

FREEZER_DESTINATION = '../public'

DOMAIN = 'froid.bluehut.ca'
SITE_NAME = 'Froid Documentation Site'
DISQUS_SITE_NAME = ''

del os
