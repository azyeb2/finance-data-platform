import pandas as pd
import streamlit as st

from src.database.connection import get_connection

st.set_page_config(page_title="Finans Dashboard", page_icon="📈", layout="wide")

st.title("Finans Veri Platformu Dashboard")
st.caption("Bu ekran ETL sonrası hazırlanan mart verilerini özetler.")

query = """
SELECT
    symbol,
    summary_date,
    avg_price,
    ma7,
    ma30,
    trend,
    daily_change_pct,
    insight
FROM mart.asset_prices
ORDER BY symbol, summary_date;
"""

connection = get_connection()
df = pd.read_sql(query, connection)
connection.close()

if df.empty:
    st.warning("Mart tablosunda veri bulunamadı.")
    st.stop()

st.subheader("Özet tablo")
latest = df.sort_values("summary_date").groupby("symbol", as_index=False).tail(1)
latest = latest[["symbol", "summary_date", "avg_price", "ma7", "ma30", "trend", "daily_change_pct"]]
latest = latest.sort_values("avg_price", ascending=False)

trend_labels = {
    "up": "Yükseliş",
    "down": "Düşüş",
    "flat": "Durağan",
}

latest["trend_tr"] = latest["trend"].map(trend_labels).fillna(latest["trend"])

asset_labels = {
    "GC=F": "Altın",
    "SI=F": "Gümüş",
    "PL=F": "Platin",
    "PA=F": "Paladyum",
    "HG=F": "Bakır",
    "EURTRY=X": "Euro",
    "GBPTRY=X": "Sterlin",
    "USDTRY=X": "Dolar",
}

latest["varlık_adı"] = latest["symbol"].map(asset_labels).fillna(latest["symbol"])
latest = latest[["varlık_adı", "summary_date", "avg_price", "ma7", "ma30", "trend_tr", "daily_change_pct"]]
latest.columns = [
    "Varlık",
    "Tarih",
    "Son Fiyat",
    "7 Günlük Ortalama",
    "30 Günlük Ortalama",
    "Trend",
    "Günlük Değişim %",
]

st.dataframe(latest, use_container_width=True)

st.subheader("Seçili varlık")
symbols = sorted(df["symbol"].unique().tolist())
options = [(asset_labels.get(symbol, symbol), symbol) for symbol in symbols]
selected_label, selected_symbol = st.selectbox("Varlık seç", options, format_func=lambda x: x[0])

filtered_df = df[df["symbol"] == selected_symbol].copy()
filtered_df["summary_date"] = pd.to_datetime(filtered_df["summary_date"])
filtered_df = filtered_df.sort_values("summary_date")

if not filtered_df.empty:
    latest_row = filtered_df.iloc[-1]
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Son Fiyat", f"{latest_row['avg_price']:.2f}")
    col2.metric("7 Günlük Ortalama", f"{latest_row['ma7']:.2f}")
    col3.metric("30 Günlük Ortalama", f"{latest_row['ma30']:.2f}")
    col4.metric("Trend", trend_labels.get(latest_row["trend"], latest_row["trend"]))

    st.metric("Günlük Değişim %", f"{latest_row['daily_change_pct']:.2f}")

    chart_data = filtered_df.set_index("summary_date")[["avg_price", "ma7", "ma30"]]
    st.line_chart(
        chart_data,
        color=["#2563eb", "#f59e0b", "#10b981"],
        use_container_width=True,
    )

    st.subheader("Özet açıklama")
    st.write(latest_row["insight"])
