"""
Froid routes
"""

import os
import inspect

from flask import render_template, abort, send_from_directory, url_for
from website import app, site


@app.route('/')
def index():
    """
    Root for website root folder
    """
    return render_template('index.html', page=site.page('/index.html'), site=site)


@app.route('/<path:url_path>.html')
def content(url_path):
    """
    Default route for html files.
    """
    url = url_for('content', url_path=url_path)
    page = site.page(url)
    return render_template(page.meta['template'] + '.html',
                           page=page,
                           site=site)


@app.route('/<path:url_path>')
def raw_files(url_path):
    """
    Catch all route to match against raw files that may exist in the content
    folder that need to be delivered as is. e.g. robots.txt, .htaccess, PHP
    files, ...
    """
    doc_path = os.path.join(app.config['CONTENT_ROOT'], url_path)
    if os.path.isfile(doc_path):
        split_path = os.path.split(os.path.abspath(doc_path))
        return send_from_directory(split_path[0], split_path[1])
    else:
        abort(404)


@app.errorhandler(404)
def page_not_found(_):
    """
    404 page handler
    """
    page = site.page('/404.html')
    return render_template(page.meta['template'] + '.html',
                           page=page, site=site), 404
