from ..data.data_loader import DataLoader
from ..signals.signal_generator import SignalGenerator
from ..trade_execution.trade_manager import TradeManager
from typing import Dict, List
import pandas as pd


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

    def run(self) -> Dict:
        """Run backtest and return results"""
        # Load data
        data = self.data_loader.fetch_data()

        # Generate signals
        signals = self.signal_generator.generate_signals(data)

        # Execute trades
        self.results = self.trade_manager.execute_trades(data, signals)

        return self.results

    def analyze_results(self) -> Dict:
        """Analyze backtest results"""
        if not self.results:
            return {}

        analysis = {
            'total_trades': len(self.results['trades']),
            'winning_trades': sum(1 for trade in self.results['trades']
                                  if trade['profit'] > 0),
            'total_profit': sum(trade['profit'] for trade in self.results['trades']),
            'max_drawdown': self._calculate_max_drawdown(),
            'sharpe_ratio': self._calculate_sharpe_ratio()
        }

        return analysis

    def _calculate_max_drawdown(self) -> float:
        """Calculate maximum drawdown from equity curve"""
        equity = pd.Series(self.results['equity_curve'])
        rolling_max = equity.expanding().max()
        drawdowns = equity / rolling_max - 1.0
        return drawdowns.min()

    def _calculate_sharpe_ratio(self) -> float:
        """Calculate Sharpe ratio of returns"""
        returns = pd.Series(self.results['equity_curve']).pct_change()
        return (returns.mean() / returns.std()) * (252 ** 0.5)  # Annualized
