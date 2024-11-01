import yfinance as yf
import pandas as pd
from typing import Optional

class DataLoader:
    def __init__(self, symbol: str, start_date: str, end_date: str):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.data: Optional[pd.DataFrame] = None

    def fetch_data(self) -> pd.DataFrame:
        """Fetch historical data from Yahoo Finance"""
        ticker = yf.Ticker(self.symbol)
        self.data = ticker.history(start=self.start_date, end=self.end_date)
        return self.data

    def get_latest_data(self) -> pd.DataFrame:
        """Get the most recent data point"""
        if self.data is None:
            self.fetch_data()
        return self.data.iloc[-1]