import os
from flask import Blueprint, render_template, abort, request, send_from_directory
from flask_login import current_user
from models import Directory
from utils import FileItem, sort_file_item

main: Blueprint = Blueprint('main', __name__)


def check_path(dir_path: str):
    # 检查权限、路径是否仍存在
    if not os.path.exists(dir_path):
        abort(404)
    visible_dir: Directory = Directory.query.filter_by(dir_path=dir_path).first_or_404()
    if visible_dir.admin_level() and not current_user.is_authenticated:
        abort(403)

    # 检查子目录路径是否存在
    path: str = request.args.get('path', '', type=str).lower().replace('/', '\\')
    if path.startswith('\\'):
        path: str = path[1:]
    if path.endswith('\\'):
        path: str = path[:-1]
    if path != '' and os.path.commonprefix([dir_path, path]) == path:
        abort(404)
    page_dir_path: str = os.path.abspath(os.path.join(dir_path, path))
    if not os.path.isdir(page_dir_path) or not os.path.exists(page_dir_path):
        abort(404)

    return page_dir_path, path


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
    file_item_list: list = []
    for dir_object in dir_list:
        try:
            file_item: FileItem = FileItem(dir_object.dir_path, '', '')
        except OSError:
            continue
        file_item_list.append(file_item)
    sort_file_item(file_item_list)
    return render_template('main/index.html', file_item_list=file_item_list)


@main.route('/<dir_path>')
def visit_visible_dir(dir_path: str):
    # 检查请求参数
    result: tuple = check_path(dir_path)
    page_dir_path: str = result[0]
    path: str = result[1]

    # 获取所有直属子目录和直属文件
    file_item_list: list = []
    for file_name in os.listdir(page_dir_path):
        try:
            file_item: FileItem = FileItem(dir_path, path, file_name)
        except OSError:
            continue
        file_item_list.append(file_item)
    sort_file_item(file_item_list)

    # 响应
    return render_template(
        'main/index.html',
        file_item_list=file_item_list,
        dir_path=None if path == '' else dir_path,
        prev_dir_path=os.path.split(path)[0],
        page_dir_path=page_dir_path.replace('\\', ' \\ ')
    )


@main.route('/download/<dir_path>')
def download(dir_path: str):
    # 检查请求参数
    result: tuple = check_path(dir_path)
    page_dir_path: str = result[0]
    file_name: str = request.args.get('filename', '', type=str)
    full_path: str = os.path.abspath(os.path.join(page_dir_path, file_name))
    if not os.path.exists(full_path):
        abort(404)

    # 下载非目录文件
    if not os.path.isdir(full_path):
        # 如果有中文乱码问题，则使用以下代码：
        """from urllib.parse import quote
        quote_file_name: str = quote(file_name)
        rv = send_from_directory(page_dir_path, file_name, as_attachment=True, attachment_filename=quote_file_name)
        rv.headers['Content-Disposition'] = rv.headers['Content-Disposition'] + "; filename*=utf-8''{}".format(quote_file_name)
        return rv"""
        attachment: bool = request.args.get('attachment', False, type=bool)
        return send_from_directory(page_dir_path, file_name, as_attachment=attachment)

    # 下载目录
    file_name_list: list = []
    for file_name in os.listdir(full_path):
        file_path: str = os.path.abspath(os.path.join(full_path, file_name))
        if os.path.exists(file_path) and not os.path.isdir(file_path):
            file_name_list.append(file_name)
    return {'status': 1, 'file_name_list': file_name_list}
