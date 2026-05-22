
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.stock import db
from models.user import User, Portfolio, Transaction, Watchlist
from services.scraper import CasablancaScraper
from config import CASABLANCA_STOCKS

portfolio_bp = Blueprint("portfolio", __name__)
scraper = CasablancaScraper()

@portfolio_bp.route("/", methods=["GET"])
@jwt_required()
def get_portfolio():
    user_id = get_jwt_identity()
    positions = Portfolio.query.filter_by(user_id=user_id).all()
    portfolio_data = []
    total_invested = 0
    total_current = 0
    for pos in positions:
        current_data = scraper.get_stock_data(pos.ticker)
        current_price = current_data["price"]
        invested = pos.quantity * pos.buy_price
        current_value = pos.quantity * current_price
        pnl = current_value - invested
        pnl_percent = ((current_price - pos.buy_price) / pos.buy_price) * 100
        total_invested += invested
        total_current += current_value
        portfolio_data.append({
            "id": pos.id, "ticker": pos.ticker,
            "name": CASABLANCA_STOCKS.get(pos.ticker, {}).get("name", pos.ticker),
            "quantity": pos.quantity, "buy_price": pos.buy_price,
            "current_price": current_price,
            "invested": round(invested, 2), "current_value": round(current_value, 2),
            "pnl": round(pnl, 2), "pnl_percent": round(pnl_percent, 2),
            "buy_date": pos.buy_date.isoformat()
        })
    user = User.query.get(user_id)
    return jsonify({
        "positions": portfolio_data,
        "summary": {
            "total_invested": round(total_invested, 2),
            "total_current": round(total_current, 2),
            "total_pnl": round(total_current - total_invested, 2),
            "total_pnl_percent": round(((total_current - total_invested) / total_invested * 100) if total_invested > 0 else 0, 2),
            "cash_balance": round(user.balance, 2),
            "total_value": round(user.balance + total_current, 2)
        }
    })

@portfolio_bp.route("/buy", methods=["POST"])
@jwt_required()
def buy_stock():
    user_id = get_jwt_identity()
    data = request.get_json()
    ticker = data.get("ticker", "").upper()
    quantity = data.get("quantity", 0)
    if ticker not in CASABLANCA_STOCKS:
        return jsonify({"error": "Action non trouvée"}), 404
    if quantity <= 0:
        return jsonify({"error": "Quantité invalide"}), 400
    stock_data = scraper.get_stock_data(ticker)
    price = stock_data["price"]
    total_cost = price * quantity
    user = User.query.get(user_id)
    if user.balance < total_cost:
        return jsonify({"error": f"Solde insuffisant. Coût: {total_cost:.2f} MAD"}), 400
    existing = Portfolio.query.filter_by(user_id=user_id, ticker=ticker).first()
    if existing:
        total_qty = existing.quantity + quantity
        avg_price = (existing.quantity * existing.buy_price + quantity * price) / total_qty
        existing.quantity = total_qty
        existing.buy_price = round(avg_price, 2)
    else:
        position = Portfolio(user_id=user_id, ticker=ticker, quantity=quantity, buy_price=price)
        db.session.add(position)
    user.balance -= total_cost
    transaction = Transaction(user_id=user_id, ticker=ticker, transaction_type="BUY",
        quantity=quantity, price=price, total=total_cost)
    db.session.add(transaction)
    db.session.commit()
    return jsonify({"message": f"Achat de {quantity} actions {ticker} à {price:.2f} MAD",
        "total_cost": round(total_cost, 2), "new_balance": round(user.balance, 2)})

@portfolio_bp.route("/sell", methods=["POST"])
@jwt_required()
def sell_stock():
    user_id = get_jwt_identity()
    data = request.get_json()
    ticker = data.get("ticker", "").upper()
    quantity = data.get("quantity", 0)
    if quantity <= 0:
        return jsonify({"error": "Quantité invalide"}), 400
    position = Portfolio.query.filter_by(user_id=user_id, ticker=ticker).first()
    if not position:
        return jsonify({"error": "Vous ne possédez pas cette action"}), 404
    if position.quantity < quantity:
        return jsonify({"error": f"Quantité insuffisante"}), 400
    stock_data = scraper.get_stock_data(ticker)
    price = stock_data["price"]
    total_revenue = price * quantity
    user = User.query.get(user_id)
    user.balance += total_revenue
    if position.quantity == quantity:
        db.session.delete(position)
    else:
        position.quantity -= quantity
    transaction = Transaction(user_id=user_id, ticker=ticker, transaction_type="SELL",
        quantity=quantity, price=price, total=total_revenue)
    db.session.add(transaction)
    db.session.commit()
    return jsonify({"message": f"Vente de {quantity} actions {ticker} à {price:.2f} MAD",
        "total_revenue": round(total_revenue, 2), "new_balance": round(user.balance, 2)})

@portfolio_bp.route("/transactions", methods=["GET"])
@jwt_required()
def get_transactions():
    user_id = get_jwt_identity()
    transactions = Transaction.query.filter_by(user_id=user_id).order_by(Transaction.date.desc()).limit(50).all()
    return jsonify([{
        "id": t.id, "ticker": t.ticker,
        "name": CASABLANCA_STOCKS.get(t.ticker, {}).get("name", t.ticker),
        "type": t.transaction_type, "quantity": t.quantity,
        "price": t.price, "total": t.total, "date": t.date.isoformat()
    } for t in transactions])

@portfolio_bp.route("/watchlist", methods=["GET"])
@jwt_required()
def get_watchlist():
    user_id = get_jwt_identity()
    items = Watchlist.query.filter_by(user_id=user_id).all()
    watchlist = []
    for item in items:
        data = scraper.get_stock_data(item.ticker)
        data["name"] = CASABLANCA_STOCKS.get(item.ticker, {}).get("name", item.ticker)
        data["sector"] = CASABLANCA_STOCKS.get(item.ticker, {}).get("sector", "")
        data["watchlist_id"] = item.id
        watchlist.append(data)
    return jsonify(watchlist)

@portfolio_bp.route("/watchlist", methods=["POST"])
@jwt_required()
def add_to_watchlist():
    user_id = get_jwt_identity()
    data = request.get_json()
    ticker = data.get("ticker", "").upper()
    if ticker not in CASABLANCA_STOCKS:
        return jsonify({"error": "Action non trouvée"}), 404
    existing = Watchlist.query.filter_by(user_id=user_id, ticker=ticker).first()
    if existing:
        return jsonify({"error": "Déjà dans la watchlist"}), 400
    item = Watchlist(user_id=user_id, ticker=ticker)
    db.session.add(item)
    db.session.commit()
    return jsonify({"message": f"{ticker} ajouté à la watchlist"})
