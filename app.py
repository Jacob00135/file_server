from flask import Flask
from config import create_app, db
from models import Customer

app: Flask = create_app('development')
# app = create_app('production')


@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Customer': Customer
    }


if __name__ == '__main__':
    app.run(host=app.config['HOST'], port=app.config['PORT'])
