-- First, connect as a superuser (usually postgres) and drop the database if it exists
DROP DATABASE IF EXISTS trading_analytics;

-- Create fresh database
CREATE DATABASE trading_analytics;

-- Connect to the new database
\c trading_analytics

-- Drop schemas if they exist (this will cascade and drop all contained objects)
DROP SCHEMA IF EXISTS trading CASCADE;
DROP SCHEMA IF EXISTS config CASCADE;
DROP SCHEMA IF EXISTS metrics CASCADE;

-- Create schemas
CREATE SCHEMA trading;
CREATE SCHEMA config;
CREATE SCHEMA metrics;

-- Create updated_at timestamp function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trading configuration table
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

-- Create trigger for trading_strategies
CREATE TRIGGER update_trading_strategies_updated_at
    BEFORE UPDATE ON config.trading_strategies
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create partitioned market_data table
CREATE TABLE trading.market_data (
    id SERIAL,
    strategy_id INTEGER REFERENCES config.trading_strategies(strategy_id),
    timestamp TIMESTAMP NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    price DECIMAL(15,2) NOT NULL,
    volume DECIMAL(15,2) NOT NULL,
    ema_short DECIMAL(15,2),
    ema_long DECIMAL(15,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (symbol, timestamp)
) PARTITION BY RANGE (timestamp);

-- Create initial partitions
CREATE TABLE trading.market_data_y2024m01 PARTITION OF trading.market_data
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE trading.market_data_y2024m02 PARTITION OF trading.market_data
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

CREATE TABLE trading.market_data_y2024m03 PARTITION OF trading.market_data
    FOR VALUES FROM ('2024-03-01') TO ('2024-04-01');

    -- First, create partitions for 2023 data
CREATE TABLE trading.market_data_y2023m01 PARTITION OF trading.market_data
    FOR VALUES FROM ('2023-01-01') TO ('2023-02-01');

CREATE TABLE trading.market_data_y2023m02 PARTITION OF trading.market_data
    FOR VALUES FROM ('2023-02-01') TO ('2023-03-01');

CREATE TABLE trading.market_data_y2023m03 PARTITION OF trading.market_data
    FOR VALUES FROM ('2023-03-01') TO ('2023-04-01');

CREATE TABLE trading.market_data_y2023m04 PARTITION OF trading.market_data
    FOR VALUES FROM ('2023-04-01') TO ('2023-05-01');

CREATE TABLE trading.market_data_y2023m05 PARTITION OF trading.market_data
    FOR VALUES FROM ('2023-05-01') TO ('2023-06-01');

CREATE TABLE trading.market_data_y2023m06 PARTITION OF trading.market_data
    FOR VALUES FROM ('2023-06-01') TO ('2023-07-01');

CREATE TABLE trading.market_data_y2023m07 PARTITION OF trading.market_data
    FOR VALUES FROM ('2023-07-01') TO ('2023-08-01');

CREATE TABLE trading.market_data_y2023m08 PARTITION OF trading.market_data
    FOR VALUES FROM ('2023-08-01') TO ('2023-09-01');

CREATE TABLE trading.market_data_y2023m09 PARTITION OF trading.market_data
    FOR VALUES FROM ('2023-09-01') TO ('2023-10-01');

CREATE TABLE trading.market_data_y2023m10 PARTITION OF trading.market_data
    FOR VALUES FROM ('2023-10-01') TO ('2023-11-01');

CREATE TABLE trading.market_data_y2023m11 PARTITION OF trading.market_data
    FOR VALUES FROM ('2023-11-01') TO ('2023-12-01');

CREATE TABLE trading.market_data_y2023m12 PARTITION OF trading.market_data
    FOR VALUES FROM ('2023-12-01') TO ('2024-01-01');

-- Modify the auto-partitioning function to be more robust
CREATE OR REPLACE FUNCTION trading.create_market_data_partition()
RETURNS TRIGGER AS $$
DECLARE
    partition_timestamp timestamp;
    partition_name text;
    start_date timestamp;
    end_date timestamp;
BEGIN
    -- Round down to the start of the month
    partition_timestamp := date_trunc('month', NEW.timestamp);

    -- Generate partition name
    partition_name := 'market_data_y' ||
                     to_char(partition_timestamp, 'YYYY') ||
                     'm' ||
                     lpad(to_char(partition_timestamp, 'MM'), 2, '0');

    start_date := partition_timestamp;
    end_date := start_date + interval '1 month';

    -- Check if partition exists
    IF NOT EXISTS (
        SELECT 1
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE c.relname = partition_name
        AND n.nspname = 'trading'
    ) THEN
        BEGIN
            EXECUTE format(
                'CREATE TABLE trading.%I PARTITION OF trading.market_data
                FOR VALUES FROM (%L) TO (%L)',
                partition_name,
                start_date,
                end_date
            );
            RAISE NOTICE 'Created new partition: trading.%', partition_name;
        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE 'Error creating partition: %', SQLERRM;
            -- Re-raise the error
            RAISE;
        END;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trades table
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

-- Create trigger for trades
CREATE TRIGGER update_trades_updated_at
    BEFORE UPDATE ON trading.trades
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create portfolio metrics table
CREATE TABLE metrics.portfolio_metrics (
    id SERIAL PRIMARY KEY,
    strategy_id INTEGER REFERENCES config.trading_strategies(strategy_id),
    timestamp TIMESTAMP NOT NULL,
    equity_value DECIMAL(15,2) NOT NULL,
    drawdown DECIMAL(8,4),
    drawdown_pct DECIMAL(8,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create daily performance table
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

-- Create auto-partitioning function
CREATE OR REPLACE FUNCTION trading.create_market_data_partition()
RETURNS TRIGGER AS $$
DECLARE
    partition_timestamp timestamp;
    partition_name text;
    start_date timestamp;
    end_date timestamp;
BEGIN
    partition_timestamp := date_trunc('month', NEW.timestamp);
    partition_name := 'market_data_y' ||
                     to_char(partition_timestamp, 'YYYY') ||
                     'm' ||
                     to_char(partition_timestamp, 'MM');

    start_date := date_trunc('month', partition_timestamp);
    end_date := start_date + interval '1 month';

    IF NOT EXISTS (
        SELECT 1
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE c.relname = partition_name
        AND n.nspname = 'trading'
    ) THEN
        EXECUTE format(
            'CREATE TABLE trading.%I PARTITION OF trading.market_data
            FOR VALUES FROM (%L) TO (%L)',
            partition_name,
            start_date,
            end_date
        );

        RAISE NOTICE 'Created new partition: trading.%', partition_name;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create auto-partitioning trigger
CREATE TRIGGER create_market_data_partition_trigger
    BEFORE INSERT ON trading.market_data
    FOR EACH ROW
    EXECUTE FUNCTION trading.create_market_data_partition();

-- Create indexes
CREATE INDEX idx_market_data_symbol_timestamp ON trading.market_data(symbol, timestamp);
CREATE INDEX idx_trades_symbol_dates ON trading.trades(symbol, entry_date, exit_date);
CREATE INDEX idx_portfolio_metrics_strategy_timestamp ON metrics.portfolio_metrics(strategy_id, timestamp);
CREATE INDEX idx_daily_performance_strategy_date ON metrics.daily_performance(strategy_id, date);

-- Create a trading application user (replace password with your secure password)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = 'trading_user') THEN
        CREATE USER trading_user WITH PASSWORD 'your_secure_password';
    END IF;
END
$$;

-- Grant privileges to the new user
GRANT USAGE ON SCHEMA trading, config, metrics TO trading_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA trading TO trading_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA config TO trading_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA metrics TO trading_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA trading TO trading_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA config TO trading_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA metrics TO trading_user;

-- Allow the user to create new partitions
GRANT CREATE ON SCHEMA trading TO trading_user;