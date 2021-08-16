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

from flask import jsonify, request
import utils
from . import retailers
from pydantic import ValidationError
from core.models.configurations import RetailerConfig
from core.services.coop_service import CoopService
from core.exceptions.coop_exception import CoopException

coop_service = CoopService()
LOGGER_NAME = 'coop4all.retailers_route'
logger = utils.get_coop_logger(LOGGER_NAME)

@retailers.route("/api/retailers", methods=["GET"])
def list_retailers():
    try:
        configs = coop_service.get_all('RetailerConfig')
        if not configs:
            raise CoopException('The retailers were not found.', status_code=404)
        return jsonify(configs)
    except Exception as error:
        error = utils.build_error(error)
        logger.error('Retailers Route - %s' % (error['message']))
        raise CoopException(error['message'], status_code=error['status_code'])

@retailers.route("/api/retailers/<string:name>", methods=["GET"])
def get_retailer(name):
    try:
        config = coop_service.get_config('RetailerConfig', name)
        if not config:
            raise CoopException('The retailer was not found.', status_code=404)
        return jsonify(config)
    except Exception as error:
        error = utils.build_error(error)
        logger.error('Retailers Route - %s' % (error['message']))
        raise CoopException(error['message'], status_code=error['status_code'])

@retailers.route("/api/retailers", methods=["POST"])
def add_retailer():
    try:
        data = dict(request.json)
        try:
            config = RetailerConfig(**data)
        except ValidationError as error:
            raise CoopException(f'Validation error: {error}', status_code=422)
        new_config = coop_service.create_config(config)
        if not new_config:
            raise CoopException('A retailer with the same name already exists. \
                Please choose another name.', status_code=409)
        return "", 201
    except Exception as error:
        error = utils.build_error(error)
        logger.error('Retailers Route - %s' % (error['message']))
        raise CoopException(error['message'], status_code=error['status_code'])

@retailers.route("/api/retailers/<string:name>", methods=["PUT"])
def update_retailer(name):
    try:
        data = dict(request.json)
        try:
            config = RetailerConfig(**data)
        except ValidationError as error:
            raise CoopException(f'Validation error: {error}', status_code=422)
        updated_config = coop_service.update_config(config)
        if not updated_config:
            raise CoopException('The retailer could not be updated because it was not found. \
            Please check the logs and try again.', status_code=404)
        return "", 200
    except Exception as error:
        error = utils.build_error(error)
        logger.error('Retailers Route - %s' % (error['message']))
        raise CoopException(error['message'], status_code=error['status_code'])

@retailers.route("/api/retailers/<string:name>", methods=["DELETE"])
def delete_retailer(name):
    try:
        config = coop_service.delete_config('RetailerConfig', name)
        if not config:
            raise CoopException('The retailer could not be deleted. \
            Please check the logs try again.', status_code=409)
        return "", 204
    except Exception as error:
        error = utils.build_error(error)
        logger.error('Retailers Route - %s' % (error['message']))
        raise CoopException(error['message'], status_code=error['status_code'])

# Exception Handler
@retailers.errorhandler(CoopException)
def handle_coop_exception(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response
