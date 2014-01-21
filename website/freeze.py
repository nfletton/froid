import os

from website import app
from flask.ext.frozen import Freezer

freezer = Freezer(app)


@freezer.register_generator
def raw_files():
    """
    Scan the content directory and register all none YAML files.
    """
    content_root = os.path.join(app.root_path, 'content')
    # site.log('NOTICE', 'Freeze non-YAML files in ' + content_root)
    for dirpath, dirnames, filenames in os.walk(content_root):
        for filename in filenames:
            if os.path.splitext(filename)[1] != '.yml':
                file_path = os.path.join(os.path.relpath(dirpath, content_root),
                                         filename)
                yield {'url_path': file_path}


@freezer.register_generator
def page():
    # freeze unreferenced pages
    for file in app.config['UNREFERENCED_FILES']:
        yield {'url_path': file}
