from config.config import TradingConfig
from src.backtesting.backtest import Backtest
from src.reporting.trading_report import TradingReport


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
        'pivot_threshold': 0.001
    }

    config = TradingConfig.from_dict(config_dict)

    # Run backtest
    backtest = Backtest(config)
    results = backtest.run()
    analysis = backtest.analyze_results()

    # Generate report
    report = TradingReport(config, results, analysis)
    report_file = report.generate_report()

    print(f"\nReport generated successfully: {report_file}")


if __name__ == "__main__":
    main()