CREATE SCHEMA IF NOT EXISTS raw;

CREATE TABLE IF NOT EXISTS raw.asset_prices (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    price NUMERIC(18,6) NOT NULL,
    currency VARCHAR(10) NOT NULL,
    collected_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    asset_type VARCHAR(20) NOT NULL,

    UNIQUE(symbol, collected_at)
); 
