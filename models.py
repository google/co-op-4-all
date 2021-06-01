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
from typing import Literal, List, Optional, Union
from pydantic import BaseModel, constr, conint, conlist, Field, validator
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

    @classmethod
    def delete(cls, name):
        key = db_client.key(cls.__name__, name)
        db_client.delete(key)

    def add(self):
        with db_client.transaction() as t:
            key = db_client.key(self.__class__.__name__, self.name)
            entity = db_client.get(key)
            if entity:
                return None
            entity = datastore.Entity(key)
            entity.update(self.dict(exclude_none=True))
            t.put(entity)
        return entity

    def update(self, name):
        self.name = name
        with db_client.transaction() as t:
            key = db_client.key(self.__class__.__name__, name)
            entity = db_client.get(key)
            if not entity:
                return None
            entity = datastore.Entity(key)
            entity.update(self.dict(exclude_none=True))
            t.put(entity)
        return entity


class Filter(BaseModel):
    type: str
    data: conlist(str, min_items=1)


class GoogleAdsDestination(BaseModel):
    type: Literal["google_ads"]
    google_ads_customer_id: constr(regex="^[0-9\-]{11}$")


class Dv360Destination(BaseModel):
    type: Literal["dv360"]
    floodlight_activity_id: constr(regex="^[0-9]{3,11}$")
    floodlight_configuration_id: constr(regex="^[0-9]{3,11}$")
    cm_profile_id: constr(regex="^[0-9]{3,11}$")


class RetailerConfig(DbModel):
    name: constr(regex="^[A-Za-z0-9\_]{3,50}$")
    bq_ga_table: constr(regex="^[A-Za-z0-9\-\.]{10,50}events_$")
    time_zone: constr(regex="^[A-Za-z\_\/]{3,25}$")
    max_backfill: int = 3
    is_active: bool = True
    created_at: datetime = None
    modified_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('created_at', pre=True, always=True)
    def default_ts_created(cls, v):
        return v or datetime.utcnow()


class CoopCampaignConfig(DbModel):
    name: constr(regex="^[A-Za-z0-9\_]{3,50}$")
    retailer_name: constr(regex="^[A-Za-z0-9\_]{3,50}$")
    utm_campaigns: conlist(str, min_items=1)
    filters: List[Filter]
    destinations: Optional[List[Union[GoogleAdsDestination, Dv360Destination]]]
    attribution_window: conint(gt=1, lt=30) = 7
    is_active: bool = True
    created_at: datetime = None
    modified_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('created_at', pre=True, always=True)
    def default_ts_created(cls, v):
        return v or datetime.utcnow()
