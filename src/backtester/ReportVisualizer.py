import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


class ReportVisualizer:
    """Creates various plots for the PDF report"""

    @staticmethod
    def create_equity_curve(portfolio_values, dates):
        plt.figure(figsize=(10, 6))
        plt.plot(dates, portfolio_values, label='Portfolio Value', color='blue')
        plt.title('Equity Curve')
        plt.xlabel('Date')
        plt.ylabel('Portfolio Value ($)')
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        return plt.gcf()

    @staticmethod
    def create_drawdown_chart(portfolio_values, dates):
        values = pd.Series(portfolio_values, index=dates)
        rolling_max = values.expanding().max()
        drawdowns = values / rolling_max - 1

        plt.figure(figsize=(10, 6))
        plt.fill_between(dates, drawdowns * 100, 0, color='red', alpha=0.3)
        plt.title('Drawdown Chart')
        plt.xlabel('Date')
        plt.ylabel('Drawdown (%)')
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        return plt.gcf()

    @staticmethod
    def create_monthly_returns_heatmap(portfolio_values, dates):
        returns = pd.Series(portfolio_values, index=dates).pct_change()
        monthly_returns = returns.resample('M').agg(lambda x: (1 + x).prod() - 1)
        monthly_returns = monthly_returns.to_frame()
        monthly_returns.columns = ['Returns']
        monthly_returns['Year'] = monthly_returns.index.year
        monthly_returns['Month'] = monthly_returns.index.month

        pivot_table = monthly_returns.pivot_table(
            index='Year',
            columns='Month',
            values='Returns'
        )

        plt.figure(figsize=(12, 8))
        sns.heatmap(pivot_table * 100,
                    annot=True,
                    fmt='.1f',
                    cmap='RdYlGn',
                    center=0)
        plt.title('Monthly Returns Heatmap (%)')
        plt.tight_layout()
        return plt.gcf()

    @staticmethod
    def create_trading_strategy_plot(signals_data, trades_df, start_date, end_date, duration_info):
        """Creates trading strategy visualization"""
        fig, ax = plt.subplots(figsize=(12, 6))

        # Plot price
        ax.plot(signals_data.index, signals_data['Close'], label='Price', color='blue')

        # Plot trades
        buy_trades = trades_df[trades_df['type'] == 'buy']
        sell_trades = trades_df[trades_df['type'] == 'sell']
        ax.scatter(buy_trades['date'], buy_trades['price'], color='green', label='Buy', marker='^', s=100)
        ax.scatter(sell_trades['date'], sell_trades['price'], color='red', label='Sell', marker='v', s=100)

        # Customize plot
        title = (f'Trading Strategy Simulation\n'
                 f'Start Date: {start_date}, End Date: {end_date}\n'
                 f'Total Duration: {duration_info}')
        ax.set_title(title)
        ax.set_xlabel('Date')
        ax.set_ylabel('Price')
        ax.legend()
        ax.grid(True)

        # Format x-axis
        weekdays = mdates.WeekdayLocator(byweekday=range(5))
        weekends = mdates.WeekdayLocator(byweekday=(5, 6))
        ax.xaxis.set_major_locator(weekdays)
        ax.xaxis.set_minor_locator(weekends)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

        # Rotate labels
        for label in ax.get_xticklabels(which='major'):
            label.set(rotation=45, horizontalalignment='right')

        plt.tight_layout()
        return plt.gcf()
