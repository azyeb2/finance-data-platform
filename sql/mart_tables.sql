
DROP SCHEMA IF EXISTS mart CASCADE;
CREATE SCHEMA IF NOT EXISTS mart;

CREATE TABLE mart.asset_prices (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    display_name VARCHAR(50) NOT NULL,
    asset_type VARCHAR(20) NOT NULL,
    normalized_currency VARCHAR(10) NOT NULL,
    normalized_unit VARCHAR(20) NOT NULL,
    summary_date DATE NOT NULL,
    avg_price NUMERIC(18,6) NOT NULL,
    min_price NUMERIC(18,6) NOT NULL,
    max_price NUMERIC(18,6) NOT NULL,
    first_price NUMERIC(18,6) NOT NULL,
    last_price NUMERIC(18,6) NOT NULL,
    price_change NUMERIC(18,6) NOT NULL,
    range_price NUMERIC(18,6) NOT NULL,
    range_pct NUMERIC(12,6) NOT NULL,
    volatility NUMERIC(18,6) NOT NULL,
    trend VARCHAR(10) NOT NULL,
    daily_change_pct NUMERIC(12,6),
    ma7 NUMERIC(18,6) NOT NULL,
    ma30 NUMERIC(18,6) NOT NULL,
    price_count INTEGER NOT NULL,
    insight TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(symbol, summary_date)
);