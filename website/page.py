import os

import werkzeug.utils
import yaml
from datetime import datetime
from flask import url_for


class Page(object):
    def __init__(self, head, body, content_path, modified_time, site):
        self.head = head
        self.body = body
        self.content_path = content_path
        self.modified_time = datetime.fromtimestamp(modified_time).isoformat() + '-07:00'
        self._site = site
        self.name = os.path.split(os.path.splitext(content_path)[0])[1]
        self._active_trail = None
        self.region_blocks = {}

    def url(self, **kwargs):
        return url_for('content', url_path=self.name, **kwargs)

    @werkzeug.utils.cached_property
    def meta(self):
        return yaml.safe_load(self.head) or {}

    @werkzeug.utils.cached_property
    def html(self):
        return self.body

    def menu(self, menu_uid):
        return self._site.menu(menu_uid).children()

    def css_classes(self):
        """
        Returns the css classes to be attached to the body tag of the page.
        Currently defaults to the name of the page template
        """
        return self.meta['template']

    def active_trail(self):
        """
        Returns a list of page URLs that are in the active trail for this page
        """
        if self._active_trail is None:
            self._active_trail = self._site.page_active_trail(self.url())
        return self._active_trail
