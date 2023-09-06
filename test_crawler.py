import unittest
from crawler import app, get_website_list

class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    def test_get_website_list(self):
        # Test the get_website_list function
        website_list = get_website_list()
        self.assertIsInstance(website_list, list)

    def test_add_website(self):
        # Test the add_website route
        response = self.app.post('/add_website', json={'url':''})
        self.assertEqual(response.status_code, 200)

    def test_scan_cookies(self):
        # Test the scan_cookies route
        response = self.app.get('/scan_cookies')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()