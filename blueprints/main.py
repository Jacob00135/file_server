import os
from flask import Blueprint, render_template, abort, request
from flask_login import current_user
from models import Directory
from utils import FileItem

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
    if current_user.is_authenticated:
        dir_list: list = Directory.query.all()
    else:
        dir_list: list = Directory.query.filter_by(access=1).all()
    return render_template('main/index.html', dir_list=dir_list)


@main.route('/<dir_path>')
def visit_visible_dir(dir_path):
    # 检查权限
    visible_dir: Directory = Directory.query.filter_by(dir_path=dir_path).first_or_404()
    if visible_dir.admin_level() and not current_user.is_authenticated:
        abort(403)

    # 检查路径
    full_path: str = os.path.abspath(os.path.join(dir_path, request.args.get('path', '', type=str)))
    if not os.path.isdir(full_path) or os.path.exists(full_path):
        abort(404)

    # 获取所有直属子目录和直属文件
    file_item_list: list = []
    for f in os.listdir(full_path):
        try:
            file_item_list.append(FileItem(f))
        except OSError:
            continue
    return render_template('main/index.html', file_item_list=file_item_list)
