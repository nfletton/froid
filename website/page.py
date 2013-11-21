from datetime import datetime

from werkzeug.utils import cached_property
import yaml


class Page(object):
    def __init__(self, head, body, url, modified_time, site):
        self.__head = head
        self.__body = body
        self.url = url
        self.__modified_time = datetime.fromtimestamp(modified_time).isoformat() + '-07:00'
        self._site = site
        self._active_trail = None
        self.region_blocks = {}

    @cached_property
    def meta(self):
        """
        Load the YAML from the head of the content file.
        """
        return yaml.safe_load(self.__head) or {}

    @cached_property
    def html(self):
        """
        Return the HTML (markdown, ...) content of the page.

        This is where you would apply any content filters such as markdown.
        """
        return self.__body

    def __getitem__(self, name):
        """
        Get attributes from YAML header.

        From templates these are accessed as: {{ page.title|safe }}
        """
        return self.meta[name] if name in self.meta else ''

    # def menu(self, menu_uid):
    #     return self._site.menu(menu_uid).children()

    # TODO: test
    def sub_menu(self, menu_uid):
        menu = self._site.sub_menu(menu_uid, self.url)
        if menu is not None:
            menu = menu.children()
        return menu

    def body_classes(self):
        """
        Returns the css classes to be attached to the body tag of the page.
        Currently defaults to the name of the page template
        """
        return self['template']

    def active_trail(self):
        """
        Returns a list of menu ids that are in the active trail for this page
        """
        if self._active_trail is None:
            self._active_trail = self._site.active_trail(self.url)
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
