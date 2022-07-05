from werkzeug.test import TestResponse
from start import BaseTestCase


class ErrorTestCase(BaseTestCase):

    def test_page_403(self):
        """403页面"""
        response: TestResponse = self.client.get('/identity/manage')
        self.assertTrue(response.status_code == 403)

    def test_page_404(self):
        """404页面"""
        response: TestResponse = self.client.get('/404')
        self.assertTrue(response.status_code == 404)

    # def test_page_500(self):
    #     """500页面"""
    #     response: TestResponse = self.client.get('/')
    #     self.assertTrue(response.status_code == 500)
