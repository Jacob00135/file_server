import os.path
from werkzeug.test import TestResponse
from start import BaseTestCase
from models import Directory
from config import db, BASE_DIR
from utils import FileItem


class ErrorPageTestCase(BaseTestCase):

    def test_page_403(self):
        """403页面"""
        response: TestResponse = self.client.get(self.identity_bp['visible_dir'])
        self.assertTrue(response.status_code == 403)

    def test_page_404(self):
        """404页面"""
        response: TestResponse = self.client.get('/404')
        self.assertTrue(response.status_code == 404)

    # def test_page_500(self):
    #     """500页面"""
    #     response: TestResponse = self.client.get('/')
    #     self.assertTrue(response.status_code == 500)


class FileItemTestCase(BaseTestCase):

    def setUp(self) -> None:
        super(FileItemTestCase, self).setUp()
        self.dir_path = BASE_DIR.lower()
        db.session.add(Directory(dir_path=self.dir_path, access=1))
        db.session.commit()

    def test_file_item_1(self):
        """测试FileItem类：可见目录"""
        file_item: FileItem = FileItem(self.dir_path, '', '')
        self.assertTrue(file_item.visible_dir_path == self.dir_path)
        self.assertTrue(file_item.path == '')
        self.assertTrue(file_item.name == '')
        self.assertTrue(file_item.full_path == self.dir_path)
        self.assertTrue(file_item.file_type == 'dir')
        self.assertTrue(file_item.size == '')
        self.assertTrue(file_item.is_visible_dir)
        self.assertTrue(file_item.is_dir)

    def test_file_item_2(self):
        """测试FileItem类：可见目录的子目录"""
        file_item: FileItem = FileItem(self.dir_path, '', 'blueprints')
        self.assertTrue(file_item.visible_dir_path == self.dir_path)
        self.assertTrue(file_item.path == 'blueprints')
        self.assertTrue(file_item.name == 'blueprints')
        self.assertTrue(file_item.full_path == os.path.join(os.path.join(self.dir_path, 'blueprints')))
        self.assertTrue(file_item.file_type == 'dir')
        self.assertTrue(file_item.size == '')
        self.assertFalse(file_item.is_visible_dir)
        self.assertTrue(file_item.is_dir)

    def test_file_item_3(self):
        """测试FileItem类：可见目录的文件"""
        file_item: FileItem = FileItem(self.dir_path, '', 'app.py')
        self.assertTrue(file_item.visible_dir_path == self.dir_path)
        self.assertTrue(file_item.path == '')
        self.assertTrue(file_item.name == 'app.py')
        self.assertTrue(file_item.full_path == os.path.join(os.path.join(self.dir_path, 'app.py')))
        self.assertTrue(file_item.file_type == 'text')
        self.assertFalse(file_item.is_visible_dir)
        self.assertFalse(file_item.is_dir)

    def test_file_item_4(self):
        """测试FileItem类：文件不存在"""
        with self.assertRaises(OSError):
            FileItem(self.dir_path, '', 'not_found_file')


class VisitVisibleDirTestCase(BaseTestCase):

    def setUp(self) -> None:
        super(VisitVisibleDirTestCase, self).setUp()
        self.dir_path = BASE_DIR.lower()
        db.session.add(Directory(dir_path=self.dir_path, access=1))
        db.session.add(Directory(dir_path='c:\\', access=4))
        db.session.commit()

    def test_visit_visible_dir_1(self):
        """测试文件管理页面：可见目录不存在于磁盘"""
        response: TestResponse = self.client.get(self.main_bp['visit_visible_dir'].format('not_found_file'))
        self.assertTrue(response.status_code == 404)

    def test_visit_visible_dir_2(self):
        """测试文件管理页面：可见目录不存在于数据库"""
        response: TestResponse = self.client.get(self.main_bp['visit_visible_dir'].format('g:\\not_found'))
        self.assertTrue(response.status_code == 404)

    def test_visit_visible_dir_3(self):
        """测试文件管理页面：无权访问"""
        response: TestResponse = self.client.get(self.main_bp['visit_visible_dir'].format('c:\\'))
        self.assertTrue(response.status_code == 403)

    def test_visit_visible_dir_4(self):
        """测试文件管理页面：path参数不合法"""
        url: str = self.main_bp['visit_visible_dir'].format(self.dir_path) + '?path=' + os.path.split(BASE_DIR.lower())[0]
        response: TestResponse = self.client.get(url)
        self.assertTrue(response.status_code == 404)

    def test_visit_visible_dir_5(self):
        """测试文件管理页面：子目录不存在"""
        self.login('admin', '123456')
        url: str = self.main_bp['visit_visible_dir'].format('c:\\') + '?path=not_found'
        response: TestResponse = self.client.get(url)
        self.assertTrue(response.status_code == 404)

    def test_visit_visible_dir_6(self):
        """测试文件管理页面：访问成功"""
        url: str = self.main_bp['visit_visible_dir'].format(self.dir_path) + '?path=\\static\\base\\'
        response: TestResponse = self.client.get(url)
        self.assertTrue(response.status_code == 200)
