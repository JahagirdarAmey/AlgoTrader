-- Create the trading database
CREATE DATABASE trading_analytics;

-- Connect to the database
--\c trading_analytics

-- Create schemas to organize our tables
CREATE SCHEMA trading;
CREATE SCHEMA config;
CREATE SCHEMA metrics;

-- Trading configuration table
CREATE TABLE config.trading_strategies (
    strategy_id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NOT NULL,
    initial_capital DECIMAL(15,2) NOT NULL,
    ema_short INTEGER NOT NULL,
    ema_long INTEGER NOT NULL,
    volume_threshold DECIMAL(15,2) NOT NULL,
    stop_loss DECIMAL(5,4) NOT NULL,
    take_profit DECIMAL(5,4) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Price and indicators data
CREATE TABLE trading.market_data (
    id SERIAL PRIMARY KEY,
    strategy_id INTEGER REFERENCES config.trading_strategies(strategy_id),
    timestamp TIMESTAMP NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    price DECIMAL(15,2) NOT NULL,
    volume DECIMAL(15,2) NOT NULL,
    ema_short DECIMAL(15,2),
    ema_long DECIMAL(15,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (symbol, timestamp)
);

-- Trade signals and executions
CREATE TABLE trading.trades (
    trade_id SERIAL PRIMARY KEY,
    strategy_id INTEGER REFERENCES config.trading_strategies(strategy_id),
    symbol VARCHAR(20) NOT NULL,
    entry_date TIMESTAMP NOT NULL,
    exit_date TIMESTAMP,
    entry_price DECIMAL(15,2) NOT NULL,
    exit_price DECIMAL(15,2),
    position_size DECIMAL(15,2) NOT NULL,
    trade_type VARCHAR(4) NOT NULL CHECK (trade_type IN ('LONG', 'SHORT')),
    profit_loss DECIMAL(15,2),
    profit_loss_pct DECIMAL(8,4),
    status VARCHAR(10) DEFAULT 'OPEN' CHECK (status IN ('OPEN', 'CLOSED')),
    exit_reason VARCHAR(20) CHECK (exit_reason IN ('SIGNAL', 'STOP_LOSS', 'TAKE_PROFIT', 'MANUAL')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Portfolio performance tracking
CREATE TABLE metrics.portfolio_metrics (
    id SERIAL PRIMARY KEY,
    strategy_id INTEGER REFERENCES config.trading_strategies(strategy_id),
    timestamp TIMESTAMP NOT NULL,
    equity_value DECIMAL(15,2) NOT NULL,
    drawdown DECIMAL(8,4),
    drawdown_pct DECIMAL(8,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Daily performance metrics
CREATE TABLE metrics.daily_performance (
    id SERIAL PRIMARY KEY,
    strategy_id INTEGER REFERENCES config.trading_strategies(strategy_id),
    date DATE NOT NULL,
    starting_equity DECIMAL(15,2) NOT NULL,
    ending_equity DECIMAL(15,2) NOT NULL,
    daily_returns DECIMAL(8,4),
    daily_profit_loss DECIMAL(15,2),
    number_of_trades INTEGER,
    winning_trades INTEGER,
    losing_trades INTEGER,
    sharpe_ratio DECIMAL(8,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (strategy_id, date)
);

-- Create indexes for better query performance
CREATE INDEX idx_market_data_symbol_timestamp ON trading.market_data(symbol, timestamp);
CREATE INDEX idx_trades_symbol_dates ON trading.trades(symbol, entry_date, exit_date);
CREATE INDEX idx_portfolio_metrics_strategy_timestamp ON metrics.portfolio_metrics(strategy_id, timestamp);
CREATE INDEX idx_daily_performance_strategy_date ON metrics.daily_performance(strategy_id, date);

-- Create time-based partitioning for market_data table
--CREATE TABLE trading.market_data_y2024m01 PARTITION OF trading.market_data
--    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- Create a function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at columns
CREATE TRIGGER update_trading_strategies_updated_at
    BEFORE UPDATE ON config.trading_strategies
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_trades_updated_at
    BEFORE UPDATE ON trading.trades
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();