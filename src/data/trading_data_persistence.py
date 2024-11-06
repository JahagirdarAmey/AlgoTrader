import psycopg2
from psycopg2.extras import execute_batch
from datetime import datetime
import logging
import pandas as pd
from typing import Dict, List, Optional, Tuple

import psycopg2
from psycopg2.extras import execute_batch
from datetime import datetime
import logging
import pandas as pd
from dateutil.relativedelta import relativedelta
from typing import Dict, List, Optional, Tuple


class TradingDataPersistence:
    def __init__(self, db_config: Dict[str, str]):
        """
        Initialize database connection.

        Args:
            db_config: Dictionary containing database connection parameters
                {
                    'dbname': 'trading_analytics',
                    'user': 'trading_user',
                    'password': 'your_secure_password',
                    'host': 'localhost',
                    'port': '5432'
                }
        """
        self.db_config = db_config
        self.setup_logging()
        self.conn = None
        self.connect()

    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            self.logger.info("Successfully connected to the database")
        except Exception as e:
            self.logger.error(f"Error connecting to database: {str(e)}")
            raise

    def ensure_partitions_exist(self, start_date: datetime, end_date: datetime):
        """
        Ensure all required partitions exist for the date range.

        Args:
            start_date: Start date for data
            end_date: End date for data
        """
        try:
            current = start_date.replace(day=1)  # Start at beginning of month
            while current <= end_date:
                partition_name = f"market_data_y{current.year}m{current.month:02d}"
                next_month = current + relativedelta(months=1)

                query = f"""
                   CREATE TABLE IF NOT EXISTS trading.{partition_name}
                   PARTITION OF trading.market_data
                   FOR VALUES FROM ('{current.strftime('%Y-%m-01')}')
                   TO ('{next_month.strftime('%Y-%m-01')}');
                   """

                with self.conn.cursor() as cur:
                    cur.execute(query)

                self.logger.info(f"Ensured partition exists for {current.strftime('%Y-%m')}")
                current = next_month

            self.conn.commit()
            self.logger.info("All required partitions verified/created")

        except Exception as e:
            self.conn.rollback()
            self.logger.error(f"Error ensuring partitions exist: {str(e)}")
            raise

    def save_market_data(self, strategy_id: int, results: Dict, config: Dict):
        """
        Save market data including prices and indicators using upsert logic.

        Args:
            strategy_id: The strategy_id from trading_strategies table
            results: Dictionary containing market data
            config: Trading configuration containing dates and symbol
        """
        try:
            # Ensure partitions exist before inserting data
            dates = pd.to_datetime(results['dates'])
            self.ensure_partitions_exist(
                start_date=dates.min(),
                end_date=dates.max()
            )

            with self.conn.cursor() as cur:
                # Using ON CONFLICT DO UPDATE for upsert operation
                query = """
                    INSERT INTO trading.market_data 
                    (strategy_id, timestamp, symbol, price, volume, ema_short, ema_long)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (symbol, timestamp)
                    DO UPDATE SET
                        strategy_id = EXCLUDED.strategy_id,
                        price = EXCLUDED.price,
                        volume = EXCLUDED.volume,
                        ema_short = EXCLUDED.ema_short,
                        ema_long = EXCLUDED.ema_long;
                    """

                data = [
                    (strategy_id, date, config.symbol, price, volume, ema_s, ema_l)
                    for date, price, volume, ema_s, ema_l in zip(
                        results['dates'],
                        results['prices'],
                        results.get('volumes', [0] * len(results['dates'])),
                        results.get('ema_short', [None] * len(results['dates'])),
                        results.get('ema_long', [None] * len(results['dates']))
                    )
                ]

                # Process in smaller batches to handle large datasets more efficiently
                batch_size = 1000
                for i in range(0, len(data), batch_size):
                    batch = data[i:i + batch_size]
                    execute_batch(cur, query, batch, page_size=batch_size)
                    self.conn.commit()
                    self.logger.info(f"Processed batch of {len(batch)} market data records")

                self.logger.info(f"Successfully saved/updated {len(data)} market data records")

        except Exception as e:
            self.conn.rollback()
            self.logger.error(f"Error saving market data: {str(e)}")
            raise

    def save_trading_strategy(self, config) -> int:
        """
        Save trading strategy configuration and return the strategy_id.
        If symbol already exists, update the existing strategy.

        Args:
            config: TradingConfig object containing strategy parameters

        Returns:
            int: The strategy_id of the inserted/updated record
        """
        try:
            with self.conn.cursor() as cur:
                # First try to get existing strategy_id
                cur.execute("""
                    SELECT strategy_id FROM config.trading_strategies 
                    WHERE symbol = %s
                    ORDER BY created_at DESC 
                    LIMIT 1
                """, (config.symbol,))

                result = cur.fetchone()

                if result:
                    # Update existing strategy
                    strategy_id = result[0]
                    query = """
                    UPDATE config.trading_strategies 
                    SET start_date = %s,
                        end_date = %s,
                        initial_capital = %s,
                        ema_short = %s,
                        ema_long = %s,
                        volume_threshold = %s,
                        stop_loss = %s,
                        take_profit = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE strategy_id = %s
                    """
                    cur.execute(query, (
                        config.start_date,
                        config.end_date,
                        config.initial_capital,
                        config.ema_short,
                        config.ema_long,
                        config.volume_threshold,
                        config.stop_loss,
                        config.take_profit,
                        strategy_id
                    ))
                    self.logger.info(f"Updated existing trading strategy with ID: {strategy_id}")
                else:
                    # Insert new strategy
                    query = """
                    INSERT INTO config.trading_strategies 
                    (symbol, start_date, end_date, initial_capital, ema_short, 
                    ema_long, volume_threshold, stop_loss, take_profit)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING strategy_id;
                    """
                    cur.execute(query, (
                        config.symbol,
                        config.start_date,
                        config.end_date,
                        config.initial_capital,
                        config.ema_short,
                        config.ema_long,
                        config.volume_threshold,
                        config.stop_loss,
                        config.take_profit
                    ))
                    strategy_id = cur.fetchone()[0]
                    self.logger.info(f"Created new trading strategy with ID: {strategy_id}")

                # Clean up old data for this symbol
                self._cleanup_old_data(strategy_id, config.symbol)

                self.conn.commit()
                return strategy_id

        except Exception as e:
            self.conn.rollback()
            self.logger.error(f"Error saving trading strategy: {str(e)}")
            raise

    def save_trades(self, strategy_id: int, trades: List[Dict]):
        """
        Save executed trades.

        Args:
            strategy_id: The strategy_id from trading_strategies table
            trades: List of trade dictionaries
        """
        try:
            with self.conn.cursor() as cur:
                query = """
                INSERT INTO trading.trades 
                (strategy_id, symbol, entry_date, exit_date, entry_price, 
                exit_price, position_size, trade_type, profit_loss, 
                profit_loss_pct, status, exit_reason)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                data = [
                    (strategy_id, trade['symbol'], trade['entry_date'],
                     trade.get('exit_date'), trade['entry_price'],
                     trade.get('exit_price'), trade['position_size'],
                     trade['trade_type'], trade.get('profit_loss'),
                     trade.get('profit_loss_pct'),
                     'CLOSED' if trade.get('exit_date') else 'OPEN',
                     trade.get('exit_reason'))
                    for trade in trades
                ]
                execute_batch(cur, query, data)
                self.conn.commit()
                self.logger.info(f"Saved {len(trades)} trades")
        except Exception as e:
            self.conn.rollback()
            self.logger.error(f"Error saving trades: {str(e)}")
            raise

    def save_portfolio_metrics(self, strategy_id: int, metrics: Dict):
        """
        Save portfolio metrics including equity curve and drawdown.

        Args:
            strategy_id: The strategy_id from trading_strategies table
            metrics: Dictionary containing portfolio metrics
        """
        try:
            with self.conn.cursor() as cur:
                query = """
                INSERT INTO metrics.portfolio_metrics 
                (strategy_id, timestamp, equity_value, drawdown, drawdown_pct)
                VALUES (%s, %s, %s, %s, %s)
                """
                data = [
                    (strategy_id, date, equity, dd, dd_pct)
                    for date, equity, dd, dd_pct in zip(
                        metrics['dates'],
                        metrics['equity_curve'],
                        metrics.get('drawdown', [None] * len(metrics['dates'])),
                        metrics.get('drawdown_pct', [None] * len(metrics['dates']))
                    )
                ]
                execute_batch(cur, query, data, page_size=1000)
                self.conn.commit()
                self.logger.info(f"Saved {len(data)} portfolio metric records")
        except Exception as e:
            self.conn.rollback()
            self.logger.error(f"Error saving portfolio metrics: {str(e)}")
            raise

    def save_daily_performance(self, strategy_id: int, performance: Dict):
        """
        Save daily performance metrics.

        Args:
            strategy_id: The strategy_id from trading_strategies table
            performance: Dictionary containing daily performance metrics
        """
        try:
            with self.conn.cursor() as cur:
                query = """
                INSERT INTO metrics.daily_performance 
                (strategy_id, date, starting_equity, ending_equity, 
                daily_returns, daily_profit_loss, number_of_trades, 
                winning_trades, losing_trades, sharpe_ratio)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                data = [
                    (strategy_id, date, perf['starting_equity'],
                     perf['ending_equity'], perf['returns'],
                     perf['profit_loss'], perf['num_trades'],
                     perf['winning_trades'], perf['losing_trades'],
                     perf.get('sharpe_ratio'))
                    for date, perf in performance.items()
                ]
                execute_batch(cur, query, data)
                self.conn.commit()
                self.logger.info(f"Saved {len(data)} daily performance records")
        except Exception as e:
            self.conn.rollback()
            self.logger.error(f"Error saving daily performance: {str(e)}")
            raise

    def _cleanup_old_data(self, current_strategy_id: int, symbol: str):
        """
        Clean up old data for the given symbol, keeping data for the current strategy.

        Args:
            current_strategy_id: The current strategy_id to keep
            symbol: The trading symbol
        """
        try:
            with self.conn.cursor() as cur:
                # Instead of deleting market data, update it to the current strategy_id
                cur.execute("""
                    UPDATE trading.market_data 
                    SET strategy_id = %s
                    WHERE symbol = %s AND strategy_id != %s
                """, (current_strategy_id, symbol, current_strategy_id))

                # Delete other related data for old strategies
                tables = [
                    'trading.trades',
                    'metrics.portfolio_metrics',
                    'metrics.daily_performance'
                ]

                for table in tables:
                    cur.execute(f"""
                        DELETE FROM {table}
                        WHERE strategy_id IN (
                            SELECT strategy_id 
                            FROM config.trading_strategies 
                            WHERE symbol = %s AND strategy_id != %s
                        )
                    """, (symbol, current_strategy_id))

                # Delete old strategies
                cur.execute("""
                    DELETE FROM config.trading_strategies 
                    WHERE symbol = %s AND strategy_id != %s
                """, (symbol, current_strategy_id))

                self.logger.info(f"Cleaned up old data for symbol: {symbol}")

        except Exception as e:
            self.logger.error(f"Error cleaning up old data: {str(e)}")
            raise

    def diagnose_data_saving(self, config, results, analysis):
        """
        Diagnose issues with data saving process by checking data structure and contents.

        Args:
            config: Trading configuration object
            results: Trading results dictionary
            analysis: Trading analysis dictionary
        """
        self.logger.info("Starting data saving diagnosis...")

        # Check trades data
        if 'trades' not in results:
            self.logger.error("No trades data found in results dictionary")
        else:
            self.logger.info(f"Found {len(results['trades'])} trades")
            # Log sample trade for structure verification
            if results['trades']:
                self.logger.info(f"Sample trade structure: {results['trades'][0]}")

        # Check portfolio metrics data
        if 'equity_curve' not in results:
            self.logger.error("No equity curve data found in results")
        else:
            self.logger.info(f"Found equity curve data with {len(results['equity_curve'])} points")

        # Check daily performance data
        if 'daily_performance' not in analysis:
            self.logger.error("No daily performance data found in analysis")
        else:
            self.logger.info(f"Found daily performance data with {len(analysis['daily_performance'])} days")
            # Log sample daily performance for structure verification
            if analysis['daily_performance']:
                sample_date = list(analysis['daily_performance'].keys())[0]
                self.logger.info(f"Sample daily performance structure: {analysis['daily_performance'][sample_date]}")

        # Verify data structure matches database schema
        try:
            with self.conn.cursor() as cur:
                # Check if tables exist
                for table in ['trading.trades', 'metrics.portfolio_metrics', 'metrics.daily_performance']:
                    cur.execute(
                        f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = split_part(%s, '.', 1) AND table_name = split_part(%s, '.', 2))",
                        (table, table))
                    exists = cur.fetchone()[0]
                    if not exists:
                        self.logger.error(f"Table {table} does not exist in database")
                    else:
                        self.logger.info(f"Table {table} exists in database")
        except Exception as e:
            self.logger.error(f"Error checking database schema: {str(e)}")

    def persist_all_data(self, config, results, analysis) -> int:
        """
        Persist all trading data in a single transaction.

        Args:
            config: Trading configuration object
            results: Trading results dictionary
            analysis: Trading analysis dictionary

        Returns:
            int: The strategy_id of the saved data
        """
        try:
            # Run diagnostics first
            self.diagnose_data_saving(config, results, analysis)

            strategy_id = self.save_trading_strategy(config)
            self.save_market_data(strategy_id, results, config)

            if 'trades' in results:
                if not results['trades']:
                    self.logger.warning("Trades list is empty")
                else:
                    self.save_trades(strategy_id, results['trades'])
            else:
                self.logger.warning("No trades data found in results")

            if 'equity_curve' in results:
                metrics_data = {
                    'dates': results['dates'],
                    'equity_curve': results['equity_curve'],
                    'drawdown': analysis.get('drawdown_series', []),
                    'drawdown_pct': analysis.get('drawdown_pct_series', [])
                }
                self.save_portfolio_metrics(strategy_id, metrics_data)
            else:
                self.logger.warning("No equity curve data found in results")

            if 'daily_performance' in analysis:
                if not analysis['daily_performance']:
                    self.logger.warning("Daily performance dictionary is empty")
                else:
                    self.save_daily_performance(strategy_id, analysis['daily_performance'])
            else:
                self.logger.warning("No daily performance data found in analysis")

            self.logger.info(f"Successfully persisted all available trading data for strategy {strategy_id}")
            return strategy_id

        except Exception as e:
            self.logger.error(f"Error persisting trading data: {str(e)}")
            raise
0
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.logger.info("Database connection closed")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()