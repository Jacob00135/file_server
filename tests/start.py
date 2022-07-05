import os.path
import unittest
from flask import current_app
from config import BASE_DIR, create_app, db
from models import Customer


class BaseTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.client = self.app.test_client(True)
        self.app_context.push()

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
        self.app_context.pop()


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
