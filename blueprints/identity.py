import os.path
from typing import Union
from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import current_user, login_user, logout_user
from config import db
from models import Customer, Directory

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
def visible_dir():
    if not current_user.is_authenticated:
        abort(403)
    return render_template('identity/visible_dir.html', dir_list=Directory.query.all())


@identity.route('/add_dir', methods=['POST'])
def add_dir():
    if not current_user.is_authenticated:
        abort(403)
    dir_path: str = request.form.get('dir_path', '', type=str).lower()
    access: int = request.form.get('access', 0, type=int)
    if access not in [1, 2, 4]:
        return {'status': 0, 'message': '访问权限只能是[1, 2, 4]其中一个！'}
    if ('/' not in dir_path and '\\' not in dir_path) or not os.path.exists(dir_path):
        return {'status': 0, 'message': '路径不存在！'}
    if Directory.query.filter_by(dir_path=dir_path).first() is not None:
        return {'status': 0, 'message': '该目录已经被添加过！'}
    dir_object: Directory = Directory(dir_path=dir_path, access=access)
    db.session.add(dir_object)
    db.session.commit()
    return {'status': 1}
