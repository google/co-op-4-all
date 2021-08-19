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
from core.services.google_ads_service import GoogleAdsService

coop_service = CoopService()
LOGGER_NAME = 'coop4all.scheduler_route'
logger = utils.get_coop_logger(LOGGER_NAME)

@scheduler.route("/api/scheduler/update_all_configs", methods=["POST"])
def update_all_configs():
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
        #TODO: Move this logic to the CoopService
        coop_config = coop_service.get_config('CoopCampaignConfig', name)
        retailer = coop_service.get_config('RetailerConfig', coop_config['retailer_name'])
        if not retailer:
            raise CoopException('The retailer was not found.', status_code=404)
        if not coop_config:
            raise CoopException('The Co-Op config was not found.', status_code=404)
        coop_name = coop_config["name"]
        if coop_config['is_active']:
            # Creating a dict for the BqService params
            coop_config_params = dict(coop_config)
            coop_config_params['currency'] = retailer['currency']
            coop_config_params['time_zone'] = retailer['time_zone']
            google_ads_service = GoogleAdsService(coop_config_params)
            conversions = google_ads_service.get_conversions()
            if not conversions:
                raise CoopException(f'There was a problem getting' \
                f'the conversions for the Co-Op Config {coop_name}.', status_code=500)
            response = Response(response=conversions,
                                status=200, mimetype="text/csv")
            response.headers["Content-Type"] = "text/csv"
            logger.info(f'Scheduler Configs Route - Conversions for the Co-Op Config {coop_name}' \
                'were sent successfully!')
            return response
        else:
            logger.info(
                f'Scheduler Configs Route - The Co-Op Config {coop_name} is inactive.' \
                'Conversions were not sent to Google Ads.')
            return '', 204
    except Exception as error:
        error = utils.build_error(error)
        logger.error('Scheduler Configs Route - %s' % (error['message']))
        raise CoopException(error['message'], status_code=error['status_code'])

# Exception Handler
@scheduler.errorhandler(CoopException)
def handle_coop_exception(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response