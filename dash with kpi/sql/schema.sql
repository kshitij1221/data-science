DROP TABLE IF EXISTS sales;

CREATE TABLE sales (
    order_id TEXT PRIMARY KEY,
    order_date TEXT NOT NULL,
    customer_id TEXT NOT NULL,
    customer_segment TEXT NOT NULL,
    region TEXT NOT NULL,
    country TEXT NOT NULL,
    city TEXT NOT NULL,
    category TEXT NOT NULL,
    product TEXT NOT NULL,
    channel TEXT NOT NULL,
    payment_method TEXT NOT NULL,
    fulfillment_status TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    discount_pct REAL NOT NULL,
    revenue REAL NOT NULL,
    cost REAL NOT NULL,
    profit REAL NOT NULL
);

CREATE INDEX idx_sales_order_date ON sales(order_date);
CREATE INDEX idx_sales_region ON sales(region);
CREATE INDEX idx_sales_category ON sales(category);
CREATE INDEX idx_sales_channel ON sales(channel);
