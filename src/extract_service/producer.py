import json
import yfinance as yf
from kafka import KafkaProducer
from src.database.connection import get_connection

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

def get_assets():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT symbol, asset_type
        FROM reference.assets
    """)

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    assets = []

    for row in rows:

        assets.append(
            {
                "symbol": row[0],
                "asset_type": row[1]
            }
        )

    return assets


def get_market_data():

    assets = get_assets()
    market_data = []

    for asset in assets:
        asset_type = asset["asset_type"]
        ticker = yf.Ticker(asset["symbol"])
        info = ticker.info

        data = {
         "symbol": info["symbol"],
         "price": info["regularMarketPrice"],
         "currency": info["currency"],
         "asset_type": asset["asset_type"]
       }
       
        market_data.append(data)

    return market_data


market_data = get_market_data()

for data in market_data:
    producer.send("market_data_raw", value=data)

producer.flush()

print("Veriler Kafka'ya başarıyla gönderildi.")
