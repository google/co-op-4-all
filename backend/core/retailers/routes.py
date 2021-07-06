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

from flask import abort, jsonify, request
from . import retailers
from pydantic import ValidationError
from core.models.configurations import RetailerConfig
from core.services.coop_service import CoopService

coop_service = CoopService()

@retailers.route("/api/retailers", methods=["GET"])
def list_retailers():
    configs = coop_service.get_all('RetailerConfig')
    return jsonify(configs)

@retailers.route("/api/retailers/<string:name>", methods=["GET"])
def get_retailer(name):
    config = coop_service.get_config('RetailerConfig', name)
    if not config:
        abort(404)
    return jsonify(config)

@retailers.route("/api/retailers", methods=["POST"])
def add_retailer():
    data = dict(request.json)
    try:
        config = RetailerConfig(**data)
    except ValidationError as e:
        return jsonify(e.json()), 422
    new_config = coop_service.create_config(config)
    if not new_config:
        abort(409)
    return "", 201

@retailers.route("/api/retailers/<string:name>", methods=["PUT"])
def update_retailer(name):
    data = dict(request.json)
    try:
        config = RetailerConfig(**data)
    except ValidationError as e:
        return jsonify(e.json()), 422
    update = coop_service.update_config(config)
    if not update:
        abort(404)
    return "", 200

@retailers.route("/api/retailers/<string:name>", methods=["DELETE"])
def delete_retailer(name):
    config = coop_service.delete_config('RetailerConfig', name)
    if not config:
        abort(404)
    return "", 204
