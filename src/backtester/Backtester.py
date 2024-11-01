import pandas as pd

from backtester.PortfolioManager import PortfolioManager
from backtester.SignalGenerator import SignalGenerator
from backtester.StockDataFetcher import StockDataFetcher
from backtester.TechnicalAnalyzer import TechnicalAnalyzer
from backtester.TradingVisualizer import TradingVisualizer


class Backtester:

    def __init__(self, initial_capital=100000):
        self.data_fetcher = StockDataFetcher()
        self.technical_analyzer = TechnicalAnalyzer()
        self.signal_generator = SignalGenerator()
        self.portfolio_manager = PortfolioManager(initial_capital)
        self.visualizer = TradingVisualizer()

    def run_backtest(self, symbol='GOOGL', start_date=None, end_date=None):

        data = self.data_fetcher.fetch_stock_data(symbol, start_date, end_date)

        if data is None:
            raise ValueError("No data available for backtesting.")

        # Process data and generate signals
        processed_data = self.technical_analyzer.add_all_indicators(data)
        signals_data = self.signal_generator.generate_signals(processed_data)

        # Run simulation
        trades = []
        portfolio_values = []

        for i in range(1, len(signals_data)):
            current_price = signals_data['Close'].iloc[i]
            current_date = signals_data.index[i]
            current_signal = signals_data['Signal'].iloc[i]

            if current_signal == 1 and self.portfolio_manager.position == 0:
                position_size = self.portfolio_manager.calculate_position_size(
                    current_price,
                    signals_data['Atr'].iloc[i]
                )
                trade = self.portfolio_manager.enter_position(current_price, current_date, position_size)
                trades.append(trade)

            elif self.portfolio_manager.position > 0:
                if (current_price >= 1.02 * self.portfolio_manager.entry_price and
                        self.portfolio_manager.remaining_position == self.portfolio_manager.position):
                    trade = self.portfolio_manager.exit_partial_position(current_price, current_date, 0.50)
                    trades.append(trade)

                elif (current_price >= 1.025 * self.portfolio_manager.entry_price and
                      self.portfolio_manager.remaining_position == self.portfolio_manager.position * 0.50):
                    trade = self.portfolio_manager.exit_partial_position(current_price, current_date, 0.50)
                    trades.append(trade)

                elif self.portfolio_manager.remaining_position < self.portfolio_manager.position:
                    trade = self.portfolio_manager.exit_full_position(current_price, current_date)
                    trades.append(trade)

            portfolio_values.append({
                'date': current_date,
                'portfolio_value': self.portfolio_manager.get_portfolio_value(current_price)
            })

        return self.prepare_results(trades, portfolio_values, signals_data)

    def prepare_results(self, trades, portfolio_values, signals_data):
        trades_df = pd.DataFrame(trades)
        portfolio_df = pd.DataFrame(portfolio_values)

        results = {
            'trades_df': trades_df,
            'portfolio_df': portfolio_df,
            'signals_data': signals_data,
            'total_trades': len(trades),
            'final_portfolio_value': portfolio_df['portfolio_value'].iloc[-1],
            'total_return': (portfolio_df['portfolio_value'].iloc[-1] - self.portfolio_manager.capital) /
                            self.portfolio_manager.capital * 100
        }

        return results


