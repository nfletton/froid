from importlib import import_module
import io
import os
from random import shuffle
import itertools

import yaml
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

    def page_from_url(self, url):
        """
        Get a page from its URL.
        """
        if url[0] == '/':
            url = url[1:]
        content_root_path = os.path.splitext(url)[0]
        for extension in app.config['CONTENT_EXTENSIONS']:
            candidate_path = content_root_path +  extension
            absolute_path = os.path.abspath(
                os.path.join(app.config['CONTENT_ROOT'], candidate_path))
            if os.path.isfile(absolute_path):
                return self.page_from_path(candidate_path)
        abort(404)

    def page_from_path(self, content_path):
        """
        Get a page from its relative content path.
        """
        absolute_path = os.path.abspath(os.path.join(app.config['CONTENT_ROOT'],
                                                     content_path))
        try:
            mtime = os.path.getmtime(absolute_path)
        except OSError:
            self.log('ERROR', 'Page not found: ' + absolute_path)
            abort(404)
        page, old_mtime = self._page_cache.get(content_path, (None, None))
        if not page or mtime != old_mtime:
            with io.open(absolute_path, mode='r') as fd:
                self.log('NOTICE', 'Loading page %s' % absolute_path)
                head = ''.join(itertools.takewhile(unicode.strip, fd))
                body = fd.read()
            page = self.create_page(head, body, content_path, mtime, self)
            self._page_cache[content_path] = (page, mtime)
        return page

    @staticmethod
    def create_page(head, body, content_path, modified_time, site):
        """
        Factory method to create pages.

        By default create a page withe the class Page. If page YAML
        contains a 'type' attribute, then try to create a class
        of 'type' specified. If no such class exists, fallback to
        the Page class.
        """
        head_data = yaml.safe_load(head)
        if head_data and 'type' in head_data:
            try:
                module = import_module('website.page')
                class_ = getattr(module, head_data['type'])
                return class_(head_data, body, content_path, modified_time,
                              site)
            except AttributeError:
                pass
        return Page(head_data, body, content_path, modified_time, site)

    def pages(self):
        """
        Get all content pages.
        """
        for (dirpath, dirnames, filenames) in os.walk(
                app.config['CONTENT_ROOT']):
            for name in filenames:
                extension = os.path.splitext(name)[1]
                if extension in app.config['CONTENT_EXTENSIONS']:
                    yield self.page_from_path(
                        os.path.relpath(os.path.join(dirpath, name),
                                        app.config['CONTENT_ROOT']))

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
            pages = sorted(pages, key=lambda page: page.meta['published'],
                           reverse=True)
        elif sort == 'priority':
            pages = sorted(pages, key=lambda page: page['priority'])
        elif sort == 'random':
            shuffle(pages)
        return pages[0:quantity]

    def pages_by_type(self, page_type):
        """
        Get all pages of a given type
        """
        for page in self.pages():
            try:
                if page_type == page.meta['type']:
                    yield page
            except KeyError:
                pass

    def load_menus(self, sender, **extra):
        for name in os.listdir(app.config['CONFIG_ROOT']):
            if name.endswith('.yml') and name.startswith('nav-'):
                filename = os.path.join(app.config['CONFIG_ROOT'], name)
                mtime = os.path.getmtime(filename)
                menu_uid = os.path.splitext(os.path.basename(filename))[0]
                cached_menu, old_mtime = self._menu_cache.get(menu_uid,
                                                              (None, None))
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
            if name.endswith('.yml') and name.startswith('context-'):
                filename = os.path.join(app.config['CONFIG_ROOT'], name)
                mtime = os.path.getmtime(filename)
                context_uid = os.path.splitext(os.path.basename(filename))[0]
                cached_context, old_mtime = self._context_cache.get(context_uid,
                                                                    (
                                                                    None, None))
                if not cached_context or mtime != old_mtime:
                    with io.open(filename, mode='r') as fd:
                        self.log('NOTICE', 'Loading context %s' % filename)
                        updated = True
                        self._context_cache[context_uid] = (
                        yaml.load(fd.read()), mtime)
        if updated:
            # flush region data in all cached pages as context config
            # has changed
            for page, mtime in self._page_cache.values():
                page.flush_regions()

    def region_blocks(self, region, page):
        """
        Get the names of the blocks (template names) that are defined in
        contexts to be displayed in a region of a page.
        """
        blocks = []
        for context in self._context_cache.values():
            context_data = context[0]
            if self._exact_context_match(context_data, 'global', True) or \
                    self._list_exact_context_match(context_data, 'type',
                                                   page.meta['type']) or \
                    self._list_partial_context_match(context_data, 'url',
                                                     page.url()[1:]):
                if region in context_data:
                    blocks.extend(context_data[region])
        return [block[0] for block in
                sorted(blocks, key=lambda block: block[1])]

    def _exact_context_match(self, context, key, value):
        """
        Returns true if the context dictionary contains the key/value pair.
        """
        return context.get(key, None) == value

    def _list_exact_context_match(self, context, key, value):
        """
        Returns true if the context dictionary contains the key and
        the sequence value associated with the key contains expected value.
        """
        return value in context.get(key, [])

    def _list_partial_context_match(self, context, key, actual):
        """
        Returns true if the context dictionary contains the key and
        the sequence value associated with the key contains a value that
         starts with the expected value.
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
