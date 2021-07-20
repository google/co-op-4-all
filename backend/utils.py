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

from datetime import date
from flask.json import JSONEncoder
import logging
from google.cloud import logging as gcp_logging

client = gcp_logging.Client()
handler = client.get_default_handler()

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()
        return super().default(obj)

def get_coop_logger(name):
    cloud_logger = logging.getLogger(name)
    cloud_logger.setLevel(logging.INFO)
    cloud_logger.addHandler(handler)
    return cloud_logger

def build_error(error):
    message = error.message if hasattr(error, 'message') else str(error)
    status_code = error.status_code if hasattr(error, 'status_code') else 500
    error = {
        'message': message,
        'status_code': status_code
    }
    return error