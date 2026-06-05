DROP TABLE IF EXISTS mart_daily_sales;
CREATE TABLE mart_daily_sales AS
SELECT
    DATE(o.order_date) AS sales_date,
    COUNT(DISTINCT o.order_id) AS total_orders,
    COUNT(DISTINCT o.customer_id) AS unique_customers,
    SUM(oi.quantity) AS total_units_sold,
    ROUND(SUM((oi.quantity * oi.unit_price) - oi.discount_amount), 2) AS gross_revenue,
    ROUND(AVG((oi.quantity * oi.unit_price) - oi.discount_amount), 2) AS avg_item_revenue
FROM raw_orders o
JOIN raw_order_items oi ON o.order_id = oi.order_id
WHERE o.order_status IN ('paid', 'shipped', 'delivered')
GROUP BY DATE(o.order_date);

DROP TABLE IF EXISTS mart_customer_lifetime_value;
CREATE TABLE mart_customer_lifetime_value AS
SELECT
    c.customer_id,
    c.first_name,
    c.last_name,
    c.email,
    c.city,
    c.state,
    COUNT(DISTINCT o.order_id) AS total_orders,
    ROUND(SUM((oi.quantity * oi.unit_price) - oi.discount_amount), 2) AS lifetime_value,
    MIN(o.order_date) AS first_order_at,
    MAX(o.order_date) AS latest_order_at
FROM raw_customers c
JOIN raw_orders o ON c.customer_id = o.customer_id
JOIN raw_order_items oi ON o.order_id = oi.order_id
WHERE o.order_status IN ('paid', 'shipped', 'delivered')
GROUP BY
    c.customer_id,
    c.first_name,
    c.last_name,
    c.email,
    c.city,
    c.state;

DROP TABLE IF EXISTS mart_product_performance;
CREATE TABLE mart_product_performance AS
SELECT
    p.product_id,
    p.sku,
    p.product_name,
    p.category,
    SUM(oi.quantity) AS units_sold,
    COUNT(DISTINCT oi.order_id) AS order_count,
    ROUND(SUM((oi.quantity * oi.unit_price) - oi.discount_amount), 2) AS product_revenue
FROM raw_products p
JOIN raw_order_items oi ON p.product_id = oi.product_id
JOIN raw_orders o ON oi.order_id = o.order_id
WHERE o.order_status IN ('paid', 'shipped', 'delivered')
GROUP BY
    p.product_id,
    p.sku,
    p.product_name,
    p.category;

