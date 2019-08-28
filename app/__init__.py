import os
import sqlite3

from flask import Flask, g

from . import models

app = Flask(__name__)
app.config['SQLITE_DATABASE_PATH'] = (
    os.path.join(app.instance_path, 'myultto.db'))
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f'sqlite:///{app.config["SQLITE_DATABASE_PATH"]}')
models.db.init_app(app)


from app import filters, views  # noqa: E402, F401
