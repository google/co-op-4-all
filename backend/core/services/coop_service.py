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

import logging
from datetime import date, datetime, timedelta
import re
from zoneinfo import ZoneInfo

from .bigquery_service import BigqueryService
from .datastore_service import DatastoreClient


class CoopService():
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
        model_params = model.dict(exclude_none=True)
        config = self.ds_client.add(model_type, model_params)
        if config:
            self.bq_client.create(model_type, model_params)
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
        config = self.ds_client.update(model_type, model_params)
        if config:
            self.bq_client.update(model_type, model_params)
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

        last_update = retailer_config.get('bq_update_at')
        time_zone = retailer_config.get('timze_zone')
        current_date = datetime.now(ZoneInfo(time_zone))

        return not last_update or last_update.day < current_date.day
    
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
        clicks_table = f'{retailer_name}.all_clicks'
        clicks_table_info = self.bq_client.get_table_info(clicks_table)
        click_table_modified_at = clicks_table_info.get('modified_at')
        coop_table = f'{retailer_name}.{coop_config["name"]}'
        coop_table_info = self.bq_client.get_table_info(coop_table)
        coop_modified_at = coop_table_info.get('modified_at')

        return coop_modified_at < click_table_modified_at

    def update_all(self):
        """Checks each retailer and campaign and updates if needed.
        """

        retailer_configs = self.ds_client.get_all('RetailerConfig')
        coop_configs = self.ds_client.get_all('CoopCampaignConfig')

        for retailer_config in retailer_configs:

            if self.bq_client.ga_table_ready(retailer_config):
                retailer_name = retailer_config.get('name')
                time_zone = retailer_config.get('time_zone')
                current_date = datetime.now(ZoneInfo(time_zone))

                if self.retailer_ready(retailer_config):
                    self.bq_client.update('RetailerConfig', retailer_config)
                    retailer_config['bq_updated_at'] = current_date
                    self.ds_client.update('RetailerConfig', retailer_config)
                    logging.info(
                        f'CoopService - update_all - Updated \
                        {retailer_name} all_cliaks and all_transactions tables.')
                else:
                    for coop_config in coop_configs:

                        if coop_config['retailer_name'] == retailer_name:

                            if self.coop_campaign_ready(retailer_config, coop_config):
                                self.bq_client.update('CoopCampaignConfig', coop_config)
                                logging.info(
                                    f'CoopService - update_all - Updated \
                                    {coop_config["name"]} table')
