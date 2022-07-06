import os.path
import unittest
from werkzeug.test import TestResponse
from flask import current_app, url_for
from config import BASE_DIR, create_app, db
from models import Customer


class BaseTestCase(unittest.TestCase):
    identity_bp: dict = {
        'login': '/identity/login',
        'logout': '/identity/logout',
        'visible_dir': '/identity/visible_dir'
    }
    main_bp: dict = {
        'index': '/'
    }

    def setUp(self) -> None:
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.client = self.app.test_client(True)
        self.app_context.push()

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self, customer_name: str, password: str, verify=True) -> None:
        """登录"""
        login_url: str = self.identity_bp['login']
        login_info: dict = {'customer_name': customer_name, 'password': password}
        response: TestResponse = self.client.post(login_url, data=login_info, follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        if verify:
            self.assertTrue(self.is_logged())

    def logout(self) -> None:
        response: TestResponse = self.client.get(self.identity_bp['logout'], follow_redirects=True)
        self.verify_redirect(response, '/')

    def is_logged(self) -> bool:
        """是否已登录"""
        response: TestResponse = self.client.get(self.identity_bp['visible_dir'])
        return response.status_code == 200

    def verify_redirect(self, response: TestResponse, location: str) -> None:
        """检查重定向"""
        self.assertTrue(response.status_code == 200)
        self.assertTrue(len(response.history) == 1)
        self.assertTrue(response.history[0].status_code == 302)
        self.assertTrue(response.history[0].headers.get('Location') == location)


class ConfigTestCase(BaseTestCase):
    def test_app_config(self):
        """检查应用配置"""
        self.assertFalse(current_app is None)
        self.assertTrue(current_app.config['TESTING'])
        self.assertTrue(os.path.exists(current_app.config['DATABASE_PATH']))
        cus: Customer = Customer.query.filter_by(customer_name='admin').first()
        self.assertTrue(cus is not None)
        self.assertTrue(cus.verify_password('123456'))


if __name__ == '__main__':
    test = unittest.TestLoader().discover(os.path.join(BASE_DIR, 'tests'), pattern='*.py')
    unittest.TextTestRunner(verbosity=2).run(test)
