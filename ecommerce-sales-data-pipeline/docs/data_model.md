# Data Model

## Raw Layer

The raw layer stores source-style transactional tables.

| Table | Purpose |
| --- | --- |
| `raw_customers` | Customer profile and location data |
| `raw_products` | Product catalog and category data |
| `raw_orders` | Order header records |
| `raw_order_items` | Line items attached to orders |
| `raw_payments` | Payment method and status |
| `raw_shipments` | Shipment carrier and delivery status |

## Analytics Layer

| Table | Purpose |
| --- | --- |
| `mart_daily_sales` | Daily revenue, order count, customer count, and units sold |
| `mart_customer_lifetime_value` | Customer-level order history and lifetime value |
| `mart_product_performance` | Product and category revenue performance |

## Pipeline Flow

```text
Dummy data generator
        |
        v
MySQL raw tables
        |
        v
SQL transformations
        |
        v
Analytics marts
        |
        v
Validation checks and KPI queries
```

