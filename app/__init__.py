import os

from flask import Flask
from flask_migrate import Migrate


def create_app(test_config=None):
    app = Flask(__name__)
    db_path = os.path.join(app.instance_path, 'myultto.db')
    db_uri = f'sqlite:///{db_path}'
    app.config.from_mapping(SQLALCHEMY_DATABASE_URI=db_uri)

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from app import filters, views
    from app.models import db

    migrate = Migrate(app, db)

    app.register_blueprint(filters.bp)
    app.register_blueprint(views.bp)

    db.init_app(app)

    return app
