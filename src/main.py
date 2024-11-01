#!/usr/bin/env python3
"""
Main script for running backtesting simulations.
"""
import os
import sys
from datetime import datetime, timedelta
import logging
import matplotlib.pyplot as plt

from backtester import (
    Backtester,
    BacktestReporter,
    TradingVisualizer
)

# Configure logging

previous_dir = os.path.abspath(os.path.join(os.getcwd(), '..'))

logs_path = os.path.join(previous_dir, 'logs')

if not os.path.exists(logs_path):
    os.makedirs(logs_path)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(logs_path, 'backtest.log')),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def setup_backtester():
    """Initialize the backtester with configuration"""
    return Backtester()


def run_backtest(symbol: str, start_date: datetime, end_date: datetime):
    """
    Run the backtest simulation for a given symbol and time period

    Parameters:
    -----------
    symbol : str
        The stock symbol to backtest
    start_date : datetime
        Start date for the backtest
    end_date : datetime
        End date for the backtest

    Returns:
    --------
    dict
        Results of the backtest
    """
    try:
        backtester = setup_backtester()
        results = backtester.run_backtest(symbol, start_date, end_date)

        logger.info(f"Backtest completed successfully for {symbol}")
        return results

    except Exception as e:
        logger.error(f"Error running backtest: {e}")
        raise


def calculate_duration(start_date: datetime, end_date: datetime) -> str:
    """Calculate and format the duration of the backtest"""
    duration_days = (end_date - start_date).days
    duration_months = duration_days // 30
    duration_remainder = duration_days % 30

    return f"{duration_days} days (~{duration_months} months and {duration_remainder} days)"


def save_visualization(results: dict, duration_info: str, output_file: str = 'trading_strategy_simulation.png'):
    """Generate and save the trading strategy visualization"""
    try:
        fig = TradingVisualizer.plot_trading_strategy(
            results['signals_data'],
            results['trades_df'],
            results['signals_data'].index[0],
            results['signals_data'].index[-1],
            duration_info
        )

        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        logger.info(f"Visualization saved to {output_file}")
        return fig

    except Exception as e:
        logger.error(f"Error generating visualization: {e}")
        raise


def print_results(results: dict):
    """Print the backtest results summary"""
    print("\n=== Backtest Results ===")
    print(f"Total Trades: {results['total_trades']}")
    print(f"Final Portfolio Value: ${results['final_portfolio_value']:,.2f}")
    print(f"Total Return: {results['total_return']:.2f}%")
    print("=====================\n")


def main():
    """Main execution function"""
    try:
        # Configuration
        symbol = 'GOOGL'
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)

        logger.info(f"Starting backtest for {symbol} from {start_date} to {end_date}")

        # Run backtest
        results = run_backtest(symbol, start_date, end_date)

        # Calculate duration
        duration_info = calculate_duration(
            results['signals_data'].index[0],
            results['signals_data'].index[-1]
        )

        # Print results
        print_results(results)

        # Create and save visualization
        fig = save_visualization(results, duration_info)
        plt.show()

        # Generate report
        reporter = BacktestReporter(results)
        report_path = reporter.generate_report()
        logger.info(f"Report generated successfully: {report_path}")

    except Exception as e:
        logger.error(f"An error occurred in main execution: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()