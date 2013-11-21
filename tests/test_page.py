"""
Tests for Page objects
"""
import os
import unittest

from website.page import Page

# Setup global test data location
TEST_DATA_ROOT = os.path.join('tests', 'testdata', 'page')
# pass the root of the test data to the app via environment variable
os.environ['TEST_DATA_ROOT'] = TEST_DATA_ROOT

from website import app


class TestPageFunctions(unittest.TestCase):

    def setUp(self):
        app.config['CONTENT_ROOT'] = os.path.join(TEST_DATA_ROOT, u'content')
        app.config['CONFIG_ROOT'] = os.path.join(TEST_DATA_ROOT, u'config')
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_html(self):
        """
        Test html body content
        """
        head = "title: 'Hello World'"
        body = '<h1>Hello World</h2>'
        url = '/one/two/three/hello-world.html'
        modified_time = 23233232
        site = None
        page = Page(head, body, url, modified_time, site)
        assert page['title'] == 'Hello World'
        assert page.html == '<h1>Hello World</h2>'

    def test_attributes(self):
        """
        Test accessing attributes in the YAML header
        """
        yml_head = "title: Hello World\nkeywords: abc, 1234, xyx\nlist: [1, 2, 3]"
        body = '<h1>Hello World</h2>'
        url = '/one/two/three/hello-world.html'
        modified_time = 23233232
        site = None
        page = Page(yml_head, body, url, modified_time, site)
        assert page['title'] == 'Hello World'
        assert page['keywords'] == 'abc, 1234, xyx'
        assert page['list'][0] == 1
        assert page['list'][1] == 2
        assert page['list'][2] == 3

    def test_non_existent_attributes(self):
        """
        Test accessing attributes that do not exits
        """
        head = ''
        body = '<h1>Hello World</h2>'
        url = '/one/two/three/hello-world.html'
        modified_time = 23233232
        site = None
        page = Page(head, body, url, modified_time, site)
        assert page['title'] is ''

    def test_body_classes(self):
        """
        Test css classes for the HTML body tag
        """
        head = "title: Hello World\nkeywords: abc, 1234, xyx\nlist: [1, 2, 3]" \
               "\ntemplate: index"
        body = '<h1>Hello World</h2>'
        url = '/one/two/three/hello-world.html'
        modified_time = 23233232
        site = None
        page = Page(head, body, url, modified_time, site)
        assert page.body_classes() == 'index'

