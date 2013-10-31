import io
import os
from flask import Flask, render_template, make_response, send_from_directory, abort, url_for
from flask import request_started, request_tearing_down

import itertools
import werkzeug
import yaml


if 'TEST_DATA_ROOT' in os.environ:
    TEST_DATA_ROOT = os.environ['TEST_DATA_ROOT']
    STATIC_FOLDER = os.path.join(u'..', TEST_DATA_ROOT, u'assets')
    TEMPLATE_FOLDER = os.path.join(u'..', TEST_DATA_ROOT, u'templates')
    app = Flask(__name__,
                static_folder=os.path.join(u'..', TEST_DATA_ROOT, u'assets'),
                template_folder=os.path.join(u'..', TEST_DATA_ROOT, u'templates')
                )
else:
    app = Flask(__name__, static_folder='assets')

app.config.from_pyfile('settings.py')

app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True


from website.site import Site
site = Site()

import website.route
import website.filter

# load cached resources on each request if they are outdated
request_started.connect(site.load_menus, app)

# flush request error messages after request
request_tearing_down.connect(site.flush_errors, app)
