from src.database.connection import get_connection
import pandas as pd
import matplotlib.pyplot as plt


def fetch_mart_data(symbol):

    connection = get_connection()

    query = """
        SELECT
            summary_date,
            avg_price,
            ma7,
            ma30
        FROM mart.asset_prices
        WHERE symbol = %s
        ORDER BY summary_date;
    """

    df = pd.read_sql(
        query,
        connection,
        params=(symbol,)
    )

    connection.close()

    return df


def create_chart(symbol):

    df = fetch_mart_data(symbol)

    if df.empty:
        print("Veri bulunamadı.")
        return

    df["summary_date"] = pd.to_datetime(df["summary_date"])

    plt.figure(figsize=(10,5))

    plt.plot(
        df["summary_date"],
        df["avg_price"],
        label="Average Price"
    )

    plt.plot(
        df["summary_date"],
        df["ma7"],
        label="MA7"
    )

    plt.plot(
        df["summary_date"],
        df["ma30"],
        label="MA30"
    )

    plt.title(f"{symbol} Price Analysis")
    plt.xlabel("Date")
    plt.ylabel("Price")

    plt.legend()
    plt.grid()

    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.show()


if __name__ == "__main__":
    create_chart("GC=F")