import os.path
from os import urandom
from flask import Flask

BASE_DIR: str = os.path.dirname(__file__)
DATABASE_DIR: str = os.path.join(BASE_DIR, 'database_sqlite')


class Config(object):
    HOST: str = '0.0.0.0'
    PORT: int = 2333
    SECRET_KEY: bytes = urandom(16)
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    @staticmethod
    def init_app(app: Flask) -> None:
        pass


class DevelopmentConfig(Config):
    ENV: str = 'development'
    DEBUG: bool = True
    SQLALCHEMY_DATABASE_URI: str = 'sqlite:///{}'.format(os.path.join(DATABASE_DIR, 'db.sqlite'))


class TestingConfig(Config):
    TESTING: bool = True
    SQLALCHEMY_DATABASE_URI: str = 'sqlite:///{}'.format(os.path.join(DATABASE_DIR, 'db_test.sqlite'))


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI: str = 'sqlite:///{}'.format(os.path.join(DATABASE_DIR, 'db.sqlite'))


config: dict = {
    'default': DevelopmentConfig,
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}


if __name__ == '__main__':
    print(DevelopmentConfig.SQLALCHEMY_DATABASE_URI)
