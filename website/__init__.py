import io
import os
from flask import Flask, render_template, make_response, send_from_directory, abort, url_for
from flask import request_started

import itertools
import werkzeug
import yaml

app = Flask(__name__, static_folder='assets')
app.config.from_object('website.settings')
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True


from website.site import Site
site = Site(app)

import website.route
import website.filter

# load cached resources on each request if they are outdated
request_started.connect(site.load_menus, app)
