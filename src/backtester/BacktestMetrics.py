import numpy as np
import pandas as pd


class BacktestMetrics:
    """Calculates various performance metrics for the backtest"""

    @staticmethod
    def calculate_returns_metrics(portfolio_values):
        """Calculate return-based metrics"""
        returns = pd.Series(portfolio_values).pct_change()

        metrics = {
            'Total Return (%)': ((portfolio_values[-1] / portfolio_values[0]) - 1) * 100,
            'Annualized Return (%)': (((portfolio_values[-1] / portfolio_values[0]) ** (252 / len(returns))) - 1) * 100,
            'Daily Volatility (%)': returns.std() * 100,
            'Annualized Volatility (%)': returns.std() * np.sqrt(252) * 100,
            'Sharpe Ratio': (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() != 0 else 0,
            'Sortino Ratio': (returns.mean() / returns[returns < 0].std()) * np.sqrt(252) if len(
                returns[returns < 0]) > 0 else 0
        }
        return metrics

    @staticmethod
    def calculate_drawdown_metrics(portfolio_values):
        """Calculate drawdown-related metrics"""
        values = pd.Series(portfolio_values)
        rolling_max = values.expanding().max()
        drawdowns = values / rolling_max - 1

        metrics = {
            'Maximum Drawdown (%)': drawdowns.min() * 100,
            'Average Drawdown (%)': drawdowns[drawdowns < 0].mean() * 100 if len(drawdowns[drawdowns < 0]) > 0 else 0,
            'Drawdown Duration (days)': len(drawdowns[drawdowns < 0])
        }
        return metrics

    @staticmethod
    def calculate_trade_metrics(trades_df):
        """Calculate trade-related metrics"""
        if len(trades_df) == 0:
            return {}

        buy_trades = trades_df[trades_df['type'] == 'buy']
        sell_trades = trades_df[trades_df['type'] == 'sell']

        if len(buy_trades) == 0 or len(sell_trades) == 0:
            return {}

        metrics = {
            'Total Trades': len(trades_df),
            'Win Rate (%)': (len(sell_trades[sell_trades['price'] > buy_trades['price'].iloc[0]]) / len(
                sell_trades)) * 100,
            'Average Trade Duration (days)': (sell_trades['date'] - buy_trades['date'].iloc[0]).mean().days,
            'Profit Factor': abs(sell_trades['price'].sum() / buy_trades['price'].sum()) if buy_trades[
                                                                                                'price'].sum() != 0 else 0
        }
        return metrics

    @staticmethod
    def predict_future_returns(current_value, annualized_return):
        """Calculate predicted future returns"""
        predictions = {
            '1 Month': current_value * (1 + annualized_return) ** (1 / 12),
            '12 Months': current_value * (1 + annualized_return),
            '10 Years': current_value * (1 + annualized_return) ** 10
        }
        return predictions