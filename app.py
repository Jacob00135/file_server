from flask import Flask
from config import create_app, db
from models import Customer, Directory
from utils import FileItem

# app: Flask = create_app('development')
app: Flask = create_app('production')


@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Customer': Customer,
        'Directory': Directory,
        'FileItem': FileItem
    }


if __name__ == '__main__':
    app.run(host=app.config['HOST'], port=app.config['PORT'])
