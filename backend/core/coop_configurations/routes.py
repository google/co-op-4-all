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
from . import coop_configurations
from pydantic import ValidationError
from core.models.configurations import CoopCampaignConfig

@coop_configurations.route("/api/co_op_campaigns", methods=["GET"])
def list_co_op_campaigns():
    configs = CoopCampaignConfig.get_all()
    return jsonify(configs)

@coop_configurations.route("/api/co_op_campaigns", methods=["POST"])
def add_co_op_campaign():
    data = dict(request.json)
    try:
        config = CoopCampaignConfig(**data)
    except ValidationError as e:
        return jsonify(e.json()), 422
    new_config = config.add()
    if not new_config:
        abort(409)
    return "", 201

@coop_configurations.route("/api/co_op_campaigns/<string:name>", methods=["GET"])
def get_co_op_campaign(name):
    config = CoopCampaignConfig.get(name)
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
    update = config.update(name)
    if not update:
        abort(404)
    return "", 200

@coop_configurations.route("/api/co_op_campaigns/<string:name>", methods=["DELETE"])
def delete_co_op_campaign(name):
    config = CoopCampaignConfig.get(name)
    if not config:
        abort(404)
    CoopCampaignConfig.delete(name)
    return "", 204