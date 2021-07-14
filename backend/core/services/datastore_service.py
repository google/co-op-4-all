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


from google.cloud import datastore


class DatastoreClient():
    def __init__(self):
        self.client = datastore.Client()

    def get_all(self, model_type):
        """Get all entities for a specific model_type.

        Args:
            model_type (str): The model type (CoopCampaingConfig or RetailerConfig).

        Returns:
            entities (lst): A list of entities.
        """

        query = self.client.query(kind=model_type)
        entities = list(query.fetch())
        return entities

    def get_by_name(self, model_type, name):
        """Get a Datastore entity by name.

        Args:
            model_type (str): The model type (CoopCampaingConfig or RetailerConfig).
            name (str): The name (key) of the entity
            (retailer name or coopconfig name).

        Returns:
            entity (datastore.Entity)
        """

        key = self.client.key(model_type, name)
        entity = self.client.get(key)
        if entity:
            return entity

    def delete(self, model_type, name):
        """Delete an entity in datastore.

        Args:
            model_type (str): The model type (CoopCampaingConfig or RetailerConfig).
            name (str): The name (key) of the entity to delete
            (retailer name or coopconfig name).

        Returns:
            entity (datastore.Entity): The deleted entity.
        """

        key = self.client.key(model_type, name)
        entity = self.client.get(key)
        if entity:
            self.client.delete(key)
        return entity

    def delete_multi(self, model_type, name, field):
        """Delete multiple keys in a single transaction.

        Args:
            model_type (str): The model type (CoopCampaingConfig or RetailerConfig).
            name (str): The name (key) of the entity to delete
            (retailer name or coopconfig name).
            field (str): The field name to filter by.

        Returns:
            None
        """

        query = self.client.query(kind=model_type)
        query.keys_only()
        query.add_filter(field, '=', name)
        keys = list([entity for entity in query.fetch()])
        self.client.delete_multi(keys)

    def add(self, model_type, model_params):
        """Saves the model to Datastore.

        Args:
            model_type (str): The model type (CoopCampaingConfig or RetailerConfig).
            or a RetailerConfig.
            model_params (dict): Model parameters to save in datastore.

        Returns:
            entity (datastore.Entity): The new entity created.
        """

        with self.client.transaction() as t:
            key = self.client.key(model_type, model_params['name'])
            entity = self.client.get(key)
            if not entity:
                entity = datastore.Entity(key)
                entity.update(model_params)
                t.put(entity)
                return entity

    def update(self, model_type, model_params):
        """Updates the model in Datastore.

        Args:
            model_type (str): The model type (CoopCampaingConfig or RetailerConfig).
            or a RetailerConfig.
            model_params (dict): Model parameters to update in datastore.

        Returns:
            entity (datastore.Entity): The updated entity.
        """

        with self.client.transaction() as t:
            key = self.client.key(model_type, model_params['name'])
            entity = self.client.get(key)
            if entity:
                entity = datastore.Entity(key)
                entity.update(model_params)
                t.put(entity)
                return entity
