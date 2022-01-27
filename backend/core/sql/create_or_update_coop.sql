/*
Copyright 2021 Google LLC
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

-- Creates a table based on a CoopCampaingConfiguration parameters.

-- Joins all_transactions and all_clicks.
-- Filters specific products from all_transactions.
-- Filters specific utm_campaings from all_clicks.
-- Filters sessions that occurs within an attribution_window (in days) before a transaction.


CREATE OR REPLACE TABLE
  {{ params['retailer_name'] }}.{{ params['name']}} AS -- The table is always replaced with new data

WITH coop_transactions AS (
SELECT
  t.* EXCEPT(user_pseudo_id, session_number),
  c.coop_campaign,
  c.coop_gclid,
  c.coop_dclid,
  c.click_datetime
FROM
  {{ params['retailer_name'] }}.all_clicks c
INNER JOIN
  {{ params['retailer_name'] }}.all_transactions t
USING(user_pseudo_id)
WHERE
  c.click_datetime <= t.transaction_datetime -- To get a click that is before a transaction
  AND c.click_datetime >= DATE_SUB(t.transaction_datetime, INTERVAL {{ params['attribution_window'] }} DAY) -- And within the attribution window (30 days by default)
  AND coop_campaign IN ({{ params['utm_campaigns'] | map('tojson') | join(', ')}})
  {% for filter in params['filters'] %}
  AND {{ filter['type'] }} IN ({{filter['data'] | map('tojson') | join(', ')}})
  {% endfor %}
)
SELECT
  transaction_id,
  transaction_date,
  transaction_datetime,
  transaction_timestamp,
  coop_campaign,
  coop_gclid,
  coop_dclid,
  item_id,
  item_name,
  item_brand,
  quantity,
  ROUND(price, 2) AS price,
  ROUND(item_revenue, 2) AS item_revenue,
  '{{ params['name'] }}' AS coop_name
FROM (
  SELECT
    transaction_id,
    MAX(click_datetime) AS click_datetime -- Transactions might be duplicated, the latest is selected
  FROM
    coop_transactions
  GROUP BY 1)
INNER JOIN
  coop_transactions
USING (transaction_id, click_datetime)
