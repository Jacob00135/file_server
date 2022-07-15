from werkzeug.security import generate_password_hash, check_password_hash
from config import db, login_manager, IDENTITY_ACCESS


class Customer(db.Model):
    __tablename__: str = 'customers'
    customer_id: int = db.Column(db.Integer, primary_key=True)
    customer_name: str = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash: str = db.Column(db.String(128), nullable=False)

    @property
    def is_active(self) -> bool:
        return True

    @property
    def is_authenticated(self) -> bool:
        return self.is_active

    @property
    def is_anonymous(self) -> bool:
        return False

    def get_id(self) -> str:
        return str(self.customer_id)

    @property
    def password(self) -> None:
        raise AttributeError('密码不是可读属性')

    @password.setter
    def password(self, password) -> None:
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return '<Customer "{}">'.format(self.customer_name)


class Directory(db.Model):
    __tablename__: str = 'directory'
    dir_id: int = db.Column(db.Integer, primary_key=True)
    dir_path: str = db.Column(db.Text, nullable=False, unique=True)
    access: int = db.Column(db.Integer, nullable=False)

    def can(self, perm) -> bool:
        return (self.access & perm) == self.access

    def admin_level(self) -> bool:
        return len(bin(IDENTITY_ACCESS['administrator']).replace('0b', '')) == len(bin(self.access).replace('0b', ''))

    def __repr__(self) -> str:
        return '<Directory "{}">'.format(self.dir_path)


@login_manager.user_loader
def load_user(customer_id):
    return Customer.query.get(int(customer_id))
