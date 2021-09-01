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

from flask import jsonify, Response
import utils
from . import scheduler
from core.exceptions.coop_exception import CoopException
from core.services.coop_service import CoopService

coop_service = CoopService()
LOGGER_NAME = 'coop4all.scheduler_route'
logger = utils.get_coop_logger(LOGGER_NAME)

@scheduler.route("/api/scheduler/update_all_configs", methods=["GET"])
def update_all_configs():
    '''Endpoint to update all the Co-Op Configurations by checking if
    the Google Analytics data is available.
    '''

    try:
        coop_service.update_all()
        return "", 200
    except Exception as error:
        error = utils.build_error(error)
        logger.error('Scheduler Route - %s' % (error['message']))
        raise CoopException(error['message'], status_code=error['status_code'])

@scheduler.route("/api/scheduler/get_google_ads_conversions/<string:name>", methods=["GET"])
def get_google_ads_conversions(name):
    '''Endpoint to retrieve the Google Ads conversions for
    the specified Co-Op Configuration.

        Args:
        name (str): The Co-Op Configuration name.

        Returns:
        conversions (str): a list of Google Ads conversions in csv format.
    '''
    try:
        conversions = coop_service.get_google_ads_conversions(name)
        if conversions:
            response = Response(response=conversions,
                                status=200, mimetype="text/csv")
            response.headers["Content-Type"] = "text/csv"
            logger.info(f'Scheduler Configs Route - get_google_ads_conversions - ' \
            f'Conversions for the Co-Op Config {name} were sent successfully to Google Ads!')
            return response
        else:
            logger.log(f'Scheduler Configs Route - get_google_ads_conversions - ' \
            f'Conversions not found for the Co-Op Config {name}')
            return f'Conversions not found for the Co-Op Config {name}', 204
    except Exception as error:
        error = utils.build_error(error)
        logger.error('Scheduler Configs Route - %s' % (error['message']))
        raise CoopException(error['message'], status_code=error['status_code'])

@scheduler.route("/api/scheduler/push_dv360_cm_conversions", methods=["GET"])
def push_dv360_cm_conversions():
    '''Endpoint to push the DV360/CM conversions for all the Co-Op Configurations'''

    try:
        coop_service.push_dv360_cm_conversions()
        return f'The conversions for all the Co-Op Configs were processed! ' \
        f'Please check the logs in case there is any error.', 200
    except Exception as error:
        error = utils.build_error(error)
        logger.error('Scheduler Route - %s' % (error['message']))
        raise CoopException(error['message'], status_code=error['status_code'])

# Exception Handler
@scheduler.errorhandler(CoopException)
def handle_coop_exception(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response