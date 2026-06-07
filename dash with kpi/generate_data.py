from __future__ import annotations

import random
import sqlite3
import csv
from datetime import date, timedelta
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
SQL_DIR = BASE_DIR / "sql"
CSV_PATH = DATA_DIR / "sales_dummy.csv"
DB_PATH = DATA_DIR / "business_kpi.db"


PRODUCT_CATALOG = {
    "Prescription": [
        ("CardioRelief 10mg", 38, 0.43),
        ("GlucoBalance XR", 52, 0.47),
        ("NeuroCalm Plus", 44, 0.45),
        ("RespiraClear", 31, 0.41),
    ],
    "OTC": [
        ("ColdAway Syrup", 14, 0.36),
        ("PainEase Tablets", 11, 0.34),
        ("AllerFree Spray", 18, 0.38),
        ("DigestWell Caps", 16, 0.35),
    ],
    "Wellness": [
        ("Vitamin D3 Drops", 21, 0.39),
        ("OmegaCare Softgels", 27, 0.42),
        ("Immunity Gummies", 19, 0.37),
        ("Protein Plus Sachets", 33, 0.44),
    ],
    "Devices": [
        ("Digital Thermometer", 22, 0.33),
        ("Pulse Oximeter", 49, 0.40),
        ("BP Monitor", 69, 0.46),
        ("Nebulizer Kit", 57, 0.43),
    ],
}

REGIONS = {
    "North": [("United States", "New York"), ("United States", "Chicago"), ("Canada", "Toronto")],
    "South": [("United States", "Austin"), ("United States", "Miami"), ("Mexico", "Monterrey")],
    "West": [("United States", "Seattle"), ("United States", "San Diego"), ("Canada", "Vancouver")],
    "Central": [("United States", "Denver"), ("United States", "Kansas City"), ("Mexico", "Guadalajara")],
}

SEGMENTS = ["Retail", "Hospital", "Clinic", "Distributor"]
CHANNELS = ["Online", "Retail Store", "Partner", "Sales Rep"]
PAYMENTS = ["Card", "Bank Transfer", "Insurance", "Wallet"]
STATUSES = ["Delivered", "Delivered", "Delivered", "Returned", "Cancelled"]


def make_sales_rows(row_count: int = 5000, seed: int = 42) -> list[dict]:
    random.seed(seed)
    start_date = date.today().replace(day=1) - timedelta(days=730)
    rows: list[dict] = []

    for index in range(1, row_count + 1):
        category = random.choices(
            list(PRODUCT_CATALOG.keys()),
            weights=[0.33, 0.26, 0.25, 0.16],
        )[0]
        product, base_price, cost_ratio = random.choice(PRODUCT_CATALOG[category])
        region = random.choice(list(REGIONS.keys()))
        country, city = random.choice(REGIONS[region])
        segment = random.choices(SEGMENTS, weights=[0.42, 0.2, 0.23, 0.15])[0]
        channel = random.choices(CHANNELS, weights=[0.38, 0.29, 0.18, 0.15])[0]
        status = random.choice(STATUSES)

        order_date = start_date + timedelta(days=random.randint(0, 729))
        quantity = random.randint(1, 18 if segment == "Distributor" else 8)
        seasonal_boost = 1.12 if order_date.month in [1, 11, 12] else 1.0
        region_factor = {"North": 1.08, "South": 0.98, "West": 1.12, "Central": 0.94}[region]
        unit_price = round(base_price * seasonal_boost * region_factor * random.uniform(0.9, 1.15), 2)
        discount_pct = round(random.choice([0, 0.03, 0.05, 0.08, 0.1, 0.12]), 2)

        gross_revenue = quantity * unit_price * (1 - discount_pct)
        if status == "Cancelled":
            gross_revenue = 0
        elif status == "Returned":
            gross_revenue *= 0.25

        cost = gross_revenue * cost_ratio * random.uniform(0.92, 1.08)
        profit = gross_revenue - cost

        rows.append(
            {
                "order_id": f"ORD-{index:06d}",
                "order_date": order_date.isoformat(),
                "customer_id": f"CUST-{random.randint(1000, 1799)}",
                "customer_segment": segment,
                "region": region,
                "country": country,
                "city": city,
                "category": category,
                "product": product,
                "channel": channel,
                "payment_method": random.choice(PAYMENTS),
                "fulfillment_status": status,
                "quantity": quantity,
                "unit_price": unit_price,
                "discount_pct": discount_pct,
                "revenue": round(gross_revenue, 2),
                "cost": round(cost, 2),
                "profit": round(profit, 2),
            }
        )

    return rows


def reset_database(rows: list[dict]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    schema = (SQL_DIR / "schema.sql").read_text(encoding="utf-8")

    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(schema)
        columns = list(rows[0].keys())
        placeholders = ",".join(["?"] * len(columns))
        conn.executemany(
            f"INSERT INTO sales ({','.join(columns)}) VALUES ({placeholders})",
            [[row[column] for column in columns] for row in rows],
        )


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    rows = make_sales_rows()
    with CSV_PATH.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    reset_database(rows)
    print(f"Created {CSV_PATH}")
    print(f"Created {DB_PATH}")
    print(f"Rows: {len(rows):,}")


if __name__ == "__main__":
    main()
