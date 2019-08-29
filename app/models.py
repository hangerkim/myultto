from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property

db = SQLAlchemy()


class Result(db.Model):
    __tablename__ = 'result'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    published_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    candidates = db.relationship('Candidate', backref='result', lazy=False)
    seed = db.Column(db.BigInteger, nullable=False)

    @hybrid_property
    def winners(self):
        return (Candidate.query.with_parent(self)
                .filter_by(is_winner=True)
                .all())


class Candidate(db.Model):
    __tablename__ = 'candidate'

    id = db.Column(db.Integer, primary_key=True)
    is_winner = db.Column(db.Boolean, nullable=False, default=False)
    name = db.Column(db.String(128), nullable=False)
    result_id = db.Column(db.Integer, db.ForeignKey('result.id'),
                          nullable=False)
