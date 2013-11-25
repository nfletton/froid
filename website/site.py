import io
import os
from random import shuffle
import yaml
import itertools

from flask import abort

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
        Get a page from its URL
        """
        if url[0] == '/':
            url = url[1:]
        content_path = os.path.join(
            app.config['CONTENT_ROOT'],
            os.path.splitext(url)[0]) + app.config['CONTENT_EXTENSION']
        absolute_path = os.path.abspath(content_path)
        try:
            mtime = os.path.getmtime(absolute_path)
        except OSError:
            self.log('ERROR', 'Page not found: ' + absolute_path)
            abort(404)
        page, old_mtime = self._page_cache.get(url, (None, None))
        if not page or mtime != old_mtime:
            with io.open(absolute_path, mode='r') as fd:
                self.log('NOTICE', 'Loading page %s' % absolute_path)
                head = ''.join(itertools.takewhile(unicode.strip, fd))
                body = fd.read()
            page = Page(head, body, url, mtime, self)
            self._page_cache[url] = (page, mtime)
        return page

    def pages(self):
        """
        Get all content pages. Primarily used to create an XML sitemap.

        It scans the content directory for all YAML files and makes
        a test request on a number of possible URLs that the YAML
        file may represent the content for. The first URL that
        returns a successful response against the Flask test client is
        used to obtain the corresponding page object.
        """
        with app.test_client() as test_client:
            for (dirpath, dirnames, filenames) in os.walk(app.config['CONTENT_ROOT']):
                for name in filenames:
                    if name.endswith(app.config['CONTENT_EXTENSION']):
                        root_name = os.path.splitext(name)[0]
                        for extension in app.config['URL_EXTENSIONS']:
                            rel_path = os.path.relpath(dirpath, app.config['CONTENT_ROOT'])
                            if rel_path == '.':
                                candidate_url = '/' + root_name + extension
                            else:
                                candidate_url = '/' + rel_path + '/' + root_name + extension
                            response = test_client.get(candidate_url)
                            if response.status_code == 200:
                                yield self.page(candidate_url)
                                break

    def pages_by_destination(self, destination, sort=None, quantity=30):
        """
        Get pages marked for display in a particular destination.
        Typically used for displaying content in blocks and atom feed.
        """
        pages = []
        for page in self.pages():
            try:
                if destination in page.meta['post_in']:
                    pages.append(page)
            except KeyError:
                pass
        if sort == 'date':
            pages = sorted(pages, key=lambda page: page.meta['published'], reverse=True)
        elif sort == 'priority':
            pages = sorted(pages, key=lambda page: page['priority'])
        elif sort == 'random':
            shuffle(pages)
        return pages[0:quantity]

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

    def sub_menu_items(self, menu_uid, url):
        """
        Get the sub menu items of a page.
        """
        menu_based_menu = self._menu_cache[menu_uid][0].sub_menu(url)
        if menu_based_menu is not None:
            return menu_based_menu.children()
        else:
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
