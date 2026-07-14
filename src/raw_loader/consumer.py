from kafka import KafkaConsumer
import json
from src.database.connection import get_connection

consumer = KafkaConsumer(

    "market_data_raw",
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda x: json.loads(x.decode("utf-8"))
)

connection = get_connection()
cursor = connection.cursor()



for message in consumer:

    data = message.value

    print(data)

    cursor.execute(
        """
        INSERT INTO raw.asset_prices
        (symbol, asset_type, price, currency)
        VALUES (%s, %s, %s, %s)
        """,
        (
            data["symbol"],
            data["asset_type"],
            data["price"],
            data["currency"],
            
        ),
    )

    connection.commit()