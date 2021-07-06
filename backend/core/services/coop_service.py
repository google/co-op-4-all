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

from . bigquery_service import BigqueryService
from . datastore_service import DatastoreClient

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

        config = self.ds_client.add(model)
        if config:
            self.bq_client.create(model)
        return config

    def update_config(self, model):
        """Updates the entity in datastore and tables in BigQuery.

        Args:
            model: A Pydantic model representing a CoopCampaingConfig
            or a RetailerConfig.

        Returns:
            config (datastore.Entity): The updated entity.
        """

        config = self.ds_client.update(model)
        if config:
            self.bq_client.update(model)
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