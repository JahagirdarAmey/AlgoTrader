import pandas as pd
import numpy as np


class TechnicalAnalyzer:
    """Handles all technical indicator calculations"""

    @staticmethod
    def calculate_rsi(data, period=14):
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    @staticmethod
    def calculate_vwap(data):
        return (data['Close'] * data['Volume']).cumsum() / data['Volume'].cumsum()

    @staticmethod
    def calculate_atr(data, period=14):
        high_low = data['High'] - data['Low']
        high_close = np.abs(data['High'] - data['Close'].shift())
        low_close = np.abs(data['Low'] - data['Close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        return np.max(ranges, axis=1).rolling(window=period).mean()

    @staticmethod
    def calculate_bollinger_bands(data, period=20, std_dev=2):
        sma = data['Close'].rolling(window=period).mean()
        std = data['Close'].rolling(window=period).std()
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        return upper_band, lower_band

    def add_all_indicators(self, data):
        data = data.rename(columns=str.title)
        data['Rsi'] = self.calculate_rsi(data)
        data['Vwap'] = self.calculate_vwap(data)
        data['Atr'] = self.calculate_atr(data)
        data['Bb_Upper'], data['Bb_Lower'] = self.calculate_bollinger_bands(data)
        return data