-- E-commerce PostgreSQL data modeli (sxem + nümunə data + sorğular)

CREATE TABLE customers (
    id          SERIAL PRIMARY KEY,
    full_name   VARCHAR(100) NOT NULL,
    email       VARCHAR(150) NOT NULL UNIQUE,
    created_at  TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE categories (
    id    SERIAL PRIMARY KEY,
    name  VARCHAR(80) NOT NULL UNIQUE
);

CREATE TABLE products (
    id           SERIAL PRIMARY KEY,
    category_id  INT NOT NULL REFERENCES categories(id),
    name         VARCHAR(150) NOT NULL,
    price        NUMERIC(10,2) NOT NULL CHECK (price >= 0),
    stock        INT NOT NULL DEFAULT 0 CHECK (stock >= 0)
);

CREATE TABLE orders (
    id           SERIAL PRIMARY KEY,
    customer_id  INT NOT NULL REFERENCES customers(id),
    status       VARCHAR(20) NOT NULL DEFAULT 'pending'
                 CHECK (status IN ('pending','paid','shipped','cancelled')),
    created_at   TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE order_items (
    order_id    INT NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id  INT NOT NULL REFERENCES products(id),
    quantity    INT NOT NULL CHECK (quantity > 0),
    unit_price  NUMERIC(10,2) NOT NULL,  -- sifariş anındakı qiymət
    PRIMARY KEY (order_id, product_id)
);

CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_orders_customer   ON orders(customer_id);

-- Nümunə data
INSERT INTO customers (full_name, email) VALUES
    ('Aysel Məmmədova', 'aysel@example.com'),
    ('Rəşad Əliyev',    'rashad@example.com');
INSERT INTO categories (name) VALUES ('Elektronika'), ('Kitab');
INSERT INTO products (category_id, name, price, stock) VALUES
    (1, 'Qulaqlıq', 59.90, 20),
    (1, 'Klaviatura', 89.00, 10),
    (2, 'PostgreSQL Əsasları', 25.50, 50);
INSERT INTO orders (customer_id, status) VALUES (1, 'paid'), (2, 'pending');
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
    (1, 1, 1, 59.90), (1, 3, 2, 25.50), (2, 2, 1, 89.00);

-- Hər sifarişin ümumi məbləği
SELECT o.id, c.full_name, o.status, SUM(oi.quantity * oi.unit_price) AS total
FROM orders o
JOIN customers c    ON c.id = o.customer_id
JOIN order_items oi ON oi.order_id = o.id
GROUP BY o.id, c.full_name, o.status
ORDER BY o.id;

-- Ən çox satılan məhsullar
SELECT p.name, SUM(oi.quantity) AS sold
FROM order_items oi JOIN products p ON p.id = oi.product_id
GROUP BY p.name ORDER BY sold DESC;
