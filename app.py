from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from config import config

login_manager: LoginManager = LoginManager()
login_manager.login_view = 'identity.login'
db: SQLAlchemy = SQLAlchemy()


def create_app(config_name: str) -> Flask:
    # 基础配置
    app: Flask = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Flask扩展配置
    login_manager.init_app(app)
    db.init_app(app)

    # 注册蓝图
    from blueprints.main import main as main_blueprint
    from blueprints.identity import identity as identity_blueprint
    app.register_blueprint(main_blueprint)
    app.register_blueprint(identity_blueprint, url_prefix='/identity')

    return app


app: Flask = create_app('development')
# app = create_app('production')


if __name__ == '__main__':
    app.run(host=app.config['HOST'], port=app.config['PORT'])
