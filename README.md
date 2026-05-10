# design
designing new systems

DB Design

CREATE TABLE positions_by_account_date (
    account_id text,
    business_date date,
    share_id text,
    quantity decimal,
    market_value decimal,
    PRIMARY KEY (
        (account_id),
        business_date,
        share_id
    )
)
WITH CLUSTERING ORDER BY (
    business_date DESC,
    share_id ASC
);

-----Data----
 account_id | business_date | share_id | market_value | quantity
------------+---------------+---------------+--------------+----------
    ACC1001 |    2026-05-08 |          AAPL |        20500 |      100
    ACC1001 |    2026-05-08 |          AMZN |         9800 |       40
    ACC1001 |    2026-05-08 |          GOOG |        15500 |       50
    ACC1001 |    2026-05-08 |          MSFT |        12000 |       75
    ACC1001 |    2026-05-08 |          TSLA |         7200 |       25
    ACC1001 |    2026-05-07 |          AAPL |        18400 |       90
    ACC1001 |    2026-05-07 |          AMZN |         8500 |       35
    ACC1001 |    2026-05-07 |          GOOG |        14000 |       45
    ACC1001 |    2026-05-07 |          MSFT |        10100 |       60
    ACC1001 |    2026-05-07 |          TSLA |         6100 |       20
    ACC2001 |    2026-05-08 |           IBM |         8700 |       65
    ACC2001 |    2026-05-08 |          META |        14300 |       55
    ACC2001 |    2026-05-08 |          NFLX |         9600 |       30
    ACC2001 |    2026-05-08 |          NVDA |        31000 |       70
    ACC2001 |    2026-05-08 |          ORCL |         9200 |       80



--------------------




1. LIMIT 1 -> get latest date
2. Query all rows for that date



ACC1001 Partition
|
|-- 2026-05-09
|      |-- AAPL
|      |-- AMZN
|      |-- GOOG
|      |-- MSFT
|      |-- TSLA
|
|-- 2026-05-08
|      |-- AAPL
|      |-- AMZN
|      |-- GOOG
|      |-- MSFT
|      |-- TSLA
|
|-- 2026-05-07
|
|-- 2026-05-01


How Cassandra Stores This
Partition Key
(account_id)

So all rows for:

ACC1001

go into one partition.

Inside Partition

Rows are sorted by clustering columns:

business_date DESC,
share_id ASC


