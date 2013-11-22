"""
Tests for Site object
"""
import os
import unittest

# Setup global test data location
from werkzeug.exceptions import NotFound

TEST_DATA_ROOT = os.path.join('tests', 'testdata', 'site')
# pass the root of the test data to the app via environment variable
os.environ['TEST_DATA_ROOT'] = TEST_DATA_ROOT

from website import app
from website import site


class TestSiteFunctions(unittest.TestCase):

    def setUp(self):
        app.config['CONTENT_ROOT'] = os.path.join(TEST_DATA_ROOT, u'content')
        app.config['CONFIG_ROOT'] = os.path.join(TEST_DATA_ROOT, u'config')
        app.config['TESTING'] = True
        self.app = app.test_client()

    def tearDown(self):
        site.clean()

    def test_index_page_load(self):
        """
        Load the site index page
        """
        page = site.page('/index.html')
        assert page['title'] == 'Test loading of index page'
        assert page['keywords'] == 'keyword1, keyword2, keyword3, keyword4'
        assert page['template'] == 'index'
        assert page['heading'] == 'Home Page'
        assert page.html == '<p>Test loading of index page</p>\n'

    def test_sub_directory_page_load(self):
        """
        Load a page in a sub directory
        """
        page = site.page('/subfolder/nested-content.html')
        assert page['title'] == 'Test loading of page in subfolder'
        assert page['keywords'] == 'keyword10, keyword20, keyword30, keyword40'
        assert page['template'] == 'page'
        assert page['heading'] == 'Sub Page'
        assert page.html == '<h1>Test loading of subfolder content</h2>\n'

    def test_non_existent_page_load(self):
        """
        Attempt to load a page that does not exist
        """
        try:
            site.page('/does-not-exist.html')
            assert False
        except NotFound:
            assert True

    def test_loading_from_page_cache(self):
        """
        Test page loaded from page cache on second load
        """
        # first load
        site.page('/index.html')
        assert len(site._page_cache) == 1
        assert 'index.html' in site._page_cache
        # hack content in the cache and check next page load contains the change
        cached_page = site._page_cache['index.html'][0]
        cached_page.html = '<p>new content</p>'
        page = site.page('/index.html')
        assert page.html == '<p>new content</p>'

    def test_active_trail(self):
        """
        Test the correct menu IDs are returned for the active trail of a page.
        """
        # make a request to force the menus to be loaded
        self.app.get('/index.html')
        # get the active trail for the page
        active_trail = site.active_trail('nav-3-2-2.html')
        # test IDs in main nav are returned
        assert 'nav-3-2-2' in active_trail
        assert 'nav-3-2' in active_trail
        assert 'nav-3' in active_trail
        # also test that ID in secondary nav is also returned
        assert 'nav-sec-3' in active_trail

    def test_menu(self):
        """
        Test we get the correct menu hierarchy.
        """
        # make a request to force the menus to be loaded
        self.app.get('/index.html')
        menu_hierarchy = site.menu('nav-main')
        assert len(menu_hierarchy.children()) == 5
        assert menu_hierarchy.children()[0].uid == 'nav-1'
        assert len(menu_hierarchy.children()[0].children()) == 0
        assert menu_hierarchy.children()[1].uid == 'nav-2'
        assert len(menu_hierarchy.children()[1].children()) == 0
        assert menu_hierarchy.children()[2].uid == 'nav-3'
        assert len(menu_hierarchy.children()[2].children()) == 4
        assert menu_hierarchy.children()[3].uid == 'nav-4'
        assert len(menu_hierarchy.children()[3].children()) == 0
        assert menu_hierarchy.children()[4].uid == 'nav-5'
        assert len(menu_hierarchy.children()[4].children()) == 0
        assert menu_hierarchy.children()[2].children()[0].uid == 'nav-3-1'
        assert len(menu_hierarchy.children()[2].children()[0].children()) == 0
        assert menu_hierarchy.children()[2].children()[1].uid == 'nav-3-2'
        assert len(menu_hierarchy.children()[2].children()[1].children()) == 3
        assert menu_hierarchy.children()[2].children()[2].uid == 'nav-3-3'
        assert len(menu_hierarchy.children()[2].children()[2].children()) == 0
        assert menu_hierarchy.children()[2].children()[3].uid == 'nav-3-4'
        assert len(menu_hierarchy.children()[2].children()[3].children()) == 0
        assert menu_hierarchy.children()[2].children()[1].children()[0].uid == 'nav-3-2-1'
        assert menu_hierarchy.children()[2].children()[1].children()[1].uid == 'nav-3-2-2'
        assert menu_hierarchy.children()[2].children()[1].children()[2].uid == 'nav-3-2-3'

    def test_top_level_menu_items(self):
        # make a request to force the menus to be loaded
        self.app.get('/index.html')
        menu_items = site.top_level_menu_items('nav-main')
        assert len(menu_items) == 5
        assert menu_items[0].uid == 'nav-1'
        assert menu_items[1].uid == 'nav-2'
        assert menu_items[2].uid == 'nav-3'
        assert menu_items[3].uid == 'nav-4'
        assert menu_items[4].uid == 'nav-5'


if __name__ == '__main__':
    unittest.main()
