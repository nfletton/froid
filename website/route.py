import os

from flask import render_template, make_response, send_from_directory, abort, url_for
from website import app, site
from website.util import sort_by

@app.route('/')
def index():
    return render_template('index.html', page=site.page('index.yml'), site=site)


@app.route('/<path:url_path>.html')
def content(url_path):
    doc_path = os.path.join(app.root_path, 'content', url_path + '.yml')
    if os.path.isfile(doc_path):
        page = site.page(url_path + site.suffix)
        return render_template(page.meta['template'] + '.html', page=page, site=site)
    else:
        abort(404)
