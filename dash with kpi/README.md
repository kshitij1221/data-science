# Business KPI Dashboard with SQL + Python + Streamlit

This project is a self-contained KPI dashboard for sales analytics. It uses:

- Python to generate a dummy pharmaceutical/e-commerce-style sales dataset
- SQLite for the SQL database layer
- Streamlit for the interactive dashboard
- Plotly for charts

The dashboard includes revenue, profit, margin, order volume, average order value, monthly trends, region/category/channel breakdowns, fulfillment status, top products, and a raw data drill-down.

## Project structure

```text
business_kpi_dashboard/
  app.py                  # Streamlit dashboard
  generate_data.py        # Creates dummy CSV and SQLite database
  requirements.txt        # Python dependencies
  data/
    sales_dummy.csv       # Generated dataset, created after running generate_data.py
    business_kpi.db       # SQLite database, created after running generate_data.py
  sql/
    schema.sql            # SQL table schema and indexes
```

## How to run

### 1. Open the project folder

```bash
cd business_kpi_dashboard
```

### 2. Create and activate a virtual environment

Recommended: use Python 3.12. On Windows, check installed Python versions with:

```powershell
py -0p
```

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Generate the dummy dataset and SQLite database

```bash
python generate_data.py
```

This creates:

- `data/sales_dummy.csv`
- `data/business_kpi.db`

### 5. Start the dashboard

```bash
streamlit run app.py
```

Streamlit will print a local URL such as:

```text
http://localhost:8501
```

Open that URL in your browser.

## Notes

- No Kaggle download is required. The generated dataset follows the shape of common pharmaceutical sales and e-commerce sales datasets.
- If you delete the files in `data/`, the app can regenerate the SQLite database automatically when it starts.
- The SQL schema is in `sql/schema.sql`, and the dashboard reads from SQLite using SQL queries.
