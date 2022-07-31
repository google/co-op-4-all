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

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import utils
from core.exceptions.coop_exception import CoopException
from .bigquery_service import BigqueryService
from .datastore_service import DatastoreClient
from .destinations.google_ads_service import GoogleAdsService
from .destinations.dv360_cm_service import DV360CMService

LOGGER_NAME = 'coop4all.coop_service'
logger = utils.get_coop_logger(LOGGER_NAME)

class CoopService():
    '''
    Service that handles all the Co-Op config operations such as create, update, get,
    delete and conversions pull/push

        Attributes:
            bq_client: A service to handle all the BigQuery operations.
            ds_client: A service to handle all the Datastore operations.
    '''

    def __init__(self):
        self.bq_client = BigqueryService()
        self.ds_client = DatastoreClient()

    def create_config(self, model):
        """Saves the model to Datastore and create the
        dataset/table structure in BigQuery.

        Args:
            model: A Pydantic model representing a CoopCampaingConfig
            or a RetailerConfig.

        Returns:
            config (datastore.Entity): The new entity created.
        """

        model_type = model.__class__.__name__
        if model_type == 'RetailerConfig':
            bq_ga_table = model.bq_ga_table
            table = self.bq_client.get_table(bq_ga_table)
            if not table:
                raise CoopException(f'GA4 Table not found at {bq_ga_table}.' \
                    'Please check if table name is correct.', status_code=404)

        model_params = model.dict(exclude_none=True)
        name = model_params['name']
        config = self.ds_client.add(model_type, model_params)
        if config:
            self.bq_client.create(model_type, model_params)
        else:
            logger.warning(f'CoopService - Empty config {model_type}-{name},' \
                'BQ components were not created.')
        return config

    def update_config(self, model):
        """Updates the entity in datastore and tables in BigQuery.

        Args:
            model: A Pydantic model representing a CoopCampaingConfig
            or a RetailerConfig.

        Returns:
            config (datastore.Entity): The updated entity.
        """

        model_type = model.__class__.__name__
        model_params = model.dict(exclude_none=True)
        name = model_params['name']
        config = self.ds_client.update(model_type, model_params)
        if config:
            self.bq_client.update(model_type, model_params)
        else:
            logger.warning(f'CoopService - Empty config {model_type}-{name},' \
                'BQ components were not updated.')
        return config

    def delete_config(self, model_type, name):
        """Deletes the config from Datastore and
        datasets and tables from BgiQuery.

        Args:
            model_type (str): The model type (CoopCampaingConfig or RetailerConfig).
            name (str): The name (key) of the entity to delete
            (retailer name or coopconfig name).

        Returns:
            config (datastore.Entity): The deleted entity.
        """

        config = self.ds_client.delete(model_type, name)
        if config:
            self.bq_client.delete(model_params=config)
            if model_type == 'RetailerConfig':
                self.ds_client.delete_multi(model_type='CoopCampaignConfig',
                                            name=name,
                                            field='retailer_name')
        else:
            logger.warning(f'CoopService - Empty config {model_type}-{name},' \
                'BQ components were not deleted.')
        return config

    def get_config(self, model_type, name):
        """Gets a config model from Datastore.

        Args:
            model_type (str): The model type (CoopCampaingConfig or RetailerConfig).
            name (str): The name (key) of the entity to retrive
            (retailer name or coopconfig name).

        Returns:
            config (datastore.Entity)
        """

        return self.ds_client.get_by_name(model_type, name)

    def get_all(self, model_type):
        """Gets all entities for a model.

        Args:
            model_type (str): The model type (CoopCampaingConfig or RetailerConfig).

        Returns:
            config (lst): A list of entities.
        """

        return self.ds_client.get_all(model_type)

    def retailer_ready(self, retailer_config):
        """Checks if retailer tables are ready to be updated.
        A retailer is ready if there was not an update for the
        current day.

        Args:
            retailer_config (dict): Retailer parameters.

        Returns:
            bool: True if ready, False otherwise.
        """

        last_update = retailer_config.get('bq_updated_at')
        time_zone = retailer_config.get('time_zone')
        current_date = datetime.now(ZoneInfo(time_zone))

        return not last_update or last_update.date() < current_date.date()

    def coop_campaign_ready(self, retailer_config, coop_config):
        """Checks if CoopCampaign table is ready to be updated.
        A CoopCampaing is ready if it was last modified before
        the retailer tables.

        Args:
            coop_config (dict): CoopCampaign parameters.

        Returns:
            bool: True if ready, False otherwise.
        """

        retailer_name = retailer_config.get('name')
        clicks_table_reference = f'{retailer_name}.all_clicks'
        clicks_table = self.bq_client.get_table(clicks_table_reference)
        click_table_modified_at = clicks_table.modified
        coop_table_reference = f'{retailer_name}.{coop_config["name"]}'
        coop_table = self.bq_client.get_table(coop_table_reference)
        coop_modified_at = coop_table.modified

        return coop_modified_at < click_table_modified_at

    def ga_table_ready(self, retailer_config):
        """Checks if the GA4 table from the day before is ready.

        Args:
            model_params (dict): Parameters from a Pydantic Model of
            a CoopCampaignConfig or RetailerConfig.

        Returns:
            bigquery.Table: The most recent GA4 table. Returns None
            if table is not ready.
        """

        table_name = retailer_config.get('bq_ga_table')
        time_zone = retailer_config.get('time_zone')
        date = datetime.strftime(datetime.now(ZoneInfo(time_zone)) - timedelta(1), '%Y%m%d')
        table = self.bq_client.get_table(table_name.replace('*', date))
        if not table:
            logger.info(
                f'CoopService - ga_table_ready - GA4 table' \
                f'{table_name} does not exists or it is not ready.')
        return table

    def update_all(self):
        """Checks each retailer and campaign and updates if needed.
        """

        retailer_configs = self.ds_client.get_all('RetailerConfig')
        coop_configs = self.ds_client.get_all('CoopCampaignConfig')
        logger.info('CoopService - Updating retailers if ready and not updated today...')
        for retailer_config in retailer_configs:
            retailer_name = retailer_config.get('name')
            bq_ga_table = retailer_config.get('bq_ga_table')
            if self.ga_table_ready(retailer_config):
                pass
                # TODO: actual tables update should be here once the the BQ delay is fixed
            else:
                logger.info(f'INFO: The GA table {bq_ga_table} was not ready.')
            # TODO: Move this code inside the ga_table_ready condition once the BQ delay is fixed
            time_zone = retailer_config.get('time_zone')
            current_date = datetime.now(ZoneInfo(time_zone))
            retailer_is_active = retailer_config.get('is_active')
            # Check if retailer has not been updated today, if not, update retailer tables all_transactions/clicks
            if self.retailer_ready(retailer_config) and retailer_is_active:
                logger.info(f'CoopService - GA table {bq_ga_table} ready,' \
                    f'retailer ready and not updated today. Updating retailer {retailer_name}...')
                self.bq_client.update('RetailerConfig', retailer_config)
                retailer_config['bq_updated_at'] = current_date
                self.ds_client.update('RetailerConfig', retailer_config)
                logger.info(
                    f'CoopService - Updated retailer' \
                    f'{retailer_name} all_clicks and all_transactions tables.')
            else:
                logger.info(f'CoopService - Updating coop configs under retailer {retailer_name}' \
                    'if ready and not updated today...')
                for coop_config in coop_configs:
                    coop_config_name = coop_config.get('name')
                    coop_config_is_active = coop_config.get('is_active')
                    if coop_config['retailer_name'] == retailer_name and coop_config_is_active:

                        if self.coop_campaign_ready(retailer_config, coop_config):
                            logger.info(f'CoopService - coop config ready and not updated today.' \
                                f'Updating coop config {coop_config_name}...')
                            self.bq_client.update('CoopCampaignConfig', coop_config)
                            logger.info(
                                f'CoopService - Updated coop config' \
                                f'{coop_config_name} table.')
                        else:
                            logger.info(f'CoopService - Coop config {coop_config_name} was not updated since' \
                                'it was not ready or it was already updated.')

    def get_google_ads_conversions(self, name):
        '''
        Endpoint to retrieve the Google Ads conversions for the specified
        Co-Op Configuration.

            Args:
            name (str): The Co-Op Configuration name.

            Returns:
            conversions (str): a list of Google Ads conversions in csv format.
        '''

        coop_config = self.get_config('CoopCampaignConfig', name)
        retailer = self.get_config('RetailerConfig', coop_config['retailer_name'])
        if not retailer:
            raise CoopException('CoopService - get_google_ads_conversions - ' \
            'The retailer was not found. The conversions were not sent to Google Ads.',
            status_code=404)
        if not coop_config:
            raise CoopException('CoopService - get_google_ads_conversions - '
            'The Co-Op config was not found. The conversions were not sent to Google Ads.',
            status_code=404)
        coop_name = coop_config.get('name')
        if coop_config.get('is_active'):
            # Creating a dict for the BqService params
            coop_config_params = dict(coop_config)
            coop_config_params['currency'] = retailer['currency']
            coop_config_params['time_zone'] = retailer['time_zone']
            google_ads_service = GoogleAdsService(self.bq_client)
            conversions = google_ads_service.get_conversions(coop_config_params)
            if not conversions:
                raise CoopException(f'CoopService - get_google_ads_conversions - ' \
                f'There was a problem getting the conversions for the Co-Op Config {coop_name}.',
                status_code=500)
            return conversions
        else:
            logger.info(
                f'CoopService - get_google_ads_conversions - The Co-Op Config {coop_name} is inactive. ' \
                'Conversions were not sent to Google Ads.')
            return ''

    def push_dv360_cm_conversions(self):
        '''Endpoint to push the DV360/CM conversions for all the Co-Op Configurations'''

        dv360_cm_service = DV360CMService(self.bq_client)
        configs = self.get_all('CoopCampaignConfig')
        for coop_config in configs:
            coop_config_name = coop_config.get('name')
            if coop_config.get('is_active'):
                # Push conversions only if destination is available
                if self.__is_destination_available(coop_config, 'dv360'):
                    dv360_cm_service.upload_conversions(coop_config)
                else:
                    logger.info(f'CoopService - push_dv360_cm_conversions - ' \
                    f'No DV360 Destination available for Co-Op Config {coop_config_name}.')
            else:
                logger.info(f'CoopService - push_dv360_cm_conversions -  The Co-Op ' \
                f'Config {coop_config_name} is disabled. Conversions were not sent to DV360/CM.')

    def __is_destination_available(self, coop_config, destination_type):
        params = [destination for destination in coop_config["destinations"]
                        if destination["type"] == destination_type]
        return len(params) > 0