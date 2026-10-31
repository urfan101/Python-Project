# E-commerce data pipeline — stages 1 and 2

This project implements only the first two assignment stages:
1. Download product data from the public DummyJSON REST API and save it as Parquet.
2. Create a deliberately messy sales CSV and clean it with pandas.

PostgreSQL and GitHub teamwork are intentionally not included. They can be added later.

## Requirements
- Python 3.9+
- Internet connection for the API request

## Setup

From the project root:

```bash
python -m venv .venv
```

Activate the environment:

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the pipeline

Run these commands from the project root, in this order:

```bash
python src/fetch_products.py
python src/create_dirty_sales.py
python src/clean_sales.py
```

## Output files

| File | Description |
|---|---|
| `data/products.parquet` | Products downloaded from DummyJSON |
| `data/sales_dirty.csv` | Example sales data containing quality problems |
| `data/sales_clean.csv` | Cleaned sales data |

## Data quality problems demonstrated

The generated sales CSV intentionally includes:
- an exact duplicate row;
- missing quantity and price values;
- text in numeric columns (`three`, `unknown`);
- an invalid date;
- a missing product ID.

The cleaning script:
- removes duplicate rows;
- converts numeric columns and dates to appropriate types;
- removes rows missing essential fields or containing unknown product IDs;
- fills missing/invalid quantities with the median quantity;
- fills missing/invalid prices using the matching product price from the API;
- creates `line_total = quantity * sale_price`.

The sales file uses product IDs taken directly from `products.parquet`, so the IDs match the API data.

## API
DummyJSON products endpoint: https://dummyjson.com/products?limit=100
