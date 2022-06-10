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

-- Updates all_clicks and all_transactions tables for a RetailerConfig

DECLARE next_partition DATE;
DECLARE latest_partition DATE;

SET latest_partition = DATE_SUB(CURRENT_DATE('{{ params['time_zone'] }}'), INTERVAL 1 DAY); -- Get latest partition to process, which is 'yesterday'
SET next_partition = ( -- Get latest created/existing partition in BQ (the date until the data was processed correctly, could be N days ago)
    SELECT
      DATE_ADD(PARSE_DATE('%Y%m%d', MAX(partition_id)), INTERVAL 1 DAY)
    FROM
      {{ params['name'] }}.INFORMATION_SCHEMA.PARTITIONS
    WHERE
      table_name IN ('all_clicks', 'all_transactions')
      AND partition_id != '__NULL__'
);

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
  AND _TABLE_SUFFIX BETWEEN FORMAT_DATE('%Y%m%d', next_partition)
  AND FORMAT_DATE('%Y%m%d', latest_partition);

INSERT
  {{ params['name'] }}.all_clicks
SELECT
  user_pseudo_id,
  session_number,
  coop_campaign,
  coop_gclid,
  coop_dclid,
  click_date,
  MIN(event_datetime) AS click_datetime
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
    _TABLE_SUFFIX BETWEEN FORMAT_DATE('%Y%m%d', next_partition)
    AND FORMAT_DATE('%Y%m%d', latest_partition))
WHERE coop_gclid IS NOT NULL OR coop_dclid IS NOT NULL
GROUP BY 1,2,3,4,5,6;

