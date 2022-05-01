/*
 * Copyright 2021 Google LLC
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at

 * https://www.apache.org/licenses/LICENSE-2.0

 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 *limitations under the License.
*/

/*
 * Retrieves the conversions from the last 5 days for the specified Co-Op Configuration.
 * Since Google Ads deduplicates conversions, it is safe to send the same conversions
 * for some days to cover any missing days due to data availability.
 * The conversions follow the correct Google Ads Offline Conversions Import format
 * documented here: https://support.google.com/google-ads/answer/7014069?hl=en#zippy=
*/

SELECT
    coop_gclid as Google_Click_ID,
    'Offline_Conversions_{{ params['name'] }}_Co-Op4All' AS Conversion_Name,
    CONCAT(CAST(transaction_datetime AS STRING), ' {{ params['time_zone'] }}') AS Conversion_Time,
    SUM(item_revenue) AS Conversion_Value,
    '{{ params['currency'] }}' AS Conversion_Currency
FROM {{ params['retailer_name'] }}.{{ params['name']}}
WHERE
    transaction_datetime BETWEEN CAST(FORMAT_DATE('%Y-%m-%d', DATE_SUB(CURRENT_DATE(), INTERVAL 5 DAY)) AS DATE)
    AND CAST(FORMAT_DATE('%Y-%m-%d', CURRENT_DATE()) AS DATE)
    AND coop_gclid IS NOT NULL
GROUP BY coop_gclid, transaction_datetime
