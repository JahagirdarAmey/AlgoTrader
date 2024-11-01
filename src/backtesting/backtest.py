from config.config import TradingConfig
from ..data.data_loader import DataLoader
from ..signals.signal_generator import SignalGenerator
from ..trade_execution.trade_manager import TradeManager
from typing import Dict, List
import pandas as pd
import numpy as np


class Backtest:
    def __init__(self, config: 'TradingConfig'):
        self.config = config
        self.data_loader = DataLoader(
            config.symbol,
            config.start_date,
            config.end_date
        )
        self.signal_generator = SignalGenerator(config)
        self.trade_manager = TradeManager(config)
        self.results: Dict = {}

    def _ensure_list(self, data, length):
        """Helper method to ensure data is in list format"""
        if isinstance(data, pd.Series):
            return data.tolist()
        elif isinstance(data, np.ndarray):
            return data.tolist()
        elif isinstance(data, list):
            return data
        else:
            return [np.nan] * length

    def run(self) -> Dict:
        """Run backtest and return results"""
        # Load data
        data = self.data_loader.fetch_data()

        # Convert data to DataFrame if it's not already
        if isinstance(data, pd.DataFrame):
            df = data
        else:
            df = pd.DataFrame(data)

        # Generate signals
        signals = self.signal_generator.generate_signals(df)

        # Execute trades
        trade_results = self.trade_manager.execute_trades(df, signals)

        # Store trade results
        self.results = trade_results

        # Get data length
        data_length = len(df)

        # Format results for reporting system
        formatted_results = {
            'dates': df.index.tolist() if isinstance(df.index, pd.DatetimeIndex)
            else list(range(data_length)),
            'prices': self._ensure_list(df['Close'] if 'Close' in df else df.iloc[:, 0], data_length),
            'ema_short': self._ensure_list(df['EMA_short'] if 'EMA_short' in df else None, data_length),
            'ema_long': self._ensure_list(df['EMA_long'] if 'EMA_long' in df else None, data_length),
            'equity_curve': self.results.get('equity_curve', [self.config.initial_capital] * data_length),
            'buy_dates': [],
            'buy_prices': [],
            'sell_dates': [],
            'sell_prices': []
        }

        # Extract buy and sell points from trades
        if 'trades' in self.results:
            for trade in self.results['trades']:
                if trade.get('type') in ['buy', 'long']:
                    formatted_results['buy_dates'].append(trade.get('entry_time', 0))
                    formatted_results['buy_prices'].append(trade.get('entry_price', 0))
                if trade.get('type') in ['sell', 'short']:
                    formatted_results['sell_dates'].append(trade.get('exit_time', 0))
                    formatted_results['sell_prices'].append(trade.get('exit_price', 0))

        return formatted_results

    def analyze_results(self) -> Dict:
        """Analyze backtest results"""
        if not self.results or 'trades' not in self.results:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'total_profit': 0.0,
                'max_drawdown': 0.0,
                'sharpe_ratio': 0.0
            }

        trades = self.results.get('trades', [])

        analysis = {
            'total_trades': len(trades),
            'winning_trades': sum(1 for trade in trades
                                  if trade.get('profit', 0) > 0),
            'total_profit': sum(trade.get('profit', 0) for trade in trades),
            'max_drawdown': self._calculate_max_drawdown(),
            'sharpe_ratio': self._calculate_sharpe_ratio()
        }

        return analysis

    def _calculate_max_drawdown(self) -> float:
        """Calculate maximum drawdown from equity curve"""
        if not self.results.get('equity_curve'):
            return 0.0

        try:
            equity = pd.Series(self.results['equity_curve'])
            rolling_max = equity.expanding().max()
            drawdowns = equity / rolling_max - 1.0
            return float(drawdowns.min())
        except Exception as e:
            print(f"Error calculating max drawdown: {e}")
            return 0.0

    def _calculate_sharpe_ratio(self) -> float:
        """Calculate Sharpe ratio of returns"""
        if not self.results.get('equity_curve'):
            return 0.0

        try:
            returns = pd.Series(self.results['equity_curve']).pct_change()
            if returns.std() == 0:
                return 0.0
            return float((returns.mean() / returns.std()) * (252 ** 0.5))  # Annualized
        except Exception as e:
            print(f"Error calculating Sharpe ratio: {e}")
            return 0.0