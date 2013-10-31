import io
import os

import itertools

from website import app
from website.menu import Menu
from website.page import Page


class Site(object):

    def __init__(self):
        self._page_cache = {}
        self._url_to_page_index = {}
        self._menu_cache = {}
        self._context_cache = {}
        self._image_cache = {}
        self._error_log = []

    def page(self, content_path):
        """
        Load a content file from its content path
        """
        absolute_pathname = os.path.abspath(os.path.join(app.config['CONTENT_ROOT'], content_path))
        mtime = os.path.getmtime(absolute_pathname)
        page, old_mtime = self._page_cache.get(content_path, (None, None))
        if not page or mtime != old_mtime:
            with io.open(absolute_pathname, mode='r') as fd:
                self.log('NOTICE', 'Loading page %s' % absolute_pathname)
                head = ''.join(itertools.takewhile(unicode.strip, fd))
                body = fd.read()
            page = Page(head, body, content_path, mtime, self)
            self._page_cache[content_path] = (page, mtime)
            self._url_to_page_index[page.url()] = page
        return page

    def load_menus(self, sender, **extra):
        for name in os.listdir(app.config['CONFIG_ROOT']):
            if name.endswith(app.config['CONTENT_EXTENSION']) and name.startswith('nav-'):
                filename = os.path.join(app.config['CONFIG_ROOT'], name)
                mtime = os.path.getmtime(filename)
                menu_uid = os.path.splitext(os.path.basename(filename))[0]
                cached_menu, old_mtime = self._menu_cache.get(menu_uid, (None, None))
                if not cached_menu or mtime != old_mtime:
                    with io.open(filename, mode='r') as fd:
                        self.log('NOTICE', 'Loading menu %s' % filename)
                        new_menu = Menu(self)
                        new_menu.load(fd.read())
                        self._menu_cache[menu_uid] = (new_menu, mtime)

    def menu(self, menu_uid):
        return self._menu_cache[menu_uid][0].root()

    def page_active_trail(self, url):
        """
        Generate a set of URL's that are parents (i.e. part of the active menu trail)
        relative to the given page URL.
        """
        # Add the page URL to the trail
        trail = {url}
        # Add the URLs of any page that is referenced from an ancestor
        # menu item in any menu
        for menu_id, menu in self._menu_cache.items():
            trail.update(menu[0].parent_page_urls(url))
            # Add any URLs from hard coded rules
        # trail.update(self.custom_trail(url))
        return trail

    def flush_errors(self, sender, **extra):
        if self._error_log:
            print "\n".join(self._error_log)
            self._error_log = []

    def log(self, mess_type, message):
        log_message = '%s: %s' % (mess_type, message)
        if mess_type == 'NOTICE':
            print(log_message)
        else:
            # save error to be flushed at the end of request
            self._error_log.append(log_message)
