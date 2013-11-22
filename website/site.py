import io
import os

import itertools
from flask import abort
import yaml

from website import app
from website.menu import Menu
from website.page import Page

class Site(object):

    def __init__(self):
        self._page_cache = {}
        self._menu_cache = {}
        self._context_cache = {}
        self._image_cache = {}
        self._error_log = []

    def page(self, url):
        """
        Load a content file from its content path
        """
        root_path = os.path.splitext(url)[0][1:]
        absolute_pathname = os.path.abspath(os.path.join(app.config['CONTENT_ROOT'], root_path) + app.config['CONTENT_EXTENSION'])
        try:
            mtime = os.path.getmtime(absolute_pathname)
        except OSError:
            self.log('ERROR', 'Page not found: ' + absolute_pathname)
            abort(404)
        page, old_mtime = self._page_cache.get(url, (None, None))
        if not page or mtime != old_mtime:
            with io.open(absolute_pathname, mode='r') as fd:
                self.log('NOTICE', 'Loading page %s' % absolute_pathname)
                head = ''.join(itertools.takewhile(unicode.strip, fd))
                body = fd.read()
            page = Page(head, body, url, mtime, self)
            self._page_cache[url] = (page, mtime)
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

    def active_trail(self, url):
        """
        Generate a set of menu IDs that are parents (i.e. part of the active
        menu trail) relative to the given page URL.
        """
        trail = set()
        for menu_id, menu in self._menu_cache.items():
            trail.update(menu[0].parent_menu_ids(url))
        return trail

    def load_contexts(self, sender, **extra):
        updated = False
        for name in os.listdir(app.config['CONFIG_ROOT']):
            if name.endswith(app.config['CONTENT_EXTENSION']) and name.startswith('context-'):
                filename = os.path.join(app.config['CONFIG_ROOT'], name)
                mtime = os.path.getmtime(filename)
                context_uid = os.path.splitext(os.path.basename(filename))[0]
                cached_context, old_mtime = self._context_cache.get(context_uid, (None, None))
                if not cached_context or mtime != old_mtime:
                    with io.open(filename, mode='r') as fd:
                        self.log('NOTICE', 'Loading context %s' % filename)
                        updated = True
                        self._context_cache[context_uid] = (yaml.load(fd.read()), mtime)
        if updated:
            # flush region data in all cached pages as context config has changed
            for page, mtime in self._page_cache.values():
                page.flush_regions()

    def region_blocks(self, region, page):
        """
        Get the names of the blocks (template names) that are defined in contexts to be
        displayed in a region of a page.
        """
        blocks = []
        for context in self._context_cache.values():
            context_data = context[0]
            if self._exact_context_match(context_data, 'global', True) or \
                    self._list_exact_context_match(context_data, 'type', page.meta['type']) or \
                    self._list_partial_context_match(context_data, 'url', page.url()[1:]):
                if region in context_data:
                    blocks.extend(context_data[region])
        return [block[0] for block in sorted(blocks, key=lambda block: block[1])]

    def _exact_context_match(self, context, key, value):
        """
        Returns true if the context dictionary contains the key/value pair.
        """
        return context.get(key, None) == value

    def _list_exact_context_match(self, context, key, value):
        """
        Returns true if the context dictionary contains the key and the sequence
        value associated with the key contains expected value.
        """
        return value in context.get(key, [])

    def _list_partial_context_match(self, context, key, actual):
        """
        Returns true if the context dictionary contains the key and the sequence
        value associated with the key contains a value that starts with the
        expected value.
        """
        for target in context.get(key, []):
            if actual.startswith(target):
                return True
        return False

    def menu(self, menu_uid):
        """
        Get a menu hierarchy
        """
        return self._menu_cache[menu_uid][0].root()

    def top_level_menu_items(self, menu_uid):
        """
        return a menus top level menu items
        """
        return self._menu_cache[menu_uid][0].root().children()

    def sub_menu(self, menu_uid, url):
        """
        Get the sub menu of a page.
        """
        menu_based_menu = self._menu_cache[menu_uid][0].sub_menu(url)
        if menu_based_menu is not None:
            return menu_based_menu
        else:
            page = self._url_to_page_index[url]
            if page.meta['type'] == 'recipe':
                return self.sub_menu(menu_uid, '/recipes.html')
            elif page.meta['type'] == 'review':
                return self.sub_menu(menu_uid, '/reviews.html')
            elif page.meta['type'] == 'news':
                return self.sub_menu(menu_uid, '/news.html')
            elif page.meta['type'] == 'fact-file':
                return self.sub_menu(menu_uid, '/food-fact-file.html')
            elif page.meta['type'] == 'faq':
                return self.sub_menu(menu_uid, '/faq.html')
        return None

    def clean(self):
        """
        Used for testing to clean the stored data associated with the site.
        """
        self.__init__()

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
