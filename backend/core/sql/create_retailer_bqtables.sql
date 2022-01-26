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

-- Create 2 tables and 1 dataset, all_transactions and all_clicks with paramters from a RetailerConfiguration.

-- Table all_clicks contains all sessions with a gclid or dclid as an event_parameter.
-- Table all_transactions purchase events with ecommerce information.

CREATE SCHEMA IF NOT EXISTS {{ params['name'] }};

CREATE TABLE IF NOT EXISTS
  {{ params['name'] }}.all_transactions(
    user_pseudo_id STRING,
    transaction_date DATE,
    transaction_datetime DATETIME,
    transaction_timestamp INTEGER,
    transaction_id STRING,
    session_number INT64,
    item_id STRING,
    item_name STRING,
    item_brand STRING,
    quantity INT64,
    price FLOAT64,
    item_revenue FLOAT64
)
PARTITION BY
  transaction_date
OPTIONS
  (partition_expiration_days={{ params['coop_max_backfill'] }}); -- 90 days by default

INSERT
  {{ params['name'] }}.all_transactions
SELECT DISTINCT
  user_pseudo_id,
  PARSE_DATE('%Y%m%d', event_date) AS transaction_date,
  DATETIME(TIMESTAMP_MICROS(event_timestamp),'{{ params['time_zone'] }}') AS transaction_datetime,
  event_timestamp as transaction_timestamp,
  (SELECT value.string_value FROM UNNEST(event_params) WHERE key = 'transaction_id') AS transaction_id,
  (SELECT value.int_value FROM UNNEST(event_params) WHERE key = 'ga_session_number') AS session_number,
  it.item_id,
  it.item_name,
  it.item_brand,
  it.quantity,
  it.price,
  it.item_revenue
FROM `{{ params['bq_ga_table'] }}`, UNNEST(items) it
WHERE
  event_name = 'purchase'
  AND _TABLE_SUFFIX BETWEEN FORMAT_DATE('%Y%m%d',DATE_SUB(CURRENT_DATE(), INTERVAL 3 DAY))
  AND FORMAT_DATE('%Y%m%d',CURRENT_DATE('{{ params['time_zone'] }}'));


CREATE TABLE IF NOT EXISTS
  {{ params['name'] }}.all_clicks(
    user_pseudo_id STRING,
    session_number INT64,
    coop_campaign STRING,
    coop_gclid STRING,
    coop_dclid STRING,
    click_date DATE,
    click_datetime DATETIME
)
PARTITION BY
  click_date
OPTIONS
  (partition_expiration_days={{ params['coop_max_backfill'] }} + 30); -- To account for attribution. The transaction could happen on the first day, and a click has to happen within 30 days prior.

INSERT
  {{ params['name'] }}.all_clicks
SELECT
  user_pseudo_id,
  session_number,
  coop_campaign,
  coop_gclid,
  coop_dclid,
  click_date,
  MIN(event_datetime) AS click_datetime -- The first occurrence of gclid in an event, there could be several events with the same gclid (page view, etc)
FROM (
  SELECT
    user_pseudo_id,
    PARSE_DATE('%Y%m%d', event_date) AS click_date,
    DATETIME(TIMESTAMP_MICROS(event_timestamp),'{{ params['time_zone'] }}') event_datetime,
    (SELECT value.int_value FROM UNNEST(event_params) WHERE key = 'ga_session_number') as session_number,
    (SELECT value.string_value FROM UNNEST(event_params) WHERE key = 'coop_campaign') as coop_campaign,
    (SELECT value.string_value FROM UNNEST(event_params) WHERE key = 'coop_gclid') as coop_gclid,
    (SELECT value.string_value FROM UNNEST(event_params) WHERE key = 'coop_dclid') as coop_dclid
  FROM
    `{{ params['bq_ga_table'] }}`
  WHERE
    _TABLE_SUFFIX BETWEEN FORMAT_DATE('%Y%m%d',DATE_SUB(CURRENT_DATE(), INTERVAL 3 DAY))
    AND FORMAT_DATE('%Y%m%d',CURRENT_DATE('{{ params['time_zone'] }}')))
WHERE coop_gclid IS NOT NULL OR coop_dclid IS NOT NULL
GROUP BY 1,2,3,4,5,6
