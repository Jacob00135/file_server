import os.path
from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import current_user, login_user, logout_user
from models import Customer

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
    return render_template('identity/visible_dir.html', dir_list=[
        'F:\\GameCG',
        'E:\\GameCG\\Video',
        'G:\\workspace\\jpasmr',
        'G:\\L4D2_MAP',
        r'G:\learn_flask\file_server\learn_flask\file_server\learn_flask\file_server\learn_flask\file_server\learn_flask\file_server\learn_flask\file_server\learn_flask\file_server\learn_flask\file_server\learn_flask\file_server\learn_flask\file_server\learn_flask\file_server'
    ])


@identity.route('/add_dir', methods=['POST'])
def add_dir():
    if not current_user.is_authenticated:
        abort(403)
    dir_path = request.form.get('dir_path', '', type=str)
    if not os.path.exists(dir_path):
        return {'status': 0, 'message': '路径不存在！'}
    return {'status': 1}
