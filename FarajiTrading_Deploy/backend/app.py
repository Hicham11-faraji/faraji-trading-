
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)
from config import Config, CASABLANCA_STOCKS
from models.database import db, User, Portfolio, Transaction, Watchlist
from services.market_data import MarketData
from datetime import datetime

# ============================================
# INITIALISATION
# ============================================
def create_app():
    app = Flask(
        __name__,
        static_folder="../frontend",
        static_url_path=""
    )
    app.config.from_object(Config)

    CORS(app)
    JWTManager(app)
    db.init_app(app)

    with app.app_context():
        db.create_all()

    # ============================================
    # ROUTE PRINCIPALE
    # ============================================
    @app.route("/")
    def index():
        try:
            return send_from_directory("../frontend", "index.html")
        except:
            return jsonify({
                "message": "FarajiTrading API",
                "status" : "running",
                "version": "1.0",
                "endpoints": [
                    "/api/stocks/list",
                    "/api/stocks/market-summary",
                    "/api/stocks/<ticker>",
                    "/api/stocks/<ticker>/historical",
                    "/api/auth/login",
                    "/api/auth/register",
                    "/api/portfolio/",
                    "/api/portfolio/buy",
                    "/api/portfolio/sell",
                ]
            })

    # ============================================
    # ROUTES STOCKS
    # ============================================
    @app.route("/api/stocks/list")
    def list_stocks():
        stocks = MarketData.get_all_stocks(CASABLANCA_STOCKS)
        return jsonify(stocks)

    @app.route("/api/stocks/market-summary")
    def market_summary():
        stocks  = MarketData.get_all_stocks(CASABLANCA_STOCKS)
        gainers = [s for s in stocks if s.get("variation", 0) > 0]
        losers  = [s for s in stocks if s.get("variation", 0) < 0]
        return jsonify({
            "stocks": stocks,
            "stats" : {
                "total"      : len(stocks),
                "gainers"    : len(gainers),
                "losers"     : len(losers),
                "top_gainer" : max(stocks, key=lambda x: x.get("variation", 0)),
                "top_loser"  : min(stocks, key=lambda x: x.get("variation", 0)),
            }
        })

    @app.route("/api/stocks/<ticker>")
    def get_stock(ticker):
        ticker = ticker.upper()
        if ticker not in CASABLANCA_STOCKS:
            return jsonify({"error": "Action non trouvee"}), 404
        data           = MarketData.get_stock(ticker)
        data["name"]   = CASABLANCA_STOCKS[ticker]["name"]
        data["sector"] = CASABLANCA_STOCKS[ticker]["sector"]
        return jsonify(data)

    @app.route("/api/stocks/<ticker>/historical")
    def get_historical(ticker):
        ticker = ticker.upper()
        days   = request.args.get("days", 180, type=int)
        if ticker not in CASABLANCA_STOCKS:
            return jsonify({"error": "Action non trouvee"}), 404
        data = MarketData.get_historical(ticker, days)
        return jsonify({
            "ticker": ticker,
            "name"  : CASABLANCA_STOCKS[ticker]["name"],
            "data"  : data
        })

    @app.route("/api/stocks/sectors")
    def get_sectors():
        sectors = {}
        for ticker, info in CASABLANCA_STOCKS.items():
            sec = info["sector"]
            if sec == "Indice":
                continue
            if sec not in sectors:
                sectors[sec] = {
                    "stocks"          : [],
                    "total_variation" : 0,
                    "count"           : 0
                }
            data           = MarketData.get_stock(ticker)
            data["name"]   = info["name"]
            sectors[sec]["stocks"].append(data)
            sectors[sec]["total_variation"] += data.get("variation", 0)
            sectors[sec]["count"]           += 1

        for sec in sectors:
            n = sectors[sec]["count"]
            if n > 0:
                sectors[sec]["avg_variation"] = round(
                    sectors[sec]["total_variation"] / n, 2
                )
        return jsonify(sectors)

    @app.route("/api/stocks/search")
    def search_stocks():
        q = request.args.get("q", "").upper().strip()
        if not q:
            return jsonify([])
        results = []
        for ticker, info in CASABLANCA_STOCKS.items():
            if q in ticker or q.lower() in info["name"].lower():
                data           = MarketData.get_stock(ticker)
                data["name"]   = info["name"]
                data["sector"] = info["sector"]
                results.append(data)
        return jsonify(results)

    # ============================================
    # ROUTES AUTH
    # ============================================
    @app.route("/api/auth/register", methods=["POST"])
    def register():
        data     = request.get_json()
        username = data.get("username", "").strip()
        email    = data.get("email", "").strip()
        password = data.get("password", "")

        if not username or not email or not password:
            return jsonify({"error": "Tous les champs sont requis"}), 400
        if len(password) < 6:
            return jsonify({"error": "Mot de passe trop court (min 6)"}), 400
        if User.query.filter_by(username=username).first():
            return jsonify({"error": "Nom d utilisateur deja pris"}), 400
        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email deja utilise"}), 400

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        token = create_access_token(identity=user.id)
        return jsonify({
            "message": "Inscription reussie !",
            "token"  : token,
            "user"   : {
                "id"      : user.id,
                "username": user.username,
                "email"   : user.email,
                "balance" : user.balance,
            }
        }), 201

    @app.route("/api/auth/login", methods=["POST"])
    def login():
        data     = request.get_json()
        username = data.get("username", "")
        password = data.get("password", "")
        user     = User.query.filter_by(username=username).first()

        if not user or not user.check_password(password):
            return jsonify({"error": "Identifiants incorrects"}), 401

        token = create_access_token(identity=user.id)
        return jsonify({
            "message": "Connexion reussie !",
            "token"  : token,
            "user"   : {
                "id"      : user.id,
                "username": user.username,
                "email"   : user.email,
                "balance" : user.balance,
            }
        })

    # ============================================
    # ROUTES PORTFOLIO
    # ============================================
    @app.route("/api/portfolio/", methods=["GET"])
    @jwt_required()
    def get_portfolio():
        user_id   = get_jwt_identity()
        positions = Portfolio.query.filter_by(user_id=user_id).all()
        user      = User.query.get(user_id)

        port_data      = []
        total_investi  = 0
        total_actuel   = 0

        for pos in positions:
            stock_data    = MarketData.get_stock(pos.ticker)
            current_price = stock_data["price"]
            invested      = pos.quantity * pos.buy_price
            current_val   = pos.quantity * current_price
            pnl           = current_val - invested
            pnl_pct       = (pnl / invested) * 100 if invested > 0 else 0

            total_investi += invested
            total_actuel  += current_val

            port_data.append({
                "id"           : pos.id,
                "ticker"       : pos.ticker,
                "name"         : CASABLANCA_STOCKS.get(pos.ticker, {}).get("name", pos.ticker),
                "quantity"     : pos.quantity,
                "buy_price"    : pos.buy_price,
                "current_price": current_price,
                "invested"     : round(invested, 2),
                "current_value": round(current_val, 2),
                "pnl"          : round(pnl, 2),
                "pnl_percent"  : round(pnl_pct, 2),
                "buy_date"     : pos.buy_date.isoformat(),
            })

        return jsonify({
            "positions": port_data,
            "summary"  : {
                "total_invested"  : round(total_investi, 2),
                "total_current"   : round(total_actuel, 2),
                "total_pnl"       : round(total_actuel - total_investi, 2),
                "total_pnl_percent": round(
                    (total_actuel - total_investi) / total_investi * 100
                    if total_investi > 0 else 0, 2
                ),
                "cash_balance"    : round(user.balance, 2),
                "total_value"     : round(user.balance + total_actuel, 2),
            }
        })

    @app.route("/api/portfolio/buy", methods=["POST"])
    @jwt_required()
    def buy_stock():
        user_id  = get_jwt_identity()
        data     = request.get_json()
        ticker   = data.get("ticker", "").upper()
        quantity = int(data.get("quantity", 0))

        if ticker not in CASABLANCA_STOCKS:
            return jsonify({"error": "Action non trouvee"}), 404
        if quantity <= 0:
            return jsonify({"error": "Quantite invalide"}), 400

        stock_data = MarketData.get_stock(ticker)
        price      = stock_data["price"]
        total_cost = price * quantity

        user = User.query.get(user_id)
        if user.balance < total_cost:
            return jsonify({
                "error": f"Solde insuffisant. "
                         f"Cout: {total_cost:.2f} MAD, "
                         f"Solde: {user.balance:.2f} MAD"
            }), 400

        existing = Portfolio.query.filter_by(
            user_id=user_id, ticker=ticker
        ).first()

        if existing:
            total_qty      = existing.quantity + quantity
            avg_price      = (existing.quantity * existing.buy_price + quantity * price) / total_qty
            existing.quantity  = total_qty
            existing.buy_price = round(avg_price, 2)
        else:
            pos = Portfolio(
                user_id=user_id, ticker=ticker,
                quantity=quantity, buy_price=price
            )
            db.session.add(pos)

        user.balance -= total_cost

        tx = Transaction(
            user_id=user_id, ticker=ticker,
            transaction_type="BUY",
            quantity=quantity, price=price, total=total_cost
        )
        db.session.add(tx)
        db.session.commit()

        return jsonify({
            "message"    : f"Achat de {quantity} {ticker} a {price:.2f} MAD",
            "total_cost" : round(total_cost, 2),
            "new_balance": round(user.balance, 2),
        })

    @app.route("/api/portfolio/sell", methods=["POST"])
    @jwt_required()
    def sell_stock():
        user_id  = get_jwt_identity()
        data     = request.get_json()
        ticker   = data.get("ticker", "").upper()
        quantity = int(data.get("quantity", 0))

        if quantity <= 0:
            return jsonify({"error": "Quantite invalide"}), 400

        pos = Portfolio.query.filter_by(
            user_id=user_id, ticker=ticker
        ).first()
        if not pos:
            return jsonify({"error": "Position non trouvee"}), 404
        if pos.quantity < quantity:
            return jsonify({"error": "Quantite insuffisante"}), 400

        stock_data    = MarketData.get_stock(ticker)
        price         = stock_data["price"]
        total_revenue = price * quantity
        pnl           = (price - pos.buy_price) * quantity

        user          = User.query.get(user_id)
        user.balance += total_revenue

        if pos.quantity == quantity:
            db.session.delete(pos)
        else:
            pos.quantity -= quantity

        tx = Transaction(
            user_id=user_id, ticker=ticker,
            transaction_type="SELL",
            quantity=quantity, price=price, total=total_revenue
        )
        db.session.add(tx)
        db.session.commit()

        return jsonify({
            "message"      : f"Vente de {quantity} {ticker} a {price:.2f} MAD",
            "total_revenue": round(total_revenue, 2),
            "pnl"          : round(pnl, 2),
            "new_balance"  : round(user.balance, 2),
        })

    @app.route("/api/portfolio/transactions")
    @jwt_required()
    def get_transactions():
        user_id = get_jwt_identity()
        txs     = Transaction.query.filter_by(
            user_id=user_id
        ).order_by(Transaction.date.desc()).limit(50).all()

        return jsonify([{
            "id"      : t.id,
            "ticker"  : t.ticker,
            "name"    : CASABLANCA_STOCKS.get(t.ticker, {}).get("name", t.ticker),
            "type"    : t.transaction_type,
            "quantity": t.quantity,
            "price"   : t.price,
            "total"   : t.total,
            "date"    : t.date.isoformat(),
        } for t in txs])

    @app.route("/api/portfolio/watchlist", methods=["GET"])
    @jwt_required()
    def get_watchlist():
        user_id = get_jwt_identity()
        items   = Watchlist.query.filter_by(user_id=user_id).all()
        result  = []
        for item in items:
            data           = MarketData.get_stock(item.ticker)
            data["name"]   = CASABLANCA_STOCKS.get(item.ticker, {}).get("name", item.ticker)
            data["sector"] = CASABLANCA_STOCKS.get(item.ticker, {}).get("sector", "")
            data["wid"]    = item.id
            result.append(data)
        return jsonify(result)

    @app.route("/api/portfolio/watchlist", methods=["POST"])
    @jwt_required()
    def add_watchlist():
        user_id = get_jwt_identity()
        data    = request.get_json()
        ticker  = data.get("ticker", "").upper()

        if ticker not in CASABLANCA_STOCKS:
            return jsonify({"error": "Action non trouvee"}), 404
        if Watchlist.query.filter_by(user_id=user_id, ticker=ticker).first():
            return jsonify({"error": "Deja dans la watchlist"}), 400

        item = Watchlist(user_id=user_id, ticker=ticker)
        db.session.add(item)
        db.session.commit()
        return jsonify({"message": f"{ticker} ajoute a la watchlist"})

    return app

# Point d'entree
application = create_app()

if __name__ == "__main__":
    application.run(debug=True, host="0.0.0.0", port=5000)
