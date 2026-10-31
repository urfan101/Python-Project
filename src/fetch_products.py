from pathlib import Path
import requests
import pandas as pd

API_URL = "https://dummyjson.com/products"
OUTPUT = Path("data/products.parquet")


def fetch_products() -> pd.DataFrame:
    """Download products from DummyJSON and return them as a DataFrame."""
    response = requests.get(API_URL, params={"limit": 100}, timeout=30)
    response.raise_for_status()

    payload = response.json()
    products = payload.get("products", [])
    if not products:
        raise ValueError("The API returned no products.")

    df = pd.DataFrame(products)
    return df


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    products = fetch_products()
    products.to_parquet(OUTPUT, index=False)

    print(f"Downloaded {len(products)} products.")
    print(f"Saved to: {OUTPUT}")
    print(products[["id", "title", "price"]].head())


if __name__ == "__main__":
    main()
