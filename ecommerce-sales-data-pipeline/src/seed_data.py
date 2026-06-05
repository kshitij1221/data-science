from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal
import os
import random

from faker import Faker

from src.db import PROJECT_ROOT, execute_sql_file, get_connection, truncate_tables


fake = Faker()
random.seed(42)
Faker.seed(42)


CATEGORIES = [
    "Electronics",
    "Home",
    "Fashion",
    "Beauty",
    "Sports",
    "Books",
    "Toys",
    "Grocery",
]
ORDER_STATUSES = ["created", "paid", "shipped", "delivered", "cancelled"]
PAYMENT_METHODS = ["credit_card", "debit_card", "upi", "net_banking", "wallet", "cod"]
CARRIERS = ["BlueDart", "Delhivery", "DHL", "FedEx", "Ecom Express"]


def money(value: float) -> Decimal:
    return Decimal(f"{value:.2f}")


def build_customers(count: int) -> list[tuple]:
    customers = []
    for customer_id in range(1, count + 1):
        first_name = fake.first_name()
        last_name = fake.last_name()
        customers.append(
            (
                customer_id,
                first_name,
                last_name,
                f"{first_name.lower()}.{last_name.lower()}.{customer_id}@example.com",
                fake.city(),
                fake.state(),
                fake.country(),
                fake.date_time_between(start_date="-2y", end_date="-90d"),
            )
        )
    return customers


def build_products(count: int) -> list[tuple]:
    products = []
    for product_id in range(1, count + 1):
        category = random.choice(CATEGORIES)
        products.append(
            (
                product_id,
                f"SKU-{product_id:05d}",
                f"{category} {fake.word().title()} {fake.word().title()}",
                category,
                money(random.uniform(5, 500)),
                fake.date_time_between(start_date="-2y", end_date="-60d"),
            )
        )
    return products


def build_orders(customer_count: int, product_count: int, order_count: int) -> dict[str, list[tuple]]:
    orders = []
    order_items = []
    payments = []
    shipments = []
    order_item_id = 1

    for order_id in range(1, order_count + 1):
        order_date = fake.date_time_between(start_date="-180d", end_date="now")
        status = random.choices(ORDER_STATUSES, weights=[8, 28, 20, 36, 8], k=1)[0]
        customer_id = random.randint(1, customer_count)
        updated_at = order_date + timedelta(days=random.randint(0, 7))
        orders.append((order_id, customer_id, status, order_date, updated_at))

        item_count = random.randint(1, 5)
        order_total = Decimal("0.00")
        for _ in range(item_count):
            product_id = random.randint(1, product_count)
            quantity = random.randint(1, 4)
            unit_price = money(random.uniform(5, 500))
            discount = money(random.uniform(0, float(unit_price) * quantity * 0.2))
            order_total += (unit_price * quantity) - discount
            order_items.append((order_item_id, order_id, product_id, quantity, unit_price, discount))
            order_item_id += 1

        payment_status = "paid" if status in {"paid", "shipped", "delivered"} else status
        paid_at = order_date + timedelta(minutes=random.randint(2, 240)) if payment_status == "paid" else None
        payments.append(
            (
                order_id,
                order_id,
                random.choice(PAYMENT_METHODS),
                payment_status,
                order_total,
                paid_at,
            )
        )

        if status in {"shipped", "delivered"}:
            shipped_at = order_date + timedelta(days=random.randint(1, 3))
            delivered_at = shipped_at + timedelta(days=random.randint(1, 7)) if status == "delivered" else None
            shipments.append(
                (
                    order_id,
                    order_id,
                    random.choice(CARRIERS),
                    status,
                    shipped_at,
                    delivered_at,
                )
            )

    return {
        "orders": orders,
        "order_items": order_items,
        "payments": payments,
        "shipments": shipments,
    }


def insert_many(table: str, columns: list[str], rows: list[tuple]) -> None:
    placeholders = ", ".join(["%s"] * len(columns))
    column_sql = ", ".join(columns)
    query = f"INSERT INTO {table} ({column_sql}) VALUES ({placeholders})"
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.executemany(query, rows)
        conn.commit()


def seed() -> None:
    customer_count = int(os.getenv("SEED_CUSTOMERS", "500"))
    product_count = int(os.getenv("SEED_PRODUCTS", "120"))
    order_count = int(os.getenv("SEED_ORDERS", "1500"))

    execute_sql_file(PROJECT_ROOT / "sql" / "01_raw_schema.sql")
    truncate_tables(
        [
            "raw_shipments",
            "raw_payments",
            "raw_order_items",
            "raw_orders",
            "raw_products",
            "raw_customers",
        ]
    )

    customers = build_customers(customer_count)
    products = build_products(product_count)
    sales = build_orders(customer_count, product_count, order_count)

    insert_many(
        "raw_customers",
        ["customer_id", "first_name", "last_name", "email", "city", "state", "country", "created_at"],
        customers,
    )
    insert_many(
        "raw_products",
        ["product_id", "sku", "product_name", "category", "unit_price", "created_at"],
        products,
    )
    insert_many(
        "raw_orders",
        ["order_id", "customer_id", "order_status", "order_date", "updated_at"],
        sales["orders"],
    )
    insert_many(
        "raw_order_items",
        ["order_item_id", "order_id", "product_id", "quantity", "unit_price", "discount_amount"],
        sales["order_items"],
    )
    insert_many(
        "raw_payments",
        ["payment_id", "order_id", "payment_method", "payment_status", "paid_amount", "paid_at"],
        sales["payments"],
    )
    insert_many(
        "raw_shipments",
        ["shipment_id", "order_id", "carrier", "shipment_status", "shipped_at", "delivered_at"],
        sales["shipments"],
    )

    print(f"Seeded {customer_count} customers, {product_count} products, and {order_count} orders.")


if __name__ == "__main__":
    seed()

