import os.path
import sqlite3
from typing import Union
from _sqlite3 import Connection, Cursor
from os import urandom
from werkzeug.security import generate_password_hash
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

BASE_DIR: str = os.path.dirname(__file__)
DATABASE_DIR: str = os.path.join(BASE_DIR, 'database_sqlite')
login_manager: LoginManager = LoginManager()
login_manager.login_view = 'identity.login'
db: SQLAlchemy = SQLAlchemy()
IDENTITY_ACCESS: dict = {
    'anonymous': 1,
    'administrator': 7
}

if not os.path.exists(DATABASE_DIR):
    os.mkdir(DATABASE_DIR)


class Config(object):
    HOST: str = '0.0.0.0'
    PORT: int = 2333
    SECRET_KEY: bytes = urandom(16)
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    MAX_CONTENT_LENGTH = 3 * 1024 * 1024 * 1024  # 限制传输单词请求传输数据大小为3GB
    MAX_FILE_COUNT = 20  # 一页最多显示的文件数目

    @staticmethod
    def init_app(app: Flask) -> None:
        pass


class DevelopmentConfig(Config):
    ENV: str = 'development'
    DEBUG: bool = True
    DATABASE_PATH = os.path.join(DATABASE_DIR, 'db.sqlite')
    SQLALCHEMY_DATABASE_URI: str = 'sqlite:///{}'.format(DATABASE_PATH)


class TestingConfig(Config):
    TESTING: bool = True
    DATABASE_PATH = os.path.join(DATABASE_DIR, 'db_test.sqlite')
    SQLALCHEMY_DATABASE_URI: str = 'sqlite:///{}'.format(DATABASE_PATH)


class ProductionConfig(Config):
    DATABASE_PATH = os.path.join(DATABASE_DIR, 'db.sqlite')
    SQLALCHEMY_DATABASE_URI: str = 'sqlite:///{}'.format(DATABASE_PATH)


config: dict = {
    'default': DevelopmentConfig,
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}


def create_app(config_name: str) -> Flask:
    # 配置类型
    config_class: Union[DevelopmentConfig, TestingConfig, ProductionConfig] = config[config_name]

    # 基础配置
    app: Flask = Flask(__name__)
    app.config.from_object(config_class)
    config_class.init_app(app)

    # Flask扩展配置
    login_manager.init_app(app)
    db.init_app(app)

    # 初始化数据库
    # 建表：customers
    con: Connection = sqlite3.connect(config_class.DATABASE_PATH)
    cursor: Cursor = con.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS customers (
        customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name VARCHAR(255) NOT NULL UNIQUE,
        password_hash VARCHAR(128) NOT NULL
    );""")
    con.commit()
    # 插入管理员身份记录
    result: tuple = cursor.execute('SELECT count(*) FROM customers WHERE customer_name="admin";').fetchone()
    if result[0] <= 0:
        cursor.execute('INSERT INTO customers(customer_name, password_hash) VALUES("admin", "{}");'.format(generate_password_hash('123456')))
        con.commit()
    # 建表：directory
    cursor.execute("""CREATE TABLE IF NOT EXISTS directory (
        dir_id   INTEGER PRIMARY KEY AUTOINCREMENT,
        dir_path TEXT    NOT NULL UNIQUE,
        access   INTEGER NOT NULL
    );""")
    con.commit()
    cursor.close()
    con.close()

    # 注册蓝图
    from blueprints.main import main as main_blueprint
    from blueprints.identity import identity as identity_blueprint
    app.register_blueprint(main_blueprint)
    app.register_blueprint(identity_blueprint, url_prefix='/identity')

    return app


if __name__ == '__main__':
    print(DevelopmentConfig.SQLALCHEMY_DATABASE_URI)
