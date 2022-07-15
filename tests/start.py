import os.path
import unittest
from werkzeug.test import TestResponse
from flask import current_app
from config import BASE_DIR, create_app, db
from models import Customer, Directory
from config import IDENTITY_ACCESS


class BaseTestCase(unittest.TestCase):
    identity_bp: dict = {
        'login': '/identity/login',
        'logout': '/identity/logout',
        'update_password': '/identity/update_password',
        'visible_dir': '/identity/visible_dir',
        'add_dir': '/identity/add_dir',
        'delete_dir': '/identity/delete_dir',
        'update_access': '/identity/update_access'
    }
    main_bp: dict = {
        'index': '/',
        'visit_visible_dir': '/{}',
        'download': '/download/{}',
        'rename': '/rename/{}',
        'copy': '/copy/{}',
        'move': '/move/{}',
        'remove': '/remove/{}'
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

    def insert_test_directory_item(self) -> None:
        self.dir_path_list: list = ['c:\\', 'd:\\', 'e:\\', 'f:\\', 'g:\\']
        for dir_path in self.dir_path_list:
            dir_object: Directory = Directory(dir_path=dir_path, access=1)
            db.session.add(dir_object)
        db.session.commit()


class ConfigTestCase(BaseTestCase):
    def test_app_config(self):
        """检查应用配置"""
        self.assertFalse(current_app is None)
        self.assertTrue(current_app.config['TESTING'])
        self.assertTrue(os.path.exists(current_app.config['DATABASE_PATH']))
        table_name_list: list = [t.name for t in db.get_tables_for_bind()]
        self.assertTrue(len(table_name_list) == 2)
        self.assertTrue('customers' in table_name_list)
        self.assertTrue('directory' in table_name_list)
        cus: Customer = Customer.query.filter_by(customer_name='admin').first()
        self.assertTrue(cus is not None)
        self.assertTrue(cus.verify_password('123456'))


class CustomerTestCase(BaseTestCase):

    def test_password_hash(self):
        """测试自动生成password_hash"""
        cus = Customer(customer_name='xiaoming', password='123456')
        with self.assertRaises(AttributeError):
            print(cus.password)
        self.assertTrue(cus.password_hash is not None)

    def test_verify_password(self):
        """测试verify_password函数"""
        cus = Customer(customer_name='xiaoming', password='123456')
        db.session.add(cus)
        db.session.commit()
        self.assertTrue(cus.verify_password('123456'))
        self.assertFalse(cus.verify_password('098765'))


class DirectoryTestCase(BaseTestCase):

    def test_can(self):
        """Directory模型的can方法"""
        dir_1: Directory = Directory(dir_path='C:\\Users', access=1)
        dir_2: Directory = Directory(dir_path='C:\\', access=4)
        db.session.add(dir_1)
        db.session.add(dir_2)
        db.session.commit()
        self.assertTrue(dir_1.can(IDENTITY_ACCESS['anonymous']))
        self.assertTrue(dir_1.can(IDENTITY_ACCESS['administrator']))
        self.assertFalse(dir_2.can(IDENTITY_ACCESS['anonymous']))
        self.assertTrue(dir_2.can(IDENTITY_ACCESS['administrator']))

    def test_admin_level(self):
        """Directory模型的admin_level方法"""
        dir_1: Directory = Directory(dir_path='C:\\Users', access=1)
        dir_2: Directory = Directory(dir_path='C:\\', access=4)
        db.session.add(dir_1)
        db.session.add(dir_2)
        db.session.commit()
        self.assertFalse(dir_1.admin_level())
        self.assertTrue(dir_2.admin_level())


if __name__ == '__main__':
    test = unittest.TestLoader().discover(os.path.join(BASE_DIR, 'tests'), pattern='*.py')
    unittest.TextTestRunner(verbosity=2).run(test)
