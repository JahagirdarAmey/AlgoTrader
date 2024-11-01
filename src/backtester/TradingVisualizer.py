import matplotlib.pyplot as plt
import matplotlib.dates as mdates


class TradingVisualizer:
    """Handles all visualization tasks"""

    @staticmethod
    def plot_trading_strategy(signals_data, trades_df, start_date, end_date, duration_info):
        fig, ax = plt.subplots(figsize=(15, 8))

        # Plot price
        ax.plot(signals_data.index, signals_data['Close'], label='Price')

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

        return fig