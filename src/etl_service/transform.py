from src.database.connection import get_connection
from decimal import Decimal

OUNCE_TO_GRAM = Decimal("31.1034768")

def fetch_raw_data():
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute("""
   SELECT
       r.symbol,
       ref.display_name,
       r.asset_type,
       r.price,
       r.currency,
       ref.unit,
       r.collected_at
   FROM raw.asset_prices r
   JOIN reference.assets ref
   ON r.symbol = ref.symbol
   WHERE ref.active = TRUE;
   """)
    
    rows = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return rows


def create_asset_dict(row):
    
    asset = {
        "symbol": row[0],
        "display_name": row[1],
        "asset_type": row[2],
        "price": row[3],
        "currency": row[4],
        "unit": row[5],
        "collected_at": row[6]
    }
    
    return asset


def normalize_prices(assets, usd_try_rate):
    
    for asset in assets:
        asset["normalized_price"] = asset["price"]
        asset["normalized_currency"] = asset["currency"]
        asset["normalized_unit"] = asset["unit"]
        
        if asset["symbol"] in ['GC=F', 'SI=F', 'PL=F', 'PA=F']:
            price_try = asset["price"] * usd_try_rate
            price_per_gram = price_try / OUNCE_TO_GRAM
            
            asset["normalized_price"] = price_per_gram
            asset["normalized_currency"] = "TRY"
            asset["normalized_unit"] = "gram"
        
        elif asset["symbol"] == "HG=F":

            price_try = asset["price"] * usd_try_rate
            price_per_gram = price_try / Decimal("453.59237")

            asset["normalized_price"] = price_per_gram
            asset["normalized_currency"] = "TRY"
            asset["normalized_unit"] = "gram"
                        
            

    return assets


def transform_data():
    
    rows = fetch_raw_data() 
    assets = []
    
    for row in rows:
      asset = create_asset_dict(row)
      assets.append(asset)
      
    usd_try_rate = None
    for asset in assets:
      if asset["symbol"] == "USDTRY=X":
        usd_try_rate = asset["price"]
        break
        
    print(f"USD/TRY Rate: {usd_try_rate}")
    
    assets = normalize_prices(assets, usd_try_rate)
        
    return assets


def save_to_staging(assets):
    connection = get_connection()
    cursor = connection.cursor()

    for asset in assets:
            cursor.execute("""
    INSERT INTO staging.asset_prices (
        symbol,
        display_name,
        asset_type,
        normalized_price,
        normalized_currency,
        normalized_unit,
        collected_at
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (symbol, collected_at) DO NOTHING
    """, (
        asset["symbol"],
        asset["display_name"],
        asset["asset_type"],
        asset["normalized_price"],
        asset["normalized_currency"],
        asset["normalized_unit"],
        asset["collected_at"]
    ))

    connection.commit()

    cursor.close()
    connection.close()


    
if __name__ == "__main__":
    assets = transform_data()
    print(f"{len(assets)} assets transformed successfully.")
    
    save_to_staging(assets)
    print("Assets saved to staging table successfully.")
