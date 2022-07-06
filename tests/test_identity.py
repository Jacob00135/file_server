from werkzeug.test import TestResponse
from start import BaseTestCase


class LoginTestCase(BaseTestCase):
    def test_login_1(self):
        """未登录用户访问登录页面，显示登录页面"""
        response: TestResponse = self.client.get(self.identity_bp['login'])
        self.assertTrue(response.status_code == 200)
        self.assertTrue(len(response.history) == 0)

    def test_login_2(self):
        """已登录用户访问登录页面，重定向到主页"""
        self.login('admin', '123456')
        response: TestResponse = self.client.get(self.identity_bp['login'], follow_redirects=True)
        self.verify_redirect(response, '/')

    def test_login_3(self):
        """登录请求：用户名或密码为空"""
        login_url: str = self.identity_bp['login']
        login_info: dict = {'password': '123456'}
        response: TestResponse = self.client.post(login_url, data=login_info, follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertFalse(self.is_logged())

        login_info: dict = {'customer_name': 'admin'}
        response: TestResponse = self.client.post(login_url, data=login_info, follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertFalse(self.is_logged())

    def test_login_4(self):
        """登录请求：密码错误"""
        self.login('admin', '654321', False)
        self.assertFalse(self.is_logged())

    def test_login_5(self):
        """登录请求：登录成功"""
        self.login('admin', '123456')

    def test_login_6(self):
        """未登录用户访问登出页面，直接重定向到主页"""
        self.logout()

    def test_login_7(self):
        """已登录用户访问登出页面，登出然后重定向到主页"""
        self.login('admin', '123456')
        self.logout()
        self.assertFalse(self.is_logged())
