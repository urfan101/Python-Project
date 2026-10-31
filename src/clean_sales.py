from pathlib import Path
import pandas as pd

PRODUCTS_FILE = Path("data/products.parquet")
INPUT_FILE = Path("data/sales_dirty.csv")
OUTPUT_FILE = Path("data/sales_clean.csv")


def main():
    if not PRODUCTS_FILE.exists() or not INPUT_FILE.exists():
        raise FileNotFoundError(
            "Required files are missing. Run fetch_products.py and "
            "create_dirty_sales.py first."
        )

    sales = pd.read_csv(INPUT_FILE)
    products = pd.read_parquet(PRODUCTS_FILE)

    print("Rows before cleaning:", len(sales))

    # 1. Remove exact duplicate rows.
    sales = sales.drop_duplicates()

    # 2. Convert columns to numeric values; invalid values become NaN.
    for column in ["order_id", "product_id", "quantity", "sale_price"]:
        sales[column] = pd.to_numeric(sales[column], errors="coerce")

    # 3. Parse dates; invalid dates become NaT.
    sales["order_date"] = pd.to_datetime(sales["order_date"], errors="coerce")

    # 4. Remove rows without essential information.
    sales = sales.dropna(subset=["order_id", "product_id", "order_date"])

    # 5. Keep only product IDs that exist in the API product file.
    valid_ids = set(products["id"].astype(int))
    sales = sales[sales["product_id"].isin(valid_ids)].copy()

    # 6. Fill missing/invalid quantities with the median; quantities must be positive.
    sales.loc[sales["quantity"] <= 0, "quantity"] = pd.NA
    median_quantity = sales["quantity"].dropna().median()
    if pd.isna(median_quantity):
        median_quantity = 1
    sales["quantity"] = sales["quantity"].fillna(median_quantity).round().astype(int)

    # 7. Fill missing/invalid prices from the product API data.
    price_by_id = products.set_index("id")["price"]
    sales["sale_price"] = sales["sale_price"].fillna(
        sales["product_id"].map(price_by_id)
    )

    # Remove any row whose price still cannot be recovered.
    sales = sales.dropna(subset=["sale_price"])
    sales = sales[sales["sale_price"] >= 0].copy()

    # 8. Set consistent data types and calculate line total.
    sales["order_id"] = sales["order_id"].astype(int)
    sales["product_id"] = sales["product_id"].astype(int)
    sales["quantity"] = sales["quantity"].astype(int)
    sales["sale_price"] = sales["sale_price"].astype(float).round(2)
    sales["order_date"] = sales["order_date"].dt.strftime("%Y-%m-%d")
    sales["line_total"] = (sales["quantity"] * sales["sale_price"]).round(2)

    sales = sales.sort_values(["order_id", "product_id"]).reset_index(drop=True)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    sales.to_csv(OUTPUT_FILE, index=False)

    print("Rows after cleaning:", len(sales))
    print(f"Clean data saved to: {OUTPUT_FILE}")
    print(sales.to_string(index=False))


if __name__ == "__main__":
    main()
