from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
import random
import sqlite3


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "ecommerce_local.db"

CATEGORIES = ["Electronics", "Home", "Fashion", "Beauty", "Sports", "Books", "Toys", "Grocery"]
FIRST_NAMES = ["Aarav", "Vivaan", "Aditya", "Isha", "Ananya", "Diya", "Rohan", "Kabir", "Neha", "Priya"]
LAST_NAMES = ["Sharma", "Patel", "Verma", "Reddy", "Nair", "Mehta", "Gupta", "Joshi", "Khan", "Iyer"]
CITIES = ["Mumbai", "Delhi", "Bengaluru", "Hyderabad", "Pune", "Chennai", "Kolkata", "Ahmedabad"]
STATES = ["Maharashtra", "Delhi", "Karnataka", "Telangana", "Tamil Nadu", "West Bengal", "Gujarat"]
STATUSES = ["created", "paid", "shipped", "delivered", "cancelled"]
PAYMENT_METHODS = ["credit_card", "debit_card", "upi", "net_banking", "wallet", "cod"]
CARRIERS = ["BlueDart", "Delhivery", "DHL", "FedEx", "Ecom Express"]


def dt(days_back: int) -> str:
    value = datetime.now() - timedelta(days=random.randint(0, days_back), hours=random.randint(0, 23))
    return value.strftime("%Y-%m-%d %H:%M:%S")


def execute_script(conn: sqlite3.Connection, path: Path) -> None:
    conn.executescript(path.read_text(encoding="utf-8"))
    conn.commit()


def reset_raw_tables(conn: sqlite3.Connection) -> None:
    for table in [
        "raw_shipments",
        "raw_payments",
        "raw_order_items",
        "raw_orders",
        "raw_products",
        "raw_customers",
    ]:
        conn.execute(f"DELETE FROM {table}")
    conn.commit()


def seed(conn: sqlite3.Connection, customer_count: int = 500, product_count: int = 120, order_count: int = 1500) -> None:
    random.seed(42)
    execute_script(conn, PROJECT_ROOT / "sql" / "01_raw_schema.sql")
    reset_raw_tables(conn)

    customers = []
    for customer_id in range(1, customer_count + 1):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        customers.append(
            (
                customer_id,
                first,
                last,
                f"{first.lower()}.{last.lower()}.{customer_id}@example.com",
                random.choice(CITIES),
                random.choice(STATES),
                "India",
                dt(730),
            )
        )

    products = []
    for product_id in range(1, product_count + 1):
        category = random.choice(CATEGORIES)
        products.append(
            (
                product_id,
                f"SKU-{product_id:05d}",
                f"{category} Product {product_id}",
                category,
                round(random.uniform(100, 20000), 2),
                dt(730),
            )
        )

    orders = []
    order_items = []
    payments = []
    shipments = []
    order_item_id = 1

    for order_id in range(1, order_count + 1):
        order_date = dt(180)
        status = random.choices(STATUSES, weights=[8, 28, 20, 36, 8], k=1)[0]
        orders.append((order_id, random.randint(1, customer_count), status, order_date, order_date))

        order_total = 0.0
        for _ in range(random.randint(1, 5)):
            quantity = random.randint(1, 4)
            unit_price = round(random.uniform(100, 20000), 2)
            discount = round(random.uniform(0, unit_price * quantity * 0.2), 2)
            order_total += (quantity * unit_price) - discount
            order_items.append(
                (
                    order_item_id,
                    order_id,
                    random.randint(1, product_count),
                    quantity,
                    unit_price,
                    discount,
                )
            )
            order_item_id += 1

        payment_status = "paid" if status in {"paid", "shipped", "delivered"} else status
        paid_at = order_date if payment_status == "paid" else None
        payments.append((order_id, order_id, random.choice(PAYMENT_METHODS), payment_status, round(order_total, 2), paid_at))

        if status in {"shipped", "delivered"}:
            delivered_at = order_date if status == "delivered" else None
            shipments.append((order_id, order_id, random.choice(CARRIERS), status, order_date, delivered_at))

    conn.executemany("INSERT INTO raw_customers VALUES (?, ?, ?, ?, ?, ?, ?, ?)", customers)
    conn.executemany("INSERT INTO raw_products VALUES (?, ?, ?, ?, ?, ?)", products)
    conn.executemany("INSERT INTO raw_orders VALUES (?, ?, ?, ?, ?)", orders)
    conn.executemany("INSERT INTO raw_order_items VALUES (?, ?, ?, ?, ?, ?)", order_items)
    conn.executemany("INSERT INTO raw_payments VALUES (?, ?, ?, ?, ?, ?)", payments)
    conn.executemany("INSERT INTO raw_shipments VALUES (?, ?, ?, ?, ?, ?)", shipments)
    conn.commit()

    print(f"Seeded {customer_count} customers, {product_count} products, and {order_count} orders.")


def validate(conn: sqlite3.Connection) -> None:
    checks = {
        "orders_without_customers": """
            SELECT COUNT(*) FROM raw_orders o
            LEFT JOIN raw_customers c ON o.customer_id = c.customer_id
            WHERE c.customer_id IS NULL
        """,
        "items_without_orders": """
            SELECT COUNT(*) FROM raw_order_items oi
            LEFT JOIN raw_orders o ON oi.order_id = o.order_id
            WHERE o.order_id IS NULL
        """,
        "items_with_non_positive_quantity": "SELECT COUNT(*) FROM raw_order_items WHERE quantity <= 0",
        "items_with_negative_revenue": """
            SELECT COUNT(*) FROM raw_order_items
            WHERE (quantity * unit_price) - discount_amount < 0
        """,
        "empty_daily_sales_mart": "SELECT CASE WHEN COUNT(*) = 0 THEN 1 ELSE 0 END FROM mart_daily_sales",
    }

    failures = []
    for name, query in checks.items():
        result = conn.execute(query).fetchone()[0]
        print(f"{'PASS' if result == 0 else 'FAIL'}: {name} = {result}")
        if result != 0:
            failures.append(name)

    if failures:
        raise RuntimeError(f"Data quality checks failed: {', '.join(failures)}")


def print_query(conn: sqlite3.Connection, title: str, query: str) -> None:
    cursor = conn.execute(query)
    columns = [description[0] for description in cursor.description]
    rows = cursor.fetchall()
    print(f"\n{title}")
    print(" | ".join(columns))
    print("-" * 80)
    for row in rows:
        print(" | ".join(str(value) for value in row))


def show_kpis(conn: sqlite3.Connection) -> None:
    print_query(conn, "Total Revenue", "SELECT ROUND(SUM(gross_revenue), 2) AS total_revenue FROM mart_daily_sales")
    print_query(
        conn,
        "Top Product Categories",
        """
        SELECT category, ROUND(SUM(product_revenue), 2) AS category_revenue
        FROM mart_product_performance
        GROUP BY category
        ORDER BY category_revenue DESC
        LIMIT 10
        """,
    )
    print_query(
        conn,
        "Top Customers",
        """
        SELECT customer_id, first_name, last_name, city, state, lifetime_value
        FROM mart_customer_lifetime_value
        ORDER BY lifetime_value DESC
        LIMIT 10
        """,
    )
    print_query(
        conn,
        "Recent Daily Sales",
        """
        SELECT sales_date, total_orders, unique_customers, total_units_sold, gross_revenue
        FROM mart_daily_sales
        ORDER BY sales_date DESC
        LIMIT 10
        """,
    )


def main() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        seed(conn)
        execute_script(conn, PROJECT_ROOT / "sql" / "02_mart_schema.sql")
        print("Analytics mart tables rebuilt.")
        validate(conn)
        show_kpis(conn)
    print(f"\nSQLite database created at: {DB_PATH}")


if __name__ == "__main__":
    main()

