# Automated Business Report Generator

This project creates a business report from raw sales data and exports:

- `outputs/business_report.xlsx`
- `outputs/business_report.pdf`

Dummy raw data is already included in `data/dummy_sales_data.csv`.

## How To Run

1. Open this folder in your compiler or terminal.

2. Install the required Python packages:

```bash
pip install -r requirements.txt
```

3. Run the report generator:

```bash
python generate_report.py
```

4. Check the generated files inside:

```text
outputs/
```

## Project Structure

```text
business_report_generator/
  data/
    dummy_sales_data.csv
  outputs/
  generate_report.py
  requirements.txt
  README.md
```

## What The Report Includes

- Total revenue
- Total units sold
- Average order value
- Revenue by region
- Revenue by product category
- Monthly revenue trend
- Top 10 customers
- Excel charts
- PDF summary tables

