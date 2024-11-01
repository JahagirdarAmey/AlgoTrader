# tests/test_data/market_data_generator.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class MarketDataGenerator:
    @staticmethod
    def create_market_data(days=30, trend='flat', volatility='normal', include_gaps=False):
        """
        Create synthetic market data for testing

        Parameters:
        -----------
        days : int
            Number of trading days to generate
        trend : str
            'flat', 'up', or 'down'
        volatility : str
            'normal' or 'high'
        include_gaps : bool
            Whether to include missing data points

        Returns:
        --------
        pd.DataFrame
            Market data with OHLCV columns
        """
        dates = [datetime.now() - timedelta(days=x) for x in range(days)]

        # Generate base prices based on trend
        if trend == 'up':
            closes = [100 + i for i in range(days)]
        elif trend == 'down':
            closes = [100 - i for i in range(days)]
        else:
            closes = [100] * days

        # Add random noise based on volatility
        volatility_factor = 2 if volatility == 'high' else 1
        random_walk = np.random.normal(0, volatility_factor, days).cumsum()
        closes = np.array(closes) + random_walk

        data = {
            'Date': dates,
            'Open': closes - np.random.normal(0, volatility_factor, days),
            'High': closes + abs(np.random.normal(0, volatility_factor, days)),
            'Low': closes - abs(np.random.normal(0, volatility_factor, days)),
            'Close': closes,
            'Volume': np.random.normal(1000, 200, days).astype(int)
        }

        df = pd.DataFrame(data).set_index('Date')

        # Ensure High is highest and Low is lowest
        df['High'] = df[['Open', 'High', 'Close']].max(axis=1)
        df['Low'] = df[['Open', 'Low', 'Close']].min(axis=1)

        if include_gaps:
            # Randomly remove some data points
            mask = np.random.random(len(df)) > 0.1
            df.loc[~mask, ['Open', 'High', 'Low', 'Close']] = np.nan

        return df

    @staticmethod
    def create_specific_pattern(pattern_type, days=30):
        """
        Create specific market patterns for testing

        Parameters:
        -----------
        pattern_type : str
            'double_top', 'head_shoulders', etc.
        days : int
            Number of days for the pattern

        Returns:
        --------
        pd.DataFrame
            Market data with the specified pattern
        """
        # Implementation for specific patterns can be added here
        pass