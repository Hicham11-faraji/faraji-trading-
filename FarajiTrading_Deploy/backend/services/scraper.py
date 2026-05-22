
import random
from datetime import datetime, timedelta

class CasablancaScraper:

    def get_stock_data(self, ticker):
        return self._generate_realistic_data(ticker)

    def _generate_realistic_data(self, ticker):
        base_prices = {
            "IAM": 128.50, "ATW": 485.00, "BCP": 275.00, "BOA": 188.00,
            "CIH": 350.00, "CDM": 620.00, "TQM": 1180.00, "LHM": 1850.00,
            "MNG": 1450.00, "SMI": 1800.00, "CMA": 1700.00, "CSR": 195.00,
            "LES": 185.00, "GAZ": 4800.00, "ADH": 11.50, "HPS": 6200.00,
            "M2M": 580.00, "WAA": 4100.00, "SAH": 1250.00, "MDP": 285.00,
            "TMA": 1580.00, "SBM": 280.00, "ALM": 1400.00, "SNP": 780.00,
            "LBV": 4200.00, "AUT": 95.00, "RIS": 145.00,
            "MASI": 12850.00, "MADEX": 10450.00,
        }
        base = base_prices.get(ticker, 100.0)
        variation = round(random.uniform(-3.0, 3.0), 2)
        price = round(base * (1 + variation / 100), 2)
        open_price = round(base * (1 + random.uniform(-1.0, 1.0) / 100), 2)
        high = round(max(price, open_price) * (1 + random.uniform(0, 1.5) / 100), 2)
        low = round(min(price, open_price) * (1 - random.uniform(0, 1.5) / 100), 2)
        volume = random.randint(1000, 500000)

        return {
            "ticker": ticker,
            "price": price,
            "open": open_price,
            "high": high,
            "low": low,
            "close": price,
            "volume": volume,
            "variation": variation,
            "timestamp": datetime.now().isoformat()
        }

    def get_historical_data(self, ticker, days=365):
        base_prices = {
            "IAM": 128.50, "ATW": 485.00, "BCP": 275.00, "BOA": 188.00,
            "CIH": 350.00, "LHM": 1850.00, "MNG": 1450.00, "CSR": 195.00,
            "HPS": 6200.00, "LBV": 4200.00, "WAA": 4100.00, "TQM": 1180.00,
            "MASI": 12850.00, "MADEX": 10450.00,
        }
        base = base_prices.get(ticker, 100.0)
        data = []
        current_price = base * 0.85

        for i in range(days):
            date = datetime.now() - timedelta(days=days - i)
            if date.weekday() >= 5:
                continue
            change = random.gauss(0.0005, 0.015)
            current_price = current_price * (1 + change)
            current_price = max(current_price, base * 0.5)

            open_price = round(current_price * (1 + random.uniform(-0.005, 0.005)), 2)
            close_price = round(current_price, 2)
            high_price = round(max(open_price, close_price) * (1 + random.uniform(0, 0.02)), 2)
            low_price = round(min(open_price, close_price) * (1 - random.uniform(0, 0.02)), 2)
            volume = random.randint(5000, 800000)

            data.append({
                "date": date.strftime("%Y-%m-%d"),
                "open": open_price,
                "high": high_price,
                "low": low_price,
                "close": close_price,
                "volume": volume
            })
        return data

    def get_market_summary(self):
        from config import CASABLANCA_STOCKS
        summary = []
        for ticker, info in CASABLANCA_STOCKS.items():
            data = self._generate_realistic_data(ticker)
            data["name"] = info["name"]
            data["sector"] = info["sector"]
            summary.append(data)
        return summary
