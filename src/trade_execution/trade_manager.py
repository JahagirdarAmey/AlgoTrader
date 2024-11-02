from typing import Dict, List, Optional
import pandas as pd

from config.config import TradingConfig


class TradeManager:
    def __init__(self, config: 'TradingConfig'):
        self.config = config
        self.current_position: Optional[Dict] = None
        self.trades: List[Dict] = []
        self.equity_curve: List[float] = []

    def execute_trades(self, data: pd.DataFrame, signals: pd.DataFrame) -> Dict:
        """Execute trades based on signals"""
        equity = self.config.initial_capital
        self.equity_curve = [equity]

        for i in range(len(data)):
            if self.current_position is None:
                # Check for entry
                if signals['signal'].iloc[i] == 1:
                    self._enter_trade(
                        data.index[i],
                        data['Close'].iloc[i]
                    )
            else:
                # Check for exit
                if self._should_exit(
                        data['Close'].iloc[i],
                        self.current_position['entry_price']
                ):
                    profit = self._exit_trade(
                        data.index[i],
                        data['Close'].iloc[i]
                    )
                    equity += profit

            self.equity_curve.append(equity)

        return {
            'trades': self.trades,
            'equity_curve': self.equity_curve
        }

    def _enter_trade(self, date: pd.Timestamp, price: float):
        """Enter a new trade"""
        self.current_position = {
            'entry_date': date,
            'entry_price': price,
            'stop_loss': price * (1 - self.config.stop_loss),
            'take_profit': price * (1 + self.config.take_profit)
        }

    def _should_exit(self, current_price: float, entry_price: float) -> bool:
        """Check if we should exit the current position"""
        if self.current_position is None:
            return False

        return (
                current_price <= self.current_position['stop_loss'] or
                current_price >= self.current_position['take_profit']
        )

    def _exit_trade(self, date: pd.Timestamp, price: float) -> float:
        """Exit the current trade and return profit/loss"""
        if self.current_position is None:
            return 0.0

        profit = price - self.current_position['entry_price']

        self.trades.append({
            'entry_date': self.current_position['entry_date'],
            'entry_price': self.current_position['entry_price'],
            'exit_date': date,
            'exit_price': price,
            'profit': profit
        })

        self.current_position = None
        return profit