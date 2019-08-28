import os

from app import app, models


with app.app_context():
    models.db.create_all()
