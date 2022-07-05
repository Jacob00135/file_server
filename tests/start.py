import os.path
import unittest
from flask import current_app
from config import BASE_DIR, DATABASE_DIR
from app import create_app, db


class BaseTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.client = self.app.test_client(True)
        self.app_context.push()
        db.create_all()

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
        self.app_context.pop()


class ConfigTestCase(BaseTestCase):
    def test_app_exists(self):
        """检查应用配置"""
        self.assertFalse(current_app is None)
        self.assertTrue(current_app.config['TESTING'])
        self.assertTrue(os.path.exists(os.path.join(DATABASE_DIR, 'db_test.sqlite')))


if __name__ == '__main__':
    test = unittest.TestLoader().discover(os.path.join(BASE_DIR, 'tests'))
    unittest.TextTestRunner(verbosity=2).run(test)
