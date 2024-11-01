import yfinance as yf
from datetime import datetime, timedelta
import picologging


class StockDataFetcher:
    logger = picologging.Logger("StockDataFetcher")

    @staticmethod
    def fetch_stock_data(symbol='GOOGL', start_date=None, end_date=None, interval='15m'):
        if start_date is None:
            start_date = datetime.now() - timedelta(days=30)
        if end_date is None:
            end_date = datetime.now()

        StockDataFetcher.logger.info(
            f"Fetching data for {symbol} from {start_date} to {end_date} with interval {interval}")

        try:
            stock = yf.Ticker(symbol)
            data = stock.history(start=start_date, end=end_date, interval=interval)

            if data.empty:
                StockDataFetcher.logger.warning(
                    f"No data found for {symbol} in the given period. Extending search period.")
                start_date = end_date - timedelta(days=60)
                data = stock.history(start=start_date, end=end_date, interval=interval)

            StockDataFetcher.logger.info(f"Data fetched successfully for {symbol}")
            return data if not data.empty else None
        except Exception as e:
            StockDataFetcher.logger.error(f"Error fetching data for {symbol}: {e}")
            return None
