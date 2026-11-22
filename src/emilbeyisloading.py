import pandas as pd
import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "ecommerce",
    "user": "postgres",
    "password": "admin"
}

products_df = pd.read_parquet("data/products.parquet")

sales_df = pd.read_csv("data/sales_clean.csv")



conn = psycopg2.connect(**DB_CONFIG)
emil = conn.cursor()

#I think it should work like that, teacha bliz help if I am wrong


category_col = "category" if "category" in products_df.columns else None


title_col = "title" if "title" in products_df.columns else "name"


if category_col:

    categories = products_df[category_col].dropna().unique()
    
    for cat in categories:
        emil.execute(
            "INSERT INTO categories (name) VALUES (%s) ON CONFLICT (name) DO NOTHING",
            (str(cat),)
        )
else:
    emil.execute("INSERT INTO categories (name) VALUES ('General') ON CONFLICT (name) DO NOTHING")

conn.commit()

emil.execute("SELECT id, name FROM categories")

cat_map = {name: cid for cid, name in emil.fetchall()}

for _, row in products_df.iterrows():
    cat_name = str(row[category_col]) if category_col and pd.notna(row[category_col]) else "General"
    cat_id = cat_map[cat_name]
    emil.execute(

        """
        INSERT INTO products (id, category_id, name, price, stock)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET price = EXCLUDED.price
        """,

        (int(row["id"]), cat_id, str(row[title_col])[:150], float(row["price"]), 100)
    )

emil.execute(
    """
    INSERT INTO customers (id, full_name, email)
    VALUES (1, 'Default Customer', 'customer@example.com')
    ON CONFLICT (id) DO NOTHING
    """
)

#All Hail AI and Open Web Sources, muellim, but I tried really hard ngl

for oid in sales_df["order_id"].unique():

    order_date = sales_df[sales_df["order_id"] == oid]["order_date"].iloc[0]

    emil.execute(
        """
        INSERT INTO orders (id, customer_id, status, created_at)
        VALUES (%s, 1, 'paid', %s)
        ON CONFLICT (id) DO NOTHING
        """,
        (int(oid), order_date)
    )

for _, row in sales_df.iterrows():

    emil.execute(
        """
        INSERT INTO order_items (order_id, product_id, quantity, unit_price)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (order_id, product_id) DO UPDATE
        SET quantity = EXCLUDED.quantity, unit_price = EXCLUDED.unit_price
        """,
        (int(row["order_id"]), int(row["product_id"]), int(row["quantity"]), float(row["sale_price"]))
    )

conn.commit()

query ="""
SELECT p.id, p.name, SUM(oi.quantity) AS total_units, SUM(oi.quantity * oi.unit_price) AS total_revenue

FROM products p
JOIN order_items oi ON oi.product_id = p.id
GROUP BY p.id, p.name
ORDER BY total_revenue DESC;

"""

report_df = pd.read_sql_query(query, conn)
report_df.to_csv("data/sales_report.csv", index=False)
print(report_df)

emil.close()
conn.close()