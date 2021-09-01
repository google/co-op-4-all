# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import utils

LOGGER_NAME = 'coop4all.google_ads_service'
logger = utils.get_coop_logger(LOGGER_NAME)

class GoogleAdsService():
    '''Google Ads service that retrieves conversions for a specific
    Co-Op Configuration.

    Attributes:
        bq_service: Service that handles all the BigQuery operations
    '''

    def __init__(self, bq_client):
        self.bq_client = bq_client

    def __get_formatted_conversions(self, sql_file, model_config):
        '''Formats the retrieved rows of the specified query by removing
        the column underscores to match the conversions format.

            Args:
            sql_file (str): The query to be executed.

            Returns:
                conversions (list): A list of formatted conversions
        '''
        conversions = self.bq_client.get_table_data(sql_file, model_config)
        for h in conversions.columns.values.tolist():
            conversions[h.replace("_", " ")] = conversions[h]
            del conversions[h]
        return conversions

    def get_conversions(self, model_config):
        '''Gets conversions as csv format to be sent to the manufacturer's
        Google Ads account.

            Args:
                model_config: A mixed model representing a CoopConfig but including
            RetailerConfig params.

            Returns:
                csv: A list of conversions as csv format with the required
                columns and format for Offline Conversions Import in Google Ads.
        '''
        try:
            conversions = self.__get_formatted_conversions('sql/get_google_ads_conversions.sql', model_config)
            csv = conversions.to_csv(sep=',', index=False, encoding='utf-8')
            return csv
        except Exception as error:
            logger.error(f'GoogleAdsService - get_conversions - Error getting the conversions' \
                f'for the Co-Op Config { model_config["name"] } Error: { str(error) }')
        return None
