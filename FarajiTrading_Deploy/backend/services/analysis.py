
import numpy as np
import pandas as pd

class TechnicalAnalysis:

    @staticmethod
    def calculate_sma(data, period=20):
        closes = [d["close"] for d in data]
        df = pd.Series(closes)
        sma = df.rolling(window=period).mean()
        return [round(v, 2) if not np.isnan(v) else None for v in sma]

    @staticmethod
    def calculate_rsi(data, period=14):
        closes = [d["close"] for d in data]
        df = pd.Series(closes)
        delta = df.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return [round(v, 2) if not np.isnan(v) else None for v in rsi]

    @staticmethod
    def calculate_macd(data, fast=12, slow=26, signal=9):
        closes = [d["close"] for d in data]
        df = pd.Series(closes)
        ema_fast = df.ewm(span=fast, adjust=False).mean()
        ema_slow = df.ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        return {
            "macd": [round(v, 2) if not np.isnan(v) else None for v in macd_line],
            "signal": [round(v, 2) if not np.isnan(v) else None for v in signal_line],
            "histogram": [round(v, 2) if not np.isnan(v) else None for v in histogram]
        }

    @staticmethod
    def calculate_bollinger_bands(data, period=20, std_dev=2):
        closes = [d["close"] for d in data]
        df = pd.Series(closes)
        sma = df.rolling(window=period).mean()
        std = df.rolling(window=period).std()
        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)
        return {
            "upper": [round(v, 2) if not np.isnan(v) else None for v in upper],
            "middle": [round(v, 2) if not np.isnan(v) else None for v in sma],
            "lower": [round(v, 2) if not np.isnan(v) else None for v in lower]
        }

    @staticmethod
    def get_signal(data):
        if len(data) < 30:
            return {"signal": "NEUTRE", "strength": 0, "details": []}
        analysis = TechnicalAnalysis()
        closes = [d["close"] for d in data]
        current_price = closes[-1]
        signals = []
        score = 0
        rsi = analysis.calculate_rsi(data)
        if rsi[-1]:
            if rsi[-1] < 30:
                signals.append({"indicator": "RSI", "signal": "ACHAT", "value": rsi[-1]})
                score += 2
            elif rsi[-1] > 70:
                signals.append({"indicator": "RSI", "signal": "VENTE", "value": rsi[-1]})
                score -= 2
            else:
                signals.append({"indicator": "RSI", "signal": "NEUTRE", "value": rsi[-1]})
        if score >= 3:
            overall = "ACHAT FORT"
        elif score >= 1:
            overall = "ACHAT"
        elif score <= -3:
            overall = "VENTE FORTE"
        elif score <= -1:
            overall = "VENTE"
        else:
            overall = "NEUTRE"
        return {"signal": overall, "strength": score, "details": signals, "price": current_price}
