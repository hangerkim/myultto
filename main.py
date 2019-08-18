import os

from app import app, DATABASE, init_db


if not os.path.exists(DATABASE):
    init_db()
