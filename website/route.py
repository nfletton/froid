import os

from flask import render_template, abort, send_from_directory
from website import app, site

@app.route('/')
def index():
    return render_template('index.html', page=site.page('index.yml'), site=site)


@app.route('/<path:url_path>.html')
def content(url_path):
    doc_path = os.path.join(app.config['CONTENT_ROOT'], url_path + '.yml')
    if os.path.isfile(doc_path):
        page = site.page(url_path + app.config['CONTENT_EXTENSION'])
        return render_template(page.meta['template'] + '.html', page=page, site=site)
    else:
        abort(404)


@app.route('/<path:url_path>')
def raw_files(url_path):
    """
    A catch all route to match against raw files that may exist in the content folder
    that need to be delivered as is. e.g. robots.txt, .htaccess, PHP files
    """
    doc_path = os.path.join(app.config['CONTENT_ROOT'], url_path)
    if os.path.isfile(doc_path):
        split_path = os.path.split(os.path.abspath(doc_path))
        return send_from_directory(split_path[0], split_path[1])
    else:
        abort(404)
