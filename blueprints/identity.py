from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import login_required, current_user, login_user
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
    customer_name = request.form.get('customer_name')
    password = request.form.get('password')
    if customer_name is None or password is None:
        flash('用户名或密码不能为空！')
    cus: Customer = Customer.query.filter_by(customer_name=customer_name).first()
    if cus is None:
        flash('用户名不存在！')
    if not cus.verify_password(password):
        flash('密码错误！')
    login_user(cus, True)
    next_route = request.args.get('next', '/', type=str)
    if not next_route.startswith('/'):
        next_route = '/'
    return redirect(next_route)


@identity.route('/manage')
def manage():
    if not current_user.is_authenticated:
        abort(403)
    return '管理页面'
