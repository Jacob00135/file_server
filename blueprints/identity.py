import os.path
import json
import re
from json.decoder import JSONDecodeError
from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import current_user, login_user, logout_user
from config import db
from models import Customer, Directory
from decorators import anonymous_forbidden

identity: Blueprint = Blueprint('identity', __name__)


@identity.route('/login', methods=['GET', 'POST'])
def login():
    # GET
    if request.method == 'GET':
        if current_user.is_authenticated:
            return redirect(url_for('main.index'))
        return render_template('identity/login.html')

    # POST
    customer_name: str = request.form.get('customer_name')
    password: str = request.form.get('password')
    if customer_name is None or password is None:
        flash('用户名或密码不能为空！')
        return render_template('identity/login.html')
    cus: Customer = Customer.query.filter_by(customer_name=customer_name).first()
    if cus is None:
        flash('用户名不存在！')
        return render_template('identity/login.html')
    if not cus.verify_password(password):
        flash('密码错误！')
        return render_template('identity/login.html', customer_name=customer_name)
    login_user(cus, True)
    next_route = request.args.get('next', '/', type=str)
    if not next_route.startswith('/'):
        next_route = '/'
    return redirect(next_route)


@identity.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
    return redirect(url_for('main.index'))


@identity.route('/visible_dir')
@anonymous_forbidden
def visible_dir():
    return render_template('identity/visible_dir.html', dir_list=Directory.query.all())


@identity.route('/add_dir', methods=['POST'])
@anonymous_forbidden
def add_dir():
    dir_path: str = request.form.get('dir_path', '', type=str).lower().replace('/', '\\')
    access: int = request.form.get('access', 0, type=int)
    if access not in [1, 2, 4]:
        return {'status': 0, 'message': '访问权限只能是[1, 2, 4]其中一个！'}
    if '\\' not in dir_path or not os.path.exists(dir_path) or not re.findall('^[a-zA-Z]', dir_path) or not os.path.isdir(dir_path):
        return {'status': 0, 'message': '路径不存在！'}
    dir_path: str = os.path.abspath(dir_path)
    if Directory.query.filter_by(dir_path=dir_path).first() is not None:
        return {'status': 0, 'message': '该目录已经被添加过！'}
    dir_object: Directory = Directory(dir_path=dir_path, access=access)
    db.session.add(dir_object)
    db.session.commit()
    return {'status': 1}


@identity.route('/delete_dir', methods=['POST'])
@anonymous_forbidden
def delete_dir():
    dir_path_list: str = request.form.get('dir_path_list', '', type=str)
    try:
        dir_path_list: list = json.loads(dir_path_list)
    except JSONDecodeError:
        return {'status': 0, 'message': '请求数据不合法！'}
    for dir_path in dir_path_list:
        dir_object = Directory.query.filter_by(dir_path=dir_path).first()
        if dir_object is not None:
            db.session.delete(dir_object)
    db.session.commit()
    return {'status': 1}


@identity.route('/update_password', methods=['POST'])
@anonymous_forbidden
def update_password():
    password: str = request.form.get('password')
    password_length = len(password)
    if password_length < 6 or password_length > 20:
        return {'status': 0, 'message': '密码长度不能少于6位，不能大于20位！'}
    if current_user.verify_password(password):
        return {'status': 0, 'message': '新密码不能与旧密码相同！'}
    current_user.password = password
    db.session.add(current_user)
    db.session.commit()
    return {'status': 1}


@identity.route('/update_access', methods=['POST'])
@anonymous_forbidden
def update_access():
    update_item: str = request.form.get('update_item', '', type=str)
    try:
        update_item: list = json.loads(update_item)
    except JSONDecodeError:
        return {'status': 0, 'message': '请求数据不合法！'}
    for item in update_item:
        dir_path: str = item.get('dir_path', '')
        access: int = item.get('access', 0)
        dir_object = Directory.query.filter_by(dir_path=dir_path).first()
        if dir_object is not None and access in [1, 2, 4]:
            dir_object.access = access
            db.session.add(dir_object)
    db.session.commit()
    return {'status': 1}
