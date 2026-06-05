CREATE TABLE IF NOT EXISTS raw_customers (
    customer_id INT PRIMARY KEY,
    first_name VARCHAR(80) NOT NULL,
    last_name VARCHAR(80) NOT NULL,
    email VARCHAR(160) NOT NULL UNIQUE,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    created_at DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS raw_products (
    product_id INT PRIMARY KEY,
    sku VARCHAR(40) NOT NULL UNIQUE,
    product_name VARCHAR(160) NOT NULL,
    category VARCHAR(80) NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    created_at DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS raw_orders (
    order_id INT PRIMARY KEY,
    customer_id INT NOT NULL,
    order_status VARCHAR(30) NOT NULL,
    order_date DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES raw_customers(customer_id)
);

CREATE TABLE IF NOT EXISTS raw_order_items (
    order_item_id INT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    discount_amount DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES raw_orders(order_id),
    FOREIGN KEY (product_id) REFERENCES raw_products(product_id)
);

CREATE TABLE IF NOT EXISTS raw_payments (
    payment_id INT PRIMARY KEY,
    order_id INT NOT NULL,
    payment_method VARCHAR(40) NOT NULL,
    payment_status VARCHAR(30) NOT NULL,
    paid_amount DECIMAL(10, 2) NOT NULL,
    paid_at DATETIME,
    FOREIGN KEY (order_id) REFERENCES raw_orders(order_id)
);

CREATE TABLE IF NOT EXISTS raw_shipments (
    shipment_id INT PRIMARY KEY,
    order_id INT NOT NULL,
    carrier VARCHAR(60) NOT NULL,
    shipment_status VARCHAR(30) NOT NULL,
    shipped_at DATETIME,
    delivered_at DATETIME,
    FOREIGN KEY (order_id) REFERENCES raw_orders(order_id)
);

