from pathlib import Path
import pandas as pd

PRODUCTS_FILE = Path("data/products.parquet")
OUTPUT_FILE = Path("data/sales_dirty.csv")


def main():
    if not PRODUCTS_FILE.exists():
        raise FileNotFoundError(
            "products.parquet not found. Run: python src/fetch_products.py"
        )

    products = pd.read_parquet(PRODUCTS_FILE)
    # Use real product IDs from the API, so sales and products match.
    sample = products[["id", "price"]].head(6).copy()
    if len(sample) < 4:
        raise ValueError("At least four products are needed for the sample.")

    rows = [
        {"order_id": 1001, "product_id": int(sample.iloc[0]["id"]),
         "quantity": "2", "sale_price": str(sample.iloc[0]["price"]),
         "order_date": "2025-01-05"},
        {"order_id": 1002, "product_id": int(sample.iloc[1]["id"]),
         "quantity": "1", "sale_price": str(sample.iloc[1]["price"]),
         "order_date": "2025-01-06"},
        {"order_id": 1002, "product_id": int(sample.iloc[1]["id"]),
         "quantity": "1", "sale_price": str(sample.iloc[1]["price"]),
         "order_date": "2025-01-06"},  # duplicate row
        {"order_id": 1003, "product_id": int(sample.iloc[2]["id"]),
         "quantity": None, "sale_price": str(sample.iloc[2]["price"]),
         "order_date": "2025-01-07"},  # missing quantity
        {"order_id": 1004, "product_id": int(sample.iloc[3]["id"]),
         "quantity": "three", "sale_price": "unknown",
         "order_date": "2025-01-08"},  # incorrect data types
        {"order_id": 1005, "product_id": int(sample.iloc[0]["id"]),
         "quantity": "4", "sale_price": str(sample.iloc[0]["price"]),
         "order_date": "not-a-date"},  # invalid date
        {"order_id": 1006, "product_id": None,
         "quantity": "2", "sale_price": "15.50",
         "order_date": "2025-01-10"},  # missing product ID
        {"order_id": 1007, "product_id": int(sample.iloc[4]["id"]),
         "quantity": "5", "sale_price": None,
         "order_date": "2025-01-11"},  # missing price
    ]

    df = pd.DataFrame(rows)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Created intentionally messy sample: {OUTPUT_FILE}")
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
