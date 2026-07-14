import json
import yfinance as yf
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

assets = [
    {"symbol": "USDTRY=X", "asset_type": "currency"},
    {"symbol": "EURTRY=X", "asset_type": "currency"},
    {"symbol": "GBPTRY=X", "asset_type": "currency"},

    {"symbol": "GC=F", "asset_type": "metal"},
    {"symbol": "SI=F", "asset_type": "metal"},
    {"symbol": "PL=F", "asset_type": "metal"},
    {"symbol": "PA=F", "asset_type": "metal"},
    {"symbol": "HG=F", "asset_type": "metal"},
]


def get_market_data():

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
