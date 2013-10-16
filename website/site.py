import io
import os

import itertools

from website.menu import Menu
from website.page import Page
from website.util import log


class Site(object):
    suffix = '.yml'

    def __init__(self, app):
        self.config = dict()
        self.config['content_root'] = os.path.join(app.root_path, u'content')
        self.config['image_root'] = os.path.join(app.root_path, u'assets', u'images')
        self.config['config_root'] = os.path.join(app.root_path, u'config')
        self.config['content_types'] = ['.yml']
        self._page_cache = {}
        self._url_to_page_index = {}
        self._menu_cache = {}
        self._context_cache = {}
        self._image_cache = {}

    def page(self, content_path):
        """
        Load a content file from its content path
        """
        absolute_pathname = os.path.abspath(os.path.join(self.config['content_root'], content_path))
        mtime = os.path.getmtime(absolute_pathname)
        page, old_mtime = self._page_cache.get(content_path, (None, None))
        if not page or mtime != old_mtime:
            with io.open(absolute_pathname, mode='r') as fd:
                log('NOTICE', 'Loading page %s' % absolute_pathname)
                head = ''.join(itertools.takewhile(unicode.strip, fd))
                body = fd.read()
            page = Page(head, body, content_path, mtime, self)
            self._page_cache[content_path] = (page, mtime)
            self._url_to_page_index[page.url()] = page
        return page

    def load_menus(self, sender, **extra):
        for name in os.listdir(self.config['config_root']):
            if name.endswith(self.suffix) and name.startswith('nav-'):
                filename = os.path.join(self.config['config_root'], name)
                mtime = os.path.getmtime(filename)
                menu_uid = os.path.splitext(os.path.basename(filename))[0]
                cached_menu, old_mtime = self._menu_cache.get(menu_uid, (None, None))
                if not cached_menu or mtime != old_mtime:
                    with io.open(filename, mode='r') as fd:
                        log('NOTICE', 'Loading menu %s' % filename)
                        new_menu = Menu(self)
                        new_menu.load(fd.read())
                        self._menu_cache[menu_uid] = (new_menu, mtime)
