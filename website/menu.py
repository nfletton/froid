import yaml


class Menu(object):
    def __init__(self, site):
        self._menu_item_map = dict()
        self._root = MenuItem('root', None, None, None)
        self._menu_item_map[self._root.uid] = self._root
        self._url_to_menu_item = dict()
        self._site = site

    def add_menu_item(self, uid, title, content_path, parent_uid):
        """
        Add a menu item to the the existing menu structure.

        Parent menu items must have been added before their children can be
        added.
        """
        url = self._site.page_from_url(content_path).url()
        parent_menu_item = self._menu_item_map[parent_uid]
        new_menu_item = MenuItem(uid, title, url, parent_menu_item)
        parent_menu_item.add_child(new_menu_item)
        self._menu_item_map[new_menu_item.uid] = new_menu_item
        self._url_to_menu_item.setdefault(url, []).append(new_menu_item)

    def menu_trail(self, uid):
        """
        A list of ascendant menu items from the menu item with the given UID.
        """
        return self._menu_item_map[uid].menu_trail()

    def load(self, yaml_data):
        """
        Load a menu from its configuration data.
        """
        data = yaml.load(yaml_data)['menu_items']
        for entry in data:
            self.add_menu_item(*entry)

    def sub_menu(self, url):
        """
        Returns a sub menu, if one exists, for the menu item with the given URL.
        """
        page_menu_item = self._url_to_menu_item.get(url, None)
        if page_menu_item is not None:
            trail = page_menu_item[0].menu_trail()
            # return the immediate child of the root menu item
            return trail[1]
        else:
            return None

    def root(self):
        """
        The root menu item of this menu
        """
        return self._root

    def parent_menu_ids(self, url):
        """
        Return a set of all menu item IDs associated with the URL (including
        parent menu item IDs)
        """
        menu_ids = set()
        # get menu items for this URL
        menu_items = self._url_to_menu_item.get(url, [])
        for menu_item in menu_items:
            for parent_menu_item in menu_item.menu_trail():
                menu_ids.add(parent_menu_item.uid)
        return menu_ids

    def top_level_menu_item(self, url):
        """
        Get the top level parent menu item for the URL.
        """
        menu_items = self._url_to_menu_item.get(url, [])
        if menu_items:
            trail = menu_items[0].menu_trail()
            if len(trail) > 1:
                # return the immediate child of the root menu item
                return trail[1]
        return None


class MenuItem(object):
    """
    Represent a single menu item in a menu structure
    """
    def __init__(self, uid, title, url, parent):
        self.uid = uid
        self.title = title
        self.url = url
        self._parent = parent
        self._children = list()
        self._url = None

    def add_child(self, menu_item):
        """
        Add a child menu item to this menu item.
        """
        self._children.append(menu_item)

    def children(self):
        """
        Return the child menu items of this item.
        """
        return self._children

    def menu_trail(self):
        """
        The list of this and ascendant menu items.
        """
        if self._parent is None:
            return [self]
        else:
            return self._parent.menu_trail() + [self]
