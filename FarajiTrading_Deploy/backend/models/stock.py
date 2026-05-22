
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Stock(db.Model):
    __tablename__ = "stocks"
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(10), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    sector = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class StockPrice(db.Model):
    __tablename__ = "stock_prices"
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(10), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    open_price = db.Column(db.Float)
    high_price = db.Column(db.Float)
    low_price = db.Column(db.Float)
    close_price = db.Column(db.Float)
    volume = db.Column(db.BigInteger)
    variation = db.Column(db.Float)
