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
from googleapiclient import discovery
import google.auth

LOGGER_NAME = 'coop4all.dv360_cm_service'
logger = utils.get_coop_logger(LOGGER_NAME)
API_SCOPES = ['https://www.googleapis.com/auth/dfareporting',
            'https://www.googleapis.com/auth/dfatrafficking',
            'https://www.googleapis.com/auth/ddmconversions']

class DV360CMService():
    '''DV360/CM service that retrieves conversions for a specific
    Co-Op Configuration.

    Attributes:
        bq_service: Service that handles all the BigQuery operations
        service: The Campaign Manager service to access the API
    '''

    def __init__(self, bq_service):
        self.bq_service = bq_service
        credentials, project = google.auth.default(scopes=API_SCOPES)
        self.__build_dv360_cm_service(credentials)

    def __build_dv360_cm_service(self, credentials):
        '''Creates the DV60/CM service'''
        self.service = discovery.build('dfareporting', 'v3.5', credentials=credentials)

    def __build_conversions(self, conversions, floodlight_activity_id, floodlight_configuration_id):
        ''' Builds a list of offline conversions in the correct format for the request.

            Args:
              conversions (list): A list of offline conversions from the retailer's Google
              Analytics account.
              floodlight_activity_id (int): The Floodlight Activity where the offline conversion
              will be sent to.
              floodlight_configuration_id (int): The Floodlight Configuration where the offline
              conversion will be sent to.

            Returns:
              conversions_upload (list): A list of conversions in the correct format to
              send in the offline conversions request.
        '''
        conversions_upload = []
        for index, conversion in conversions.iterrows():
            conversion_obj = {
                "kind": "dfareporting#conversion",
                'floodlightActivityId': floodlight_activity_id,
                'floodlightConfigurationId': floodlight_configuration_id,
                'ordinal': 1,
                'timestampMicros': conversion['Conversion_Timestamp'],
                'dclid': conversion['Google_Click_ID'],
                "quantity": conversion['Conversion_Quantity'],
                "value": conversion['Conversion_Value']
            }
            conversions_upload.append(conversion_obj)
        return conversions_upload

    def upload_conversions(self, model_config):
        '''Builds and executes offline conversion requests using the Campaign Manager API

            Args:
              coop_config (CoopCampaignConfig): A pydantic model representing a CoopConfig.???

            Returns:
              execution (dict): A dict containing the status of the requests execution
        '''
        execution = {
            "success": [],
            "errors": []
        }
        dv60_cm_params = [destination for destination in model_config.get('destinations')
            if destination["type"] == 'dv360']
        coop_config_name = model_config.get('name')
        cm_profile_id = dv60_cm_params[0]["cm_profile_id"]
        floodlight_activity_id = dv60_cm_params[0]["floodlight_activity_id"]
        floodlight_configuration_id = dv60_cm_params[0]["floodlight_configuration_id"]
        conversions = self.bq_service.get_table_data(
            'sql/get_dv360_cm_conversions.sql', model_config)
        conversions_upload = self.__build_conversions(conversions, floodlight_activity_id,
            floodlight_configuration_id)
        # Create conversion batches to handle request limit <= 1000 conversions per request.
        conversion_batches = [conversions_upload[i:i + 1000]
                              for i in range(0, len(conversions_upload), 1000)]
        for index, conversions in enumerate(conversion_batches):
            request_body = {
                'conversions': conversions
            }
            request = self.service.conversions().batchinsert(
                profileId=cm_profile_id, body=request_body)
            response = request.execute()
            log_message = f'DV30CMService - upload_conversions Co-Op Config {coop_config_name} - ' \
                 f'Conversions batch {index} CM Profile: {cm_profile_id} ' \
                 f'Floodlight Activity ID: {floodlight_activity_id} ' \
                 f'Floodlight Configuration ID: {floodlight_configuration_id}.\n'
            if response['hasFailures']:
                status = response['status'][0]
                for error in status['errors']:
                    error_code = error['code']
                    error_message = error['message']
                    message = f'There was an error while uploading the conversions to DV360/CM: {error_code} - {error_message}'
                    execution["errors"].append(log_message + message)
                    logger.error(log_message + message)
            else:
                logger.info(log_message + ' was uploaded successfully.')
                execution["success"].append(log_message + ' was uploaded successfully.')
        return execution
