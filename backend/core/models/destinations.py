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

from typing import Literal
from pydantic import BaseModel, constr


class GoogleAdsDestination(BaseModel):
    type: Literal["google_ads"]
    customer_id: constr(regex="^([0-9]{3})-([0-9]{3})-([0-9]{4})$")


class Dv360Destination(BaseModel):
    type: Literal["dv360"]
    floodlight_activity_id: constr(regex="^[0-9]{3,11}$")
    floodlight_configuration_id: constr(regex="^[0-9]{3,11}$")
    cm_profile_id: constr(regex="^[0-9]{3,11}$")
