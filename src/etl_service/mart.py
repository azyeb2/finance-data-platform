from src.database.connection import get_connection
import pandas as pd


def fetch_staging_data():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            symbol,
            display_name,
            asset_type,
            normalized_price,
            normalized_currency,
            normalized_unit,
            collected_at
        FROM staging.asset_prices;
    """)

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    return rows


def generate_insight(row):
    trend_words = {
        "up": "yükseliş eğiliminde",
        "down": "düşüş eğiliminde",
        "flat": "durağan"
    }

    trend_text = trend_words.get(row["trend"], "stabil")
    currency = row["normalized_currency"]
    unit = row["normalized_unit"]

    return (
        f"{row['summary_date']} için {row['display_name']} ({row['symbol']}), "
        f"günde ortalama {row['avg_price']:.2f} {currency}/{unit} değerine sahip oldu. "
        f"Açılış ile kapanış arasındaki fark {row['price_change']:.2f} {currency} olarak gerçekleşti, "
        f"bu da % {row['daily_change_pct']:.2f} değişim demek. "
        f"Gün içi fiyat aralığı %{row['range_pct']:.2f} ve volatilite {row['volatility']:.6f}. "
        f"Genel olarak {trend_text} bir gün yaşandı."
    )


def calculate_daily_summary(rows):
    df = pd.DataFrame(
        rows,
        columns=[
            "symbol",
            "display_name",
            "asset_type",
            "normalized_price",
            "normalized_currency",
            "normalized_unit",
            "collected_at"
        ]
    )

    if df.empty:
        return pd.DataFrame()

    df["collected_at"] = pd.to_datetime(df["collected_at"])
    df["normalized_price"] = df["normalized_price"].astype(float)
    df["summary_date"] = df["collected_at"].dt.date
    df = df.sort_values(["symbol", "summary_date", "collected_at"])

    summary = (
        df.groupby(
            [
                "symbol",
                "display_name",
                "asset_type",
                "normalized_currency",
                "normalized_unit",
                "summary_date"
            ]
        )
        .agg(
            avg_price=("normalized_price", "mean"),
            min_price=("normalized_price", "min"),
            max_price=("normalized_price", "max"),
            first_price=("normalized_price", "first"),
            last_price=("normalized_price", "last"),
            price_count=("normalized_price", "count"),
            volatility=("normalized_price", lambda s: float(s.std(ddof=0)) if len(s) > 1 else 0.0)
        )
        .reset_index()
    )

    summary["price_change"] = (summary["last_price"] - summary["first_price"]).round(6)
    summary["range_price"] = (summary["max_price"] - summary["min_price"]).round(6)
    summary["range_pct"] = (
        (summary["range_price"] / summary["min_price"] * 100)
    ).round(6)
    summary["daily_change_pct"] = (
        (summary["last_price"] - summary["first_price"]) / summary["first_price"] * 100
    ).round(6)

    summary["trend"] = summary["daily_change_pct"].apply(
        lambda x: "up" if x > 0.5 else ("down" if x < -0.5 else "flat")
    )

    summary = summary.sort_values(["symbol", "summary_date"]).reset_index(drop=True)
    summary["ma7"] = (
        summary.groupby("symbol")["avg_price"]
        .transform(lambda s: s.rolling(window=7, min_periods=1).mean())
        .round(6)
    )
    summary["ma30"] = (
        summary.groupby("symbol")["avg_price"]
        .transform(lambda s: s.rolling(window=30, min_periods=1).mean())
        .round(6)
    )

    summary["insight"] = summary.apply(generate_insight, axis=1)

    summary = summary.loc[
        :,
        [
            "symbol",
            "display_name",
            "asset_type",
            "normalized_currency",
            "normalized_unit",
            "summary_date",
            "avg_price",
            "min_price",
            "max_price",
            "first_price",
            "last_price",
            "price_change",
            "range_price",
            "range_pct",
            "volatility",
            "trend",
            "daily_change_pct",
            "ma7",
            "ma30",
            "price_count",
            "insight"
        ],
    ]

    return summary


def save_to_mart(summary_df):
    if summary_df.empty:
        return

    connection = get_connection()
    cursor = connection.cursor()

    insert_query = """
        INSERT INTO mart.asset_prices (
            symbol,
            display_name,
            asset_type,
            normalized_currency,
            normalized_unit,
            summary_date,
            avg_price,
            min_price,
            max_price,
            first_price,
            last_price,
            price_change,
            range_price,
            range_pct,
            volatility,
            trend,
            daily_change_pct,
            ma7,
            ma30,
            price_count,
            insight
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (symbol, summary_date) DO UPDATE SET
            display_name = EXCLUDED.display_name,
            asset_type = EXCLUDED.asset_type,
            normalized_currency = EXCLUDED.normalized_currency,
            normalized_unit = EXCLUDED.normalized_unit,
            avg_price = EXCLUDED.avg_price,
            min_price = EXCLUDED.min_price,
            max_price = EXCLUDED.max_price,
            first_price = EXCLUDED.first_price,
            last_price = EXCLUDED.last_price,
            price_change = EXCLUDED.price_change,
            range_price = EXCLUDED.range_price,
            range_pct = EXCLUDED.range_pct,
            volatility = EXCLUDED.volatility,
            trend = EXCLUDED.trend,
            daily_change_pct = EXCLUDED.daily_change_pct,
            ma7 = EXCLUDED.ma7,
            ma30 = EXCLUDED.ma30,
            price_count = EXCLUDED.price_count,
            insight = EXCLUDED.insight;
    """

    for row in summary_df.itertuples(index=False, name=None):
        cursor.execute(insert_query, row)

    connection.commit()
    cursor.close()
    connection.close()


def mart_pipeline():
    rows = fetch_staging_data()
    summary_df = calculate_daily_summary(rows)

    if summary_df.empty:
        print("Staging tablosunda analiz edilecek veri yok.")
        return

    print("Mart özeti hesaplandı:")
    print(summary_df.head())

    save_to_mart(summary_df)
    print("Mart tablosuna kaydedildi.")


if __name__ == "__main__":
    mart_pipeline()
