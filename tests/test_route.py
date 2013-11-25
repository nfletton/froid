"""
Tests for URL routing
"""
import os
import unittest

# Setup global test data location
TEST_DATA_ROOT = os.path.join('tests', 'testdata', u'simple-routes')
# pass the root of the test data to the app via environment variable
os.environ['TEST_DATA_ROOT'] = TEST_DATA_ROOT

from website import app
from website import site


class TestRoutingFunctions(unittest.TestCase):

    def setUp(self):
        app.config['CONTENT_ROOT'] = os.path.join(TEST_DATA_ROOT, u'content')
        app.config['CONFIG_ROOT'] = os.path.join(TEST_DATA_ROOT, u'config')
        self.app = app.test_client()

    def tearDown(self):
        site.clean()

    def test_index_route(self):
        """
        Route to index page with path '/'
        """
        response = self.app.get('/')
        assert 'Test route to index page' in response.data

    def test_index_route_alternate(self):
        """
        Route to index page with full path
        """
        response = self.app.get('/index.html')
        assert 'Test route to index page' in response.data

    def test_top_level_route(self):
        """
        Route to page in content root
        """
        response = self.app.get('/top-level-content.html')
        assert 'Test route to top level content' in response.data

    def test_subfolder_route(self):
        """
        Route to page in sub folder
        """
        response = self.app.get('/subfolder/nested-content.html')
        assert 'Test route to subfolder content' in response.data

    def test_not_found_route(self):
        """
        Route to non-existent page
        """
        response = self.app.get('/not-here.html')
        assert response.status_code == 404
        assert 'Test Page Not Found' in response.data

    def test_not_found_subfolder_route(self):
        """
        Route to non-existent page in subfolders
        """
        response = self.app.get('/x/y/z/not-here.html')
        assert response.status_code == 404
        assert 'Test Page Not Found' in response.data

    def test_raw_document_route(self):
        """
        Route to raw document i.e. non-HTML
        """
        response = self.app.get('/rawfiles/raw.pdf')
        assert response.status_code == 200

    def test_raw_text_file_route(self):
        """
        Route to raw text file
        """
        response = self.app.get('/robots.txt')
        assert 'Allow: /' in response.data

    def test_raw_file_not_found_route(self):
        """
        Route to non-existent non-HTML file
        """
        response = self.app.get('/not-found.txt')
        assert response.status_code == 404
        assert 'Test Page Not Found' in response.data

    def test_sitemap_feed(self):
        """
        Route to the generated XML sitemap
        """
        response = self.app.get('/sitemap.xml')
        assert response.status_code == 200
        assert '<?xml version="1.0" encoding="utf-8"?>' in response.data
        assert 'index.html' in response.data
        # the 404 page should not be in the sitemap because 404.yml includes
        # "blocked: ['sitemap']
        assert '404.html' not in response.data

    def test_atom_feed(self):
        """
        Route to the generated XML Atom feed
        """
        response = self.app.get('/atom.xml')
        assert response.status_code == 200
        assert '<feed xmlns="http://www.w3.org/2005/Atom">' in response.data
        assert 'index.html' in response.data
        assert '<name>John Doe</name>' in response.data
        # the 404 page should not be in the sitemap because 404.yml includes
        # "blocked: ['sitemap']
        assert '404.html' not in response.data

if __name__ == '__main__':
    unittest.main()
