import pandas as pd

products = pd.read_parquet("data/products.parquet")
valid_ids = set(products["id"].astype(int))

df = pd.read_csv("data/sales_dirty.csv")

clean_rows = []
rejected_rows = []
seen = set()

for _, row in df.iterrows():
    if pd.isna(row["order_id"]) or pd.isna(row["product_id"]):
        bad = row.to_dict()
        bad["reason"] = "eksik id"
        rejected_rows.append(bad)
        continue

    try:
        oid = int(float(row["order_id"]))
        pid = int(float(row["product_id"]))
        qty = int(float(row["quantity"]))
        price = float(row["sale_price"])
        dt = pd.to_datetime(row["order_date"], errors="raise")
    except Exception:
        bad = row.to_dict()
        bad["reason"] = "sehv yazi tipi"
        rejected_rows.append(bad)
        continue

    if pid not in valid_ids:
        bad = row.to_dict()
        bad["reason"] = "mehsul yoxdu"
        rejected_rows.append(bad)
        continue

    if qty <= 0 or price <= 0:
        bad = row.to_dict()
        bad["reason"] = "Qedes menfi yada sifirdi"
        rejected_rows.append(bad)
        continue

    if (oid, pid) in seen:
        bad = row.to_dict()
        bad["reason"] = "eyni seyi yazib"
        rejected_rows.append(bad)
        continue

    seen.add((oid, pid))

    total = round(qty * price, 2)
    clean_item = {
        "order_id": oid,
        "product_id": pid,
        "quantity": qty,

        "sale_price": round(price, 2),
        "order_date": dt.strftime("%Y-%m-%d"),
        "line_total": total
    }
    clean_rows.append(clean_item)

clean_df = pd.DataFrame(clean_rows)

rejected_df = pd.DataFrame(rejected_rows)

clean_df.to_csv("data/sales_clean.csv", index=False)

rejected_df.to_csv("data/sales_rejected.csv", index=False)

print("Clean rows:", len(clean_rows))

print("Rejected rows:", len(rejected_rows))