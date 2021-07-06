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

from datetime import datetime, timezone
from typing import List, Optional, Union
from pydantic import BaseModel, conint, conlist, constr, validator
from core.models.destinations import Dv360Destination, GoogleAdsDestination


class Filter(BaseModel):
    type: str
    data: conlist(str, min_items=1)


class RetailerConfig(BaseModel):
    name: constr(regex="^[A-Za-z0-9\_]{3,50}$")
    bq_ga_table: constr(regex="^([A-Za-z0-9\-]{6,30})\.([A-Za-z0-9\_]{1,30})\.(events\_\*)$")
    time_zone: constr(regex="^[A-Za-z\_\/]{3,25}$")
    currency: constr(regex="^[A-Za-z]{3}$")
    coop_max_backfill: conint(ge=30, le=180) = 90
    is_active: bool = True
    created_at: datetime = None
    modified_at: datetime = None
    bq_updated_at: datetime = None

    @validator('created_at', pre=True, always=True)
    def default_ts_created(cls, v):
        return v or datetime.now(timezone.utc)

    @validator('modified_at', pre=True, always=True)
    def default_ts_updated(cls, v):
        return datetime.now(timezone.utc)


class CoopCampaignConfig(BaseModel):
    name: constr(regex="^[A-Za-z0-9\_]{3,50}$")
    retailer_name: constr(regex="^[A-Za-z0-9\_]{3,50}$")
    utm_campaigns: conlist(str, min_items=1)
    filters: List[Filter]
    destinations: Optional[List[Union[GoogleAdsDestination, Dv360Destination]]]
    attribution_window: conint(ge=1, le=30) = 7
    is_active: bool = True
    created_at: datetime = None
    modified_at: datetime = None
    bq_updated_at: datetime = None

    @validator('created_at', pre=True, always=True)
    def default_ts_created(cls, v):
        return v or datetime.now(timezone.utc)

    @validator('modified_at', pre=True, always=True)
    def default_ts_updated(cls, v):
        return datetime.now(timezone.utc)
