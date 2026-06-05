-- Overall revenue
SELECT ROUND(SUM(gross_revenue), 2) AS total_revenue
FROM mart_daily_sales;

-- Top product categories
SELECT category, ROUND(SUM(product_revenue), 2) AS category_revenue
FROM mart_product_performance
GROUP BY category
ORDER BY category_revenue DESC
LIMIT 10;

-- Top customers by lifetime value
SELECT customer_id, first_name, last_name, city, state, lifetime_value
FROM mart_customer_lifetime_value
ORDER BY lifetime_value DESC
LIMIT 10;

-- Daily sales trend
SELECT sales_date, total_orders, unique_customers, total_units_sold, gross_revenue
FROM mart_daily_sales
ORDER BY sales_date;

