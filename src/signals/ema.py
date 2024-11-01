import pandas as pd

class EMACalculator:
    @staticmethod
    def calculate(data: pd.Series, period: int) -> pd.Series:
        """Calculate EMA for the given period"""
        return data.ewm(span=period, adjust=False).mean()

    @staticmethod
    def is_bullish_crossover(short_ema: float, long_ema: float) -> bool:
        """Check if short EMA crossed above long EMA"""
        return short_ema > long_ema