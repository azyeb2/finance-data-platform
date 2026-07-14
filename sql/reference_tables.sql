CREATE SCHEMA IF NOT EXISTS reference;

CREATE TABLE IF NOT EXISTS reference.assets (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL UNIQUE,
    display_name VARCHAR(50) NOT NULL,
    asset_type VARCHAR(20) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    active BOOLEAN DEFAULT TRUE
);

INSERT INTO reference.assets
(symbol, display_name, asset_type, unit)
VALUES
('USDTRY=X', 'US Dollar', 'currency', 'unit'),
('EURTRY=X', 'Euro', 'currency', 'unit'),
('GBPTRY=X', 'British Pound', 'currency', 'unit'),
('GC=F', 'Gold', 'metal', 'ounce'),
('SI=F', 'Silver', 'metal', 'ounce'),
('PL=F', 'Platinum', 'metal', 'ounce'),
('PA=F', 'Palladium', 'metal', 'ounce'),
('HG=F', 'Copper', 'metal', 'pound');