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

from flask import jsonify
import utils
from . import logs
from core.exceptions.coop_exception import CoopException
from google.cloud import logging
from datetime import datetime, timedelta

LOGGER_NAME = 'coop4all.logs_route'
logger = utils.get_coop_logger(LOGGER_NAME)
client = logging.Client()

@logs.route("/api/logs", methods=["GET"])
def list_logs():
    filter_date = datetime.utcnow() - timedelta(days=1)
    filter_date = filter_date.isoformat(timespec='seconds')
    filter_string = f'timestamp >= "{filter_date}"'
    coop_logs = client.logger('app')

    try:
        entries = coop_logs.list_entries(filter_=filter_string)
    except Exception as error:
        error = utils.build_error(error)
        logger.error('Logs Route - %s' % (error['message']))
        raise CoopException(error['message'], status_code=error['status_code'])

    logs = []
    for entry in entries:
        logs.append({
            'date': entry.timestamp,
            'message': entry.payload.get('message')
        })
    return jsonify(logs), 200

# Exception Handler
@logs.errorhandler(CoopException)
def handle_coop_exception(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response