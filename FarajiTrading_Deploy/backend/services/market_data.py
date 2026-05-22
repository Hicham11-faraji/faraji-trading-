
import random
from datetime import datetime, timedelta

class MarketData:
    """
    Service de données du marché
    Utilise des données simulées réalistes
    En production: remplacer par scraping réel
    """

    BASE_PRICES = {
        "ATW": 485.0,  "BCP": 275.0,  "BOA": 188.0,
        "CIH": 350.0,  "CDM": 620.0,  "IAM": 128.5,
        "TQM": 1180.0, "GAZ": 4800.0, "LHM": 1850.0,
        "CMA": 1700.0, "MNG": 1450.0, "SMI": 1800.0,
        "CSR": 195.0,  "LES": 185.0,  "DWY": 540.0,
        "SBM": 280.0,  "HPS": 6200.0, "M2M": 580.0,
        "DIS": 220.0,  "WAA": 4100.0, "SAH": 1250.0,
        "ADH": 11.5,   "ADI": 45.0,   "LBV": 4200.0,
        "AUT": 95.0,   "MDP": 285.0,  "CTM": 1100.0,
        "SLF": 820.0,  "MAB": 850.0,  "SNP": 780.0,
        "ALM": 1400.0, "NEX": 220.0,  "DHO": 35.0,
        "RIS": 145.0,  "PRO": 1900.0, "MASI": 12850.0,
    }

    @classmethod
    def get_stock(cls, ticker):
        base  = cls.BASE_PRICES.get(ticker, 100.0)
        var   = round(random.uniform(-3.0, 3.0), 2)
        price = round(base * (1 + var / 100), 2)
        open_ = round(base * (1 + random.uniform(-1, 1) / 100), 2)
        high  = round(max(price, open_) * (1 + random.uniform(0, 1.5) / 100), 2)
        low   = round(min(price, open_) * (1 - random.uniform(0, 1.5) / 100), 2)
        vol   = random.randint(1000, 500000)

        return {
            "ticker"    : ticker,
            "price"     : price,
            "open"      : open_,
            "high"      : high,
            "low"       : low,
            "close"     : price,
            "volume"    : vol,
            "variation" : var,
            "timestamp" : datetime.now().isoformat(),
        }

    @classmethod
    def get_historical(cls, ticker, days=180):
        base    = cls.BASE_PRICES.get(ticker, 100.0)
        current = base * 0.88
        data    = []

        for i in range(days):
            date = datetime.now() - timedelta(days=days - i)
            if date.weekday() >= 5:
                continue

            import numpy as np
            change  = random.gauss(0.0005, 0.015)
            current = max(current * (1 + change), base * 0.4)
            open_   = round(current * (1 + random.uniform(-0.005, 0.005)), 2)
            close   = round(current, 2)
            high    = round(max(open_, close) * (1 + random.uniform(0, 0.02)), 2)
            low     = round(min(open_, close) * (1 - random.uniform(0, 0.02)), 2)

            data.append({
                "date"  : date.strftime("%Y-%m-%d"),
                "open"  : open_,
                "high"  : high,
                "low"   : low,
                "close" : close,
                "volume": random.randint(5000, 800000),
            })

        return data

    @classmethod
    def get_all_stocks(cls, stocks_config):
        result = []
        for ticker, info in stocks_config.items():
            data         = cls.get_stock(ticker)
            data["name"] = info["name"]
            data["sector"] = info["sector"]
            result.append(data)
        return result
