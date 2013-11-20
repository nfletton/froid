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

    def test_constructor(self):
        head = {'title': 'Hello World'}
        body = '<h1>Hello World</h2>'
        url = '/one/two/three/hello-world.html'
        modified_time = 23233232
        site = None
        page = Page(head, body, url, modified_time, site)
        assert page.url == '/one/two/three/hello-world.html'
