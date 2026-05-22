
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80), unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    balance       = db.Column(db.Float, default=100000.0)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Portfolio(db.Model):
    __tablename__ = "portfolio"
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"))
    ticker     = db.Column(db.String(10), nullable=False)
    quantity   = db.Column(db.Integer, nullable=False)
    buy_price  = db.Column(db.Float, nullable=False)
    buy_date   = db.Column(db.DateTime, default=datetime.utcnow)

class Transaction(db.Model):
    __tablename__ = "transactions"
    id               = db.Column(db.Integer, primary_key=True)
    user_id          = db.Column(db.Integer, db.ForeignKey("users.id"))
    ticker           = db.Column(db.String(10), nullable=False)
    transaction_type = db.Column(db.String(10), nullable=False)
    quantity         = db.Column(db.Integer, nullable=False)
    price            = db.Column(db.Float, nullable=False)
    total            = db.Column(db.Float, nullable=False)
    date             = db.Column(db.DateTime, default=datetime.utcnow)

class Watchlist(db.Model):
    __tablename__ = "watchlist"
    id       = db.Column(db.Integer, primary_key=True)
    user_id  = db.Column(db.Integer, db.ForeignKey("users.id"))
    ticker   = db.Column(db.String(10), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
