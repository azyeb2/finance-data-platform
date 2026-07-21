CREATE SCHEMA IF NOT EXISTS staging;

CREATE TABLE staging.asset_prices (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    display_name VARCHAR(50) NOT NULL,
    asset_type VARCHAR(20) NOT NULL,
    normalized_price NUMERIC(18,6) NOT NULL,
    normalized_currency VARCHAR(10) NOT NULL,
    normalized_unit VARCHAR(20) NOT NULL,
    collected_at TIMESTAMP NOT NULL,
    
    UNIQUE(symbol, collected_at)
    
);
