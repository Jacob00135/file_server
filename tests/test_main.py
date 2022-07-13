import os.path
import shutil
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


class DownloadTestCase(BaseTestCase):

    def setUp(self) -> None:
        super(DownloadTestCase, self).setUp()
        self.dir_path = BASE_DIR.lower()
        db.session.add(Directory(dir_path=self.dir_path, access=1))
        db.session.commit()

    def test_download_1(self):
        """下载文件：文件不存在于磁盘"""
        url: str = self.main_bp['download'].format(self.dir_path) + '?path=blueprints&filename=app.py'
        response: TestResponse = self.client.get(url)
        self.assertTrue(response.status_code == 404)

    def test_download_2(self):
        """下载文件：成功"""
        url: str = self.main_bp['download'].format(self.dir_path) + '?filename=app.py'
        response: TestResponse = self.client.get(url)
        self.assertTrue(response.status_code == 200)

    def test_download_3(self):
        """下载目录：成功"""
        url: str = self.main_bp['download'].format(self.dir_path) + '?path=blueprints'
        response: TestResponse = self.client.get(url)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 1)
        self.assertTrue(len(response.json['file_name_list']) == 3)


class RenameTestCase(BaseTestCase):

    def setUp(self) -> None:
        super(RenameTestCase, self).setUp()
        self.dir_path = BASE_DIR.lower()
        db.session.add(Directory(dir_path=self.dir_path, access=1))
        db.session.commit()

    def test_rename_1(self):
        """未登录用户请求重命名：403"""
        url: str = self.main_bp['rename'].format(self.dir_path) + '?filename=requirements.txt'
        response: TestResponse = self.client.post(url, data={'new-name': 'requirements.txt'})
        self.assertTrue(response.status_code == 403)

    def test_rename_2(self):
        """请求重命名：新文件名为空"""
        self.login('admin', '123456')
        url: str = self.main_bp['rename'].format(self.dir_path) + '?filename=requirements.txt'
        response: TestResponse = self.client.post(url, data={'new-name': ''})
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 0)
        self.assertTrue(response.json['message'] == '文件名不能为空！')

    def test_rename_3(self):
        """请求重命名：新旧文件名相同"""
        self.login('admin', '123456')
        url: str = self.main_bp['rename'].format(self.dir_path) + '?filename=requirements.txt'
        response: TestResponse = self.client.post(url, data={'new-name': 'requirements.txt'})
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 0)
        self.assertTrue(response.json['message'] == '新旧文件名不能相同！')

    def test_rename_4(self):
        """请求重命名：包含不合法字符"""
        self.login('admin', '123456')
        url: str = self.main_bp['rename'].format(self.dir_path) + '?filename=requirements.txt'
        response: TestResponse = self.client.post(url, data={'new-name': '\\requirements.txt'})
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 0)
        self.assertTrue(response.json['message'] == '文件名不能包含\\/:*?"<>|！')

    def test_rename_5(self):
        """请求重命名：新文件名已存在"""
        self.login('admin', '123456')
        url: str = self.main_bp['rename'].format(self.dir_path) + '?filename=requirements.txt'
        response: TestResponse = self.client.post(url, data={'new-name': '开发文档.md'})
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 0)
        self.assertTrue(response.json['message'] == '新文件名已存在')

    def test_rename_6(self):
        """请求重命名：重命名成功"""
        self.login('admin', '123456')
        url: str = self.main_bp['rename'].format(self.dir_path) + '?filename=requirements.txt'
        response: TestResponse = self.client.post(url, data={'new-name': '_requirements.txt'})
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 1)
        old_path = os.path.abspath(os.path.join(self.dir_path, '_requirements.txt'))
        new_path = os.path.abspath(os.path.join(self.dir_path, 'requirements.txt'))
        os.rename(old_path, new_path)


class CopyTestCase(BaseTestCase):

    def setUp(self) -> None:
        super(CopyTestCase, self).setUp()
        self.dir_path = BASE_DIR.lower()
        db.session.add(Directory(dir_path=self.dir_path, access=1))
        db.session.commit()

    def test_copy_1(self):
        """未登录用户请求复制：403"""
        url: str = self.main_bp['copy'].format(self.dir_path) + '?path=&filename=requirements.txt'
        data: dict = {'target-path': os.path.abspath(os.path.join(self.dir_path, 'blueprints'))}
        response: TestResponse = self.client.post(url, data=data)
        self.assertTrue(response.status_code == 403)

    def test_copy_2(self):
        """复制请求：目录路径为空"""
        self.login('admin', '123456')
        url: str = self.main_bp['copy'].format(self.dir_path) + '?path=&filename=requirements.txt'
        data: dict = {'target-path': ''}
        response: TestResponse = self.client.post(url, data=data)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 0)
        self.assertTrue(response.json['message'] == '目标路径不能为空！')

    def test_copy_3(self):
        """复制请求：与原路径相同"""
        self.login('admin', '123456')
        url: str = self.main_bp['copy'].format(self.dir_path) + '?path=&filename=requirements.txt'
        data: dict = {'target-path': self.dir_path}
        response: TestResponse = self.client.post(url, data=data)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 0)
        self.assertTrue(response.json['message'] == '原路径与目标路径不能相同！')

    def test_copy_4(self):
        """复制请求：目标路径不存在"""
        self.login('admin', '123456')
        url: str = self.main_bp['copy'].format(self.dir_path) + '?path=&filename=requirements.txt'
        data: dict = {'target-path': os.path.abspath(os.path.join(self.dir_path, 'test'))}
        response: TestResponse = self.client.post(url, data=data)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 0)
        self.assertTrue(response.json['message'] == '目标路径不存在！')

    def test_copy_5(self):
        """复制请求：目标路径中已存在同名文件"""
        source_path: str = os.path.abspath(os.path.join(self.dir_path, 'requirements.txt'))
        target_path: str = os.path.abspath(os.path.join(self.dir_path, 'blueprints', 'requirements.txt'))
        shutil.copy(source_path, target_path)
        self.login('admin', '123456')
        url: str = self.main_bp['copy'].format(self.dir_path) + '?path=&filename=requirements.txt'
        data: dict = {'target-path': os.path.abspath(os.path.join(self.dir_path, 'blueprints'))}
        response: TestResponse = self.client.post(url, data=data)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 0)
        self.assertTrue(response.json['message'] == '目标路径已存在相同名称的文件！')
        os.remove(target_path)

    def test_copy_6(self):
        """复制请求：尝试复制目录"""
        self.login('admin', '123456')
        url: str = self.main_bp['copy'].format(self.dir_path) + '?filename=blueprints'
        data: dict = {'target-path': os.path.abspath(os.path.join(self.dir_path, 'static'))}
        response: TestResponse = self.client.post(url, data=data)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 0)
        self.assertTrue(response.json['message'] == '不能复制目录，只能复制文件')

    def test_copy_7(self):
        """复制请求：成功"""
        self.login('admin', '123456')
        url: str = self.main_bp['copy'].format(self.dir_path) + '?path=&filename=requirements.txt'
        data: dict = {'target-path': os.path.abspath(os.path.join(self.dir_path, 'blueprints'))}
        response: TestResponse = self.client.post(url, data=data)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 1)
        os.remove(os.path.abspath(os.path.join(self.dir_path, 'blueprints', 'requirements.txt')))
