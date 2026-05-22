
from flask import Blueprint, request, jsonify
from services.scraper import CasablancaScraper
from services.analysis import TechnicalAnalysis
from config import CASABLANCA_STOCKS

stocks_bp = Blueprint("stocks", __name__)
scraper = CasablancaScraper()
analysis = TechnicalAnalysis()

@stocks_bp.route("/list", methods=["GET"])
def list_stocks():
    stocks = []
    for ticker, info in CASABLANCA_STOCKS.items():
        data = scraper.get_stock_data(ticker)
        data["name"] = info["name"]
        data["sector"] = info["sector"]
        stocks.append(data)
    return jsonify(stocks)

@stocks_bp.route("/market-summary", methods=["GET"])
def market_summary():
    summary = scraper.get_market_summary()
    gainers = [s for s in summary if s.get("variation", 0) > 0]
    losers = [s for s in summary if s.get("variation", 0) < 0]
    return jsonify({
        "stocks": summary,
        "stats": {
            "total": len(summary),
            "gainers": len(gainers),
            "losers": len(losers),
            "top_gainer": max(summary, key=lambda x: x.get("variation", 0)) if summary else None,
            "top_loser": min(summary, key=lambda x: x.get("variation", 0)) if summary else None,
        }
    })

@stocks_bp.route("/<ticker>", methods=["GET"])
def get_stock(ticker):
    ticker = ticker.upper()
    if ticker not in CASABLANCA_STOCKS:
        return jsonify({"error": "Action non trouvée"}), 404
    data = scraper.get_stock_data(ticker)
    data["name"] = CASABLANCA_STOCKS[ticker]["name"]
    data["sector"] = CASABLANCA_STOCKS[ticker]["sector"]
    return jsonify(data)

@stocks_bp.route("/<ticker>/historical", methods=["GET"])
def get_historical(ticker):
    ticker = ticker.upper()
    days = request.args.get("days", 365, type=int)
    if ticker not in CASABLANCA_STOCKS:
        return jsonify({"error": "Action non trouvée"}), 404
    data = scraper.get_historical_data(ticker, days)
    return jsonify({"ticker": ticker, "name": CASABLANCA_STOCKS[ticker]["name"], "data": data})

@stocks_bp.route("/<ticker>/analysis", methods=["GET"])
def get_analysis(ticker):
    ticker = ticker.upper()
    if ticker not in CASABLANCA_STOCKS:
        return jsonify({"error": "Action non trouvée"}), 404
    historical = scraper.get_historical_data(ticker, 365)
    signal = analysis.get_signal(historical)
    return jsonify({"ticker": ticker, "name": CASABLANCA_STOCKS[ticker]["name"],
        "signal": signal, "dates": [d["date"] for d in historical]})

@stocks_bp.route("/sectors", methods=["GET"])
def get_sectors():
    sectors = {}
    for ticker, info in CASABLANCA_STOCKS.items():
        sector = info["sector"]
        if sector == "Indice":
            continue
        if sector not in sectors:
            sectors[sector] = {"stocks": [], "total_variation": 0, "count": 0}
        data = scraper.get_stock_data(ticker)
        data["name"] = info["name"]
        sectors[sector]["stocks"].append(data)
        sectors[sector]["total_variation"] += data.get("variation", 0)
        sectors[sector]["count"] += 1
    for sector in sectors:
        if sectors[sector]["count"] > 0:
            sectors[sector]["avg_variation"] = round(
                sectors[sector]["total_variation"] / sectors[sector]["count"], 2)
    return jsonify(sectors)

@stocks_bp.route("/search", methods=["GET"])
def search_stocks():
    query = request.args.get("q", "").upper().strip()
    if not query:
        return jsonify([])
    results = []
    for ticker, info in CASABLANCA_STOCKS.items():
        if query in ticker or query.lower() in info["name"].lower():
            data = scraper.get_stock_data(ticker)
            data["name"] = info["name"]
            data["sector"] = info["sector"]
            results.append(data)
    return jsonify(results)
