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

import os

from flask import Flask, abort, jsonify, request
from pydantic import ValidationError

from models.configurations import CoopCampaignConfig, RetailerConfig
from utils import CustomJSONEncoder

app = Flask(__name__)
app.json_encoder = CustomJSONEncoder


@app.route("/api/campaigns", methods=["GET"])
def list_campaigns():
    configs = CoopCampaignConfig.get_all()
    return jsonify(configs)


@app.route("/api/campaigns", methods=["POST"])
def add_campaign():
    data = dict(request.json)
    try:
        config = CoopCampaignConfig(**data)
    except ValidationError as e:
        return jsonify(e.json())
    new_config = config.add()
    if not new_config:
        abort(409)
    return "", 201


@app.route("/api/campaigns/<string:name>", methods=["GET"])
def get_campaign(name):
    config = CoopCampaignConfig.get(name)
    if not config:
        abort(404)
    return jsonify(config)


@app.route("/api/campaigns/<string:name>", methods=["PUT"])
def update_campaign(name):
    data = dict(request.json)
    try:
        config = CoopCampaignConfig(**data)
    except ValidationError as e:
        return jsonify(e.json())
    update = config.update(name)
    if not update:
        abort(404)
    return "", 200


@app.route("/api/campaigns/<string:name>", methods=["DELETE"])
def delete_campaign(name):
    config = CoopCampaignConfig.get(name)
    if not config:
        abort(404)
    CoopCampaignConfig.delete(name)
    return "", 204


@app.route("/api/retailers", methods=["GET"])
def list_retailers():
    configs = RetailerConfig.get_all()
    return jsonify(configs)


@app.route("/api/retailers", methods=["POST"])
def add_retailer():
    data = dict(request.json)
    try:
        config = RetailerConfig(**data)
    except ValidationError as e:
        return jsonify(e.json())
    new_config = config.add()
    if not new_config:
        abort(409)
    return "", 201


@app.route("/api/retailers/<string:name>", methods=["GET"])
def get_retailer(name):
    config = RetailerConfig.get(name)
    if not config:
        abort(404)
    return jsonify(config)


@app.route("/api/retailers/<string:name>", methods=["PUT"])
def update_retailer(name):
    data = dict(request.json)
    try:
        config = RetailerConfig(**data)
    except ValidationError as e:
        return jsonify(e.json())
    update = config.update(name)
    if not update:
        abort(404)
    return "", 200


@app.route("/api/retailers/<string:name>", methods=["DELETE"])
def delete_retailer(name):
    config = RetailerConfig.get(name)
    if not config:
        abort(404)
    RetailerConfig.delete(name)
    return "", 204


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
