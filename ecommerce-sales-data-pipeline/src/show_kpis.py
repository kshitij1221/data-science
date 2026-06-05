from tabulate import tabulate

from src.db import get_connection


KPI_QUERIES = {
    "Total Revenue": """
        SELECT ROUND(SUM(gross_revenue), 2) AS total_revenue
        FROM mart_daily_sales
    """,
    "Top Product Categories": """
        SELECT category, ROUND(SUM(product_revenue), 2) AS category_revenue
        FROM mart_product_performance
        GROUP BY category
        ORDER BY category_revenue DESC
        LIMIT 10
    """,
    "Top Customers": """
        SELECT customer_id, first_name, last_name, city, state, lifetime_value
        FROM mart_customer_lifetime_value
        ORDER BY lifetime_value DESC
        LIMIT 10
    """,
    "Recent Daily Sales": """
        SELECT sales_date, total_orders, unique_customers, total_units_sold, gross_revenue
        FROM mart_daily_sales
        ORDER BY sales_date DESC
        LIMIT 10
    """,
}


def show_kpis() -> None:
    with get_connection() as conn:
        with conn.cursor() as cursor:
            for title, query in KPI_QUERIES.items():
                cursor.execute(query)
                rows = cursor.fetchall()
                headers = [column[0] for column in cursor.description]
                print(f"\n{title}")
                print(tabulate(rows, headers=headers, tablefmt="github"))


if __name__ == "__main__":
    show_kpis()

