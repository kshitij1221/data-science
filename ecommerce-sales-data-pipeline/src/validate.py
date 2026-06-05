from src.db import get_connection


CHECKS = {
    "orders_without_customers": """
        SELECT COUNT(*)
        FROM raw_orders o
        LEFT JOIN raw_customers c ON o.customer_id = c.customer_id
        WHERE c.customer_id IS NULL
    """,
    "items_without_orders": """
        SELECT COUNT(*)
        FROM raw_order_items oi
        LEFT JOIN raw_orders o ON oi.order_id = o.order_id
        WHERE o.order_id IS NULL
    """,
    "items_with_non_positive_quantity": """
        SELECT COUNT(*)
        FROM raw_order_items
        WHERE quantity <= 0
    """,
    "items_with_negative_revenue": """
        SELECT COUNT(*)
        FROM raw_order_items
        WHERE (quantity * unit_price) - discount_amount < 0
    """,
    "empty_daily_sales_mart": """
        SELECT CASE WHEN COUNT(*) = 0 THEN 1 ELSE 0 END
        FROM mart_daily_sales
    """,
}


def run_validations() -> None:
    failures = []
    with get_connection() as conn:
        with conn.cursor() as cursor:
            for check_name, query in CHECKS.items():
                cursor.execute(query)
                result = cursor.fetchone()[0]
                status = "PASS" if result == 0 else "FAIL"
                print(f"{status}: {check_name} = {result}")
                if result != 0:
                    failures.append(check_name)

    if failures:
        raise RuntimeError(f"Data quality checks failed: {', '.join(failures)}")


if __name__ == "__main__":
    run_validations()

