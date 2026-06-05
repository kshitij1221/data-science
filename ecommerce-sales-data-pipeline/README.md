# E-Commerce Sales Data Pipeline

A local data engineering project that loads dummy e-commerce sales data into MySQL, transforms raw transactional data into analytics tables, validates data quality, and prints business KPIs.

## What This Project Shows

- Local MySQL database setup with Docker Compose
- Dummy e-commerce data generation
- Raw ingestion tables for customers, products, orders, order items, payments, and shipments
- SQL-based transformation into analytics marts
- Data quality checks
- KPI queries for revenue, order volume, customer behavior, and product performance

## Tech Stack

- Python
- MySQL
- Docker Compose
- Faker
- mysql-connector-python

## Project Structure

```text
ecommerce-sales-data-pipeline/
  config/
    .env.example
  docs/
    data_model.md
  sql/
    01_raw_schema.sql
    02_mart_schema.sql
    03_kpi_queries.sql
  src/
    db.py
    seed_data.py
    run_pipeline.py
    validate.py
    show_kpis.py
    main.py
  tests/
    test_project_files.py
  docker-compose.yml
  requirements.txt
```

## Run Locally

### 1. Start MySQL

```bash
docker compose up -d
```

MySQL will be available on port `3306`.

### 2. Create Your Environment File

Copy the example file:

```bash
copy config\.env.example .env
```

On macOS/Linux:

```bash
cp config/.env.example .env
```

### 3. Install Python Dependencies

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

On macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Run the Full Pipeline

```bash
python -m src.main
```

This command will:

1. Create raw and analytics tables.
2. Generate dummy e-commerce data.
3. Load data into MySQL.
4. Transform raw data into mart tables.
5. Run data quality checks.
6. Print KPI summaries.

## Useful Commands

Run only dummy data loading:

```bash
python -m src.seed_data
```

Run only transformations:

```bash
python -m src.run_pipeline
```

Run only validations:

```bash
python -m src.validate
```

Show KPIs:

```bash
python -m src.show_kpis
```

Stop MySQL:

```bash
docker compose down
```

Remove MySQL data and start fresh:

```bash
docker compose down -v
```

## Portfolio Talking Points

- Designed a normalized raw data layer for e-commerce transactions.
- Built a repeatable seed-and-transform pipeline using Python and MySQL.
- Created analytics marts for daily sales, customer lifetime value, and product performance.
- Added validation checks for missing records, invalid totals, and orphaned relationships.
- Produced business KPIs from transformed warehouse tables.

