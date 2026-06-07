from __future__ import annotations

import sqlite3
import subprocess
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "business_kpi.db"


st.set_page_config(
    page_title="Business KPI Dashboard",
    page_icon="bar_chart",
    layout="wide",
)


def ensure_database() -> None:
    if DB_PATH.exists():
        return
    subprocess.run([sys.executable, str(BASE_DIR / "generate_data.py")], check=True)


def get_connection() -> sqlite3.Connection:
    ensure_database()
    return sqlite3.connect(DB_PATH)


@st.cache_data(show_spinner=False)
def load_filter_options() -> dict:
    with get_connection() as conn:
        min_max = conn.execute("SELECT MIN(order_date), MAX(order_date) FROM sales").fetchone()
        options = {
            "min_date": pd.to_datetime(min_max[0]).date(),
            "max_date": pd.to_datetime(min_max[1]).date(),
        }
        for column in ["region", "category", "channel", "customer_segment"]:
            rows = conn.execute(f"SELECT DISTINCT {column} FROM sales ORDER BY {column}").fetchall()
            options[column] = [row[0] for row in rows]
    return options


@st.cache_data(show_spinner=False)
def query_sales(
    start_date: str,
    end_date: str,
    regions: tuple[str, ...],
    categories: tuple[str, ...],
    channels: tuple[str, ...],
    segments: tuple[str, ...],
) -> pd.DataFrame:
    sql = """
        SELECT *
        FROM sales
        WHERE order_date BETWEEN ? AND ?
          AND region IN ({regions})
          AND category IN ({categories})
          AND channel IN ({channels})
          AND customer_segment IN ({segments})
    """.format(
        regions=",".join(["?"] * len(regions)),
        categories=",".join(["?"] * len(categories)),
        channels=",".join(["?"] * len(channels)),
        segments=",".join(["?"] * len(segments)),
    )
    params = [start_date, end_date, *regions, *categories, *channels, *segments]
    with get_connection() as conn:
        df = pd.read_sql_query(sql, conn, params=params, parse_dates=["order_date"])
    return df


def money(value: float) -> str:
    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    if abs(value) >= 1_000:
        return f"${value / 1_000:.1f}K"
    return f"${value:,.0f}"


def pct(value: float) -> str:
    return f"{value:.1f}%"


def make_monthly(df: pd.DataFrame) -> pd.DataFrame:
    monthly = (
        df.assign(month=df["order_date"].dt.to_period("M").dt.to_timestamp())
        .groupby("month", as_index=False)
        .agg(revenue=("revenue", "sum"), profit=("profit", "sum"), orders=("order_id", "nunique"))
    )
    return monthly


def sidebar_filters(options: dict) -> tuple:
    st.sidebar.header("Filters")
    date_range = st.sidebar.date_input(
        "Order date range",
        value=(options["min_date"], options["max_date"]),
        min_value=options["min_date"],
        max_value=options["max_date"],
    )
    if len(date_range) != 2:
        start_date, end_date = options["min_date"], options["max_date"]
    else:
        start_date, end_date = date_range

    regions = st.sidebar.multiselect("Region", options["region"], default=options["region"])
    categories = st.sidebar.multiselect("Category", options["category"], default=options["category"])
    channels = st.sidebar.multiselect("Channel", options["channel"], default=options["channel"])
    segments = st.sidebar.multiselect(
        "Customer segment",
        options["customer_segment"],
        default=options["customer_segment"],
    )

    return (
        start_date.isoformat(),
        end_date.isoformat(),
        tuple(regions or options["region"]),
        tuple(categories or options["category"]),
        tuple(channels or options["channel"]),
        tuple(segments or options["customer_segment"]),
    )


def render_dashboard(df: pd.DataFrame) -> None:
    st.title("Business KPI Dashboard")
    st.caption("SQL + Python + Streamlit dashboard using a generated pharmaceutical sales dataset.")

    if df.empty:
        st.warning("No rows match the selected filters.")
        return

    total_revenue = df["revenue"].sum()
    total_profit = df["profit"].sum()
    total_orders = df["order_id"].nunique()
    gross_margin = (total_profit / total_revenue * 100) if total_revenue else 0
    avg_order_value = total_revenue / total_orders if total_orders else 0

    kpi_cols = st.columns(5)
    kpi_cols[0].metric("Revenue", money(total_revenue))
    kpi_cols[1].metric("Profit", money(total_profit))
    kpi_cols[2].metric("Gross Margin", pct(gross_margin))
    kpi_cols[3].metric("Orders", f"{total_orders:,}")
    kpi_cols[4].metric("Avg Order Value", money(avg_order_value))

    monthly = make_monthly(df)
    left, right = st.columns([2, 1])
    with left:
        fig = px.line(
            monthly,
            x="month",
            y=["revenue", "profit"],
            markers=True,
            title="Monthly Revenue and Profit",
            labels={"value": "Amount", "month": "Month", "variable": "Metric"},
        )
        fig.update_layout(legend_title_text="", margin=dict(l=10, r=10, t=60, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with right:
        status = df.groupby("fulfillment_status", as_index=False).agg(orders=("order_id", "nunique"))
        fig = px.pie(status, names="fulfillment_status", values="orders", title="Fulfillment Status")
        fig.update_traces(textposition="inside", textinfo="percent+label")
        fig.update_layout(margin=dict(l=10, r=10, t=60, b=10))
        st.plotly_chart(fig, use_container_width=True)

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        by_region = df.groupby("region", as_index=False).agg(revenue=("revenue", "sum"))
        fig = px.bar(by_region, x="region", y="revenue", title="Revenue by Region")
        fig.update_layout(margin=dict(l=10, r=10, t=60, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        by_category = df.groupby("category", as_index=False).agg(profit=("profit", "sum"))
        fig = px.bar(by_category, x="category", y="profit", title="Profit by Category")
        fig.update_layout(margin=dict(l=10, r=10, t=60, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with col_c:
        by_channel = df.groupby("channel", as_index=False).agg(revenue=("revenue", "sum"))
        fig = px.bar(by_channel, x="channel", y="revenue", title="Revenue by Channel")
        fig.update_layout(margin=dict(l=10, r=10, t=60, b=10))
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top Products")
    product_table = (
        df.groupby(["category", "product"], as_index=False)
        .agg(
            revenue=("revenue", "sum"),
            profit=("profit", "sum"),
            units=("quantity", "sum"),
            orders=("order_id", "nunique"),
        )
        .sort_values("revenue", ascending=False)
        .head(10)
    )
    st.dataframe(
        product_table,
        use_container_width=True,
        column_config={
            "revenue": st.column_config.NumberColumn("Revenue", format="$%.2f"),
            "profit": st.column_config.NumberColumn("Profit", format="$%.2f"),
        },
        hide_index=True,
    )

    with st.expander("View raw SQL-backed sales records"):
        st.dataframe(df.sort_values("order_date", ascending=False).head(500), use_container_width=True)


def main() -> None:
    options = load_filter_options()
    filters = sidebar_filters(options)
    df = query_sales(*filters)
    render_dashboard(df)


if __name__ == "__main__":
    main()
