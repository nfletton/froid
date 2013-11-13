import yaml


class Menu(object):
    def __init__(self, site):
        self._menu_item_map = dict()
        self._root = MenuItem('root', None, None, None, False)
        self._menu_item_map[self._root.uid] = self._root
        self._url_to_menu_item = dict()
        self._site = site

    def add_menu_item(self, uid, title, content_path, parent_uid, visible):
        url = self._site.page(content_path).url()
        parent_menu_item = self._menu_item_map[parent_uid]
        new_menu_item = MenuItem(uid, title, url, parent_menu_item, visible)
        parent_menu_item.add_child(new_menu_item)
        self._menu_item_map[new_menu_item.uid] = new_menu_item
        self._url_to_menu_item.setdefault(url, []).append(new_menu_item)

    def menu_trail(self, uid):
        return self._menu_item_map[uid].menu_trail()

    def load(self, yaml_data):
        data = yaml.load(yaml_data)['menu_items']
        for entry in data:
            self.add_menu_item(*entry)

    def sub_menu(self, url):
        page_menu_item = self._url_to_menu_item.get(url, None)
        if page_menu_item is not None:
            menu_trail = page_menu_item[0].menu_trail()
            return menu_trail[1]
        else:
            return None

    def root(self):
        return self._root

    def parent_menu_ids(self, url):
        """
        Return all menu item IDs associated with the URL (including parent menu
        item IDs)
        """
        menu_ids = []
        # get menu items for this URL
        menu_items = self._url_to_menu_item.get(url, [])
        for menu_item in menu_items:
            for parent_menu_item in menu_item.menu_trail():
                menu_ids.append(parent_menu_item.uid)
        return menu_ids

    def top_level_menu_item(self, url):
        menu_items = self._url_to_menu_item.get(url, [])
        if menu_items:
            trail = menu_items[0].menu_trail()
            if len(trail) > 1:
                # return the immediate child of the root menu item
                return trail[1]
        return None


class MenuItem(object):
    def __init__(self, uid, title, url, parent, visible):
        self.uid = uid
        self.title = title
        self.url = url
        self._parent = parent
        self.visible = visible
        self._children = list()
        self._url = None

    def add_child(self, menu_item):
        self._children.append(menu_item)

    def children(self):
        return self._children

    def menu_trail(self):
        if self._parent is None:
            return [self]
        else:
            return self._parent.menu_trail() + [self]
