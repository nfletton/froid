"""
Froid routes
"""
import os

from flask import abort, make_response
from flask import render_template, send_from_directory, url_for

from website import app, site, util


@app.route('/')
def index():
    """
    Root for website root folder
    """
    return render_template('index.html', page=site.page_from_url('/index.html'), site=site)


@app.route('/sitemap.xml')
def sitemap_feed():
    response = make_response(
        render_template('sitemap.xml',
                        pages=util.sort_by('published', site.pages(), True)))
    response.headers['Content-Type'] = 'application/xml; charset=utf-8'
    return response


@app.route('/atom.xml')
def atom_feed():
    pages = util.sort_by('published', site.pages_by_destination('atom_feed', 'date', 30), True)
    response = make_response(render_template('atom.xml', pages=pages))
    response.headers['Content-Type'] = 'application/xml; charset=utf-8'
    return response


@app.route('/<path:url_path>.html')
def page(url_path):
    """
    Default route for basic content files.
    """
    url = url_for('page', url_path=url_path)
    page = site.page_from_url(url)
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
    page = site.page_from_url('/404.html')
    return render_template(page.meta['template'] + '.html',
                           page=page, site=site), 404
