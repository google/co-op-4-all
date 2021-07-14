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

from flask import abort, jsonify, request, Response
import logging
from . import coop_configurations
from pydantic import ValidationError
from core.models.configurations import CoopCampaignConfig
from core.services.google_ads_service import GoogleAdsService
from core.services.coop_service import CoopService

coop_service = CoopService()

@coop_configurations.route("/api/co_op_campaigns", methods=["GET"])
def list_co_op_campaigns():
    configs = coop_service.get_all('CoopCampaignConfig')
    return jsonify(configs)

@coop_configurations.route("/api/co_op_campaigns", methods=["POST"])
def add_co_op_campaign():
    data = dict(request.json)
    try:
        config = CoopCampaignConfig(**data)
    except ValidationError as e:
        return jsonify(e.json()), 422
    new_config = coop_service.create_config(config)
    if not new_config:
        abort(409)
    return "", 201

@coop_configurations.route("/api/co_op_campaigns/<string:name>", methods=["GET"])
def get_co_op_campaign(name):
    config = coop_service.get_config('CoopCampaignConfig', name)
    if not config:
        abort(404)
    return jsonify(config)

@coop_configurations.route("/api/co_op_campaigns/<string:name>", methods=["PUT"])
def update_co_op_campaign(name):
    data = dict(request.json)
    try:
        config = CoopCampaignConfig(**data)
    except ValidationError as e:
        return jsonify(e.json()), 422
    update = coop_service.update_config(config)
    if not update:
        abort(404)
    return "", 200

@coop_configurations.route("/api/co_op_campaigns/<string:name>", methods=["DELETE"])
def delete_co_op_campaign(name):
    config = coop_service.delete_config('CoopCampaignConfig', name)
    if not config:
        abort(404)
    return "", 204

@coop_configurations.route("/api/co_op_campaigns/get_google_ads_conversions/<string:name>", methods=["GET"])
def get_google_ads_conversions(name):
    '''Endpoint to retrieve the Google Ads conversions for
    the specified Co-Op Configuration.

        Args:
        name (str): The Co-Op Configuration name.

        Returns:
        conversions (str): a list of Google Ads conversions in csv format.
    '''
    coop_config = coop_service.get_config('CoopCampaignConfig', name)
    retailer = coop_service.get_config('RetailerConfig', coop_config['retailer_name'])
    if not coop_config or not retailer:
        abort(404)
    if coop_config['is_active']:
        # Creating a dict for the BqService params
        coop_config_params = dict(coop_config)
        coop_config_params['currency'] = retailer['currency']
        coop_config_params['time_zone'] = retailer['time_zone']
        google_ads_service = GoogleAdsService(coop_config_params)
        conversions = google_ads_service.get_conversions()
        if not conversions:
            return f'There was a problem getting the conversions \
            for the Co-Op Config { coop_config["name"] }', 500
        response = Response(response=conversions,
                            status=200, mimetype="text/csv")
        response.headers["Content-Type"] = "text/csv"
        logging.info(
            f'Coop Configurations Route - get_google_ads_conversions - \
            Conversions for the Co-Op Config {coop_config["name"]} were sent successfully!')
        return response
    else:
        logging.info(
            f'Coop Configurations Route - get_google_ads_conversions - The Co-Op Config \
            {coop_config["name"]} is inactive. Conversions were not sent to Google Ads.')
        return '', 204