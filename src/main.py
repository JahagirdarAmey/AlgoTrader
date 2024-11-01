from config.config import TradingConfig
from src.backtesting.backtest import Backtest


def main():
    # Enhanced configuration with pivot threshold
    config_dict = {
        'symbol': 'AAPL',
        'start_date': '2023-01-01',
        'end_date': '2024-01-01',
        'initial_capital': 100000,
        'ema_short': 9,
        'ema_long': 20,
        'volume_threshold': 1.5,
        'stop_loss': 0.02,
        'take_profit': 0.03,
        'pivot_threshold': 0.001  # Threshold for proximity to pivot levels
    }

    config = TradingConfig.from_dict(config_dict)

    backtest = Backtest(config)
    results = backtest.run()

    # Analyze results
    analysis = backtest.analyze_results()

    # Print results
    print("Backtest Results:")
    print("-" * 20)
    print(f"Total Trades: {analysis['total_trades']}")
    print(f"Winning Trades: {analysis['winning_trades']}")
    print(f"Total Profit: ${analysis['total_profit']:.2f}")
    print(f"Max Drawdown: {analysis['max_drawdown']:.2%}")
    print(f"Sharpe Ratio: {analysis['sharpe_ratio']:.2f}")

if __name__ == "__main__":
    main()