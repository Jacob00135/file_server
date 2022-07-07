import json
from werkzeug.test import TestResponse
from start import BaseTestCase
from models import Customer, Directory
from config import db


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


class UpdatePasswordTestCase(BaseTestCase):
    def test_update_password_1(self):
        """未登录用户请求修改密码：403"""
        response: TestResponse = self.client.post(self.identity_bp['update_password'], data={'password': '123456'})
        self.assertTrue(response.status_code == 403)

    def test_update_password_2(self):
        """修改密码请求：密码位数不在[6, 20]"""
        self.login('admin', '123456')
        response: TestResponse = self.client.post(self.identity_bp['update_password'], data={'password': '12'})
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 0)
        self.assertTrue(response.json['message'] == '密码长度不能少于6位，不能大于20位！')

        data: dict = {'password': '123456789012345678901234567890'}
        response: TestResponse = self.client.post(self.identity_bp['update_password'], data=data)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 0)
        self.assertTrue(response.json['message'] == '密码长度不能少于6位，不能大于20位！')

    def test_update_password_3(self):
        """修改密码请求：新旧密码一样"""
        self.login('admin', '123456')
        response: TestResponse = self.client.post(self.identity_bp['update_password'], data={'password': '123456'})
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 0)
        self.assertTrue(response.json['message'] == '新密码不能与旧密码相同！')

    def test_update_password_4(self):
        """修改密码请求：修改成功"""
        self.login('admin', '123456')
        response: TestResponse = self.client.post(self.identity_bp['update_password'], data={'password': '654321'})
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 1)
        self.assertTrue(Customer.query.filter_by(customer_name='admin').first().verify_password('654321'))


class AddDirTestCase(BaseTestCase):

    def test_add_dir_1(self):
        """未登录用户访问可见目录页面，403"""
        response: TestResponse = self.client.get(self.identity_bp['visible_dir'])
        self.assertTrue(response.status_code == 403)

    def test_add_dir_2(self):
        """已登录用户访问可见目录页面，200"""
        self.login('admin', '123456')
        response: TestResponse = self.client.get(self.identity_bp['visible_dir'])
        self.assertTrue(response.status_code == 200)

    def test_add_dir_3(self):
        """未登录用户请求添加目录：403"""
        response: TestResponse = self.client.post(self.identity_bp['add_dir'], data={'dir_path': 'C:\\', 'access': 4})
        self.assertTrue(response.status_code == 403)

    def test_add_dir_4(self):
        """添加目录请求：路径不存在"""
        self.login('admin', '123456')
        response: TestResponse = self.client.post(self.identity_bp['add_dir'], data={'dir_path': 'printf();', 'access': 1})
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 0)
        self.assertTrue(response.json['message'] == '路径不存在！')

    def test_add_dir_5(self):
        """添加目录请求：目录路径已添加过"""
        dir_1: Directory = Directory(dir_path='c:\\', access=4)
        db.session.add(dir_1)
        db.session.commit()
        self.login('admin', '123456')
        response: TestResponse = self.client.post(self.identity_bp['add_dir'], data={'dir_path': 'C:\\', 'access': 4})
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 0)
        self.assertTrue(response.json['message'] == '该目录已经被添加过！')

    def test_add_dir_6(self):
        """添加目录请求：访问权限不合法"""
        self.login('admin', '123456')
        response: TestResponse = self.client.post(self.identity_bp['add_dir'], data={'dir_path': 'C:\\', 'access': 3})
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 0)
        self.assertTrue(response.json['message'] == '访问权限只能是[1, 2, 4]其中一个！')

    def test_add_dir_7(self):
        """添加目录请求：添加成功"""
        self.login('admin', '123456')
        response: TestResponse = self.client.post(self.identity_bp['add_dir'], data={'dir_path': 'C:\\', 'access': 4})
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 1)
        self.assertTrue(Directory.query.filter_by(dir_path='c:\\', access=4).first() is not None)


class DeleteDirTestCase(BaseTestCase):

    def setUp(self) -> None:
        super(DeleteDirTestCase, self).setUp()
        self.dir_path_list: list = ['c:\\', 'd:\\', 'e:\\', 'f:\\', 'g:\\']
        for dir_path in self.dir_path_list:
            dir_object: Directory = Directory(dir_path=dir_path, access=1)
            db.session.add(dir_object)
        db.session.commit()

    def test_delete_dir_1(self):
        """未登录用户请求删除目录：403"""
        response: TestResponse = self.client.post(self.identity_bp['delete_dir'], data={'dir_path_list': json.dumps(['c:\\'])})
        self.assertTrue(response.status_code == 403)

    def test_delete_dir_2(self):
        """删除目录请求：json解析失败"""
        self.login('admin', '123456')
        response: TestResponse = self.client.post(self.identity_bp['delete_dir'], data={})
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 0)
        self.assertTrue(response.json['message'] == '请求数据不合法！')

        response: TestResponse = self.client.post(self.identity_bp['delete_dir'], data={'dir_path_list': 'printf("Hello);'})
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 0)
        self.assertTrue(response.json['message'] == '请求数据不合法！')

    def test_delete_dir_3(self):
        """删除目录请求：成功"""
        self.login('admin', '123456')
        data: dict = {'dir_path_list': json.dumps(self.dir_path_list)}
        response: TestResponse = self.client.post(self.identity_bp['delete_dir'], data=data)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 1)
        self.assertTrue(len(Directory.query.all()) == 0)
    
    def test_delete_dir_4(self):
        """删除目录请求：包含没有添加的目录"""
        self.login('admin', '123456')
        data: dict = {'dir_path_list': json.dumps(self.dir_path_list + ['c:\\users'])}
        response: TestResponse = self.client.post(self.identity_bp['delete_dir'], data=data)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 1)
        self.assertTrue(len(Directory.query.all()) == 0)
