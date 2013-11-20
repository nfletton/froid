import os

import werkzeug.utils
import yaml
from datetime import datetime


class Page(object):
    def __init__(self, head, body, url, modified_time, site):
        self.head = head
        self.body = body
        self.url = url
        self.modified_time = datetime.fromtimestamp(modified_time).isoformat() + '-07:00'
        self._site = site
        self._active_trail = None
        self.region_blocks = {}


    @werkzeug.utils.cached_property
    def meta(self):
        return yaml.safe_load(self.head) or {}

    @werkzeug.utils.cached_property
    def html(self):
        return self.body

    def __getitem__(self, name):
        if name in self.meta:
            return self.meta[name]
        else:
            return ''

    def menu(self, menu_uid):
        return self._site.menu(menu_uid).children()

    def sub_menu(self, menu_uid):
        menu = self._site.sub_menu(menu_uid, self.url())
        if menu is not None:
            menu = menu.children()
        return menu

    def css_classes(self):
        """
        Returns the css classes to be attached to the body tag of the page.
        Currently defaults to the name of the page template
        """
        return self.meta['template']

    def active_trail(self):
        """
        Returns a list of menu ids that are in the active trail for this page
        """
        if self._active_trail is None:
            self._active_trail = self._site.active_trail(self.url())
        return self._active_trail

    def blocks(self, region_name):
        """
        Get the block names for a region in the page
        """
        return self.region_blocks.setdefault(region_name, self._site.region_blocks(region_name, self))

    def flush_regions(self):
        """
        Flush an cached region block data
        """
        self.region_blocks = {}
