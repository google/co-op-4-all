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

from datetime import datetime
from typing import Literal
from pydantic import BaseModel, constr, conlist, Field
from google.cloud import datastore

db_client = datastore.Client()


class DbModel(BaseModel):
    @classmethod
    def get_all(cls):
        query = db_client.query(kind=cls.__name__)
        results = list(query.fetch())
        return results

    @classmethod
    def get(cls, name):
        key = db_client.key(cls.__name__, name)
        result = db_client.get(key)
        return result

    def add(self):
        with db_client.transaction() as t:
            key = db_client.key(self.__class__.__name__, self.name)
            entity = db_client.get(key)
            if entity:
                return None
            entity = datastore.Entity(key)
            entity.update(self.dict())
            t.put(entity)
        return entity

    def update(self, name):
        with db_client.transaction() as t:
            key = db_client.key(self.__class__.__name__, name)
            entity = db_client.get(key)
            if not entity:
                return None
            entity = datastore.Entity(key)
            entity.update(self.dict())
            t.put(entity)
        return entity


class RetailerConfig(DbModel):
    name: constr(regex="^[A-Za-z0-9\_ ]{3,50}$")
    bq_ga_table: constr(regex="^[A-Za-z0-9\-\.]{10,50}events_$")
    bq_retailer_dataset: constr(regex="^[A-Za-z0-9\_]{3,50}$")
    time_zone: constr(regex="^[A-Za-z\_\/]{3,25}$")
    max_backfill: int = 60
    is_active: bool = True


class GoopConfig(DbModel):
    name: constr(regex="^[A-Za-z0-9\_]{3,50}$")
    retailer_name: constr(regex="^[A-Za-z0-9\_ ]{3,50}$")
    product_filter_type:  Literal["sku", "product_id", "product_name"]
    utm_campaigns: conlist(str, min_items=1)
    products: conlist(str, min_items=1)
    created_at: datetime = Field(default_factory=datetime.now)
    ads_account_id: constr(regex="^[0-9\-]{11}$")
    floodlight_activit_id: constr(regex="^[0-9]{3,11}$") = None
    floodlight_config_id: constr(regex="^[0-9]{3,11}$") = None
    cm_profile_id: constr(regex="^[0-9]{3,11}$") = None
    is_active: bool = True
