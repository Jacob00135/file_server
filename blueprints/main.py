from flask import Blueprint, render_template

main: Blueprint = Blueprint('main', __name__)


@main.app_errorhandler(403)
def forbidden(e):
    return render_template('main/403.html', status_code=403, en_desc='Forbidden', cn_desc='无权访问',
                           desc='您没有权限访问此页面'), 403


@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('main/404.html', status_code=404, en_desc='Not Found', cn_desc='页面不存在',
                           desc='页面不存在，请确保输入的网址正确'), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    return render_template('main/500.html', status_code=500, en_desc='Internal Server Error', cn_desc='服务器内部错误',
                           desc='网站服务器出现了一个错误，请重试'), 500


@main.route('/')
def index():
    return render_template('main/index.html')
