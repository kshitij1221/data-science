from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_required_files_exist():
    required_files = [
        "docker-compose.yml",
        "requirements.txt",
        "sql/01_raw_schema.sql",
        "sql/02_mart_schema.sql",
        "sql/03_kpi_queries.sql",
        "src/main.py",
        "src/seed_data.py",
        "src/run_pipeline.py",
        "src/validate.py",
        "src/show_kpis.py",
    ]

    for file_name in required_files:
        assert (PROJECT_ROOT / file_name).exists()


def test_raw_schema_contains_core_tables():
    schema = (PROJECT_ROOT / "sql" / "01_raw_schema.sql").read_text(encoding="utf-8")
    for table in [
        "raw_customers",
        "raw_products",
        "raw_orders",
        "raw_order_items",
        "raw_payments",
        "raw_shipments",
    ]:
        assert table in schema


def test_mart_schema_contains_analytics_tables():
    schema = (PROJECT_ROOT / "sql" / "02_mart_schema.sql").read_text(encoding="utf-8")
    for table in [
        "mart_daily_sales",
        "mart_customer_lifetime_value",
        "mart_product_performance",
    ]:
        assert table in schema

