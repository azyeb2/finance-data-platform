from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from src.database.connection import get_connection


def get_available_symbols():
    connection = get_connection()
    query = """
        SELECT DISTINCT symbol
        FROM mart.asset_prices
        ORDER BY symbol;
    """
    df = pd.read_sql(query, connection)
    connection.close()

    return df["symbol"].tolist()


def fetch_mart_data(symbols=None):
    connection = get_connection()

    if symbols is None:
        symbols = get_available_symbols()

    if isinstance(symbols, str):
        symbols = [symbols]

    placeholders = ", ".join(["%s"] * len(symbols))
    query = f"""
        SELECT
            symbol,
            summary_date,
            avg_price,
            ma7,
            ma30
        FROM mart.asset_prices
        WHERE symbol IN ({placeholders})
        ORDER BY symbol, summary_date;
    """

    df = pd.read_sql(query, connection, params=tuple(symbols))
    connection.close()

    return df


def build_dashboard_payload(symbols=None):
    df = fetch_mart_data(symbols or get_available_symbols())

    if df.empty:
        return {"symbols": [], "series": []}

    df["summary_date"] = pd.to_datetime(df["summary_date"])

    payload = []
    for symbol, group in df.groupby("symbol", sort=True):
        payload.append(
            {
                "name": symbol,
                "dates": [d.strftime("%Y-%m-%d") for d in group["summary_date"]],
                "avg_price": [round(float(value), 6) for value in group["avg_price"]],
                "ma7": [round(float(value), 6) for value in group["ma7"]],
                "ma30": [round(float(value), 6) for value in group["ma30"]],
            }
        )

    return {"symbols": [item["name"] for item in payload], "series": payload}


def create_chart(symbols=None, output_path=None, show=False):
    payload = build_dashboard_payload(symbols)

    if not payload["series"]:
        print("Veri bulunamadı.")
        return None

    fig, ax = plt.subplots(figsize=(12, 6))

    for series in payload["series"]:
        dates = pd.to_datetime(series["dates"])
        ax.plot(
            dates,
            series["avg_price"],
            label=f"{series['name']} - Avg"
        )

    ax.set_title("Asset Prices Across Symbols")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend(loc="best", fontsize="small")
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()

    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=150, bbox_inches="tight")
        print(f"Chart saved to {output_path}")

    if show:
        plt.show()

    plt.close(fig)
    return payload


if __name__ == "__main__":
    create_chart(None, output_path="output/asset_prices_dashboard.png", show=False)