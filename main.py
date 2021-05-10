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
from models import GoopConfig
from flask import Flask, render_template, jsonify, request, abort


app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/new_campaign", methods=["GET"])
def new_campaign():
    return render_template("new.html")


@app.route("/campaigns", methods=["GET"])
def list_campaigns():
    configs = GoopConfig.get_all()
    return render_template("list.html", configs=configs)


@app.route("/campaigns", methods=["POST"])
def add_campaign():
    data = dict(request.json)
    config = GoopConfig(**data)
    new_config = config.add()
    if not new_config:
        abort(409)
    return "", 201


@app.route("/campaigns/<string:name>", methods=["GET"])
def get_campaign(name):
    config = GoopConfig.get(name)
    if not config:
        abort(404)
    return jsonify(config)


@app.route("/campaigns/<string:name>", methods=["PUT"])
def update_campaign(name):
    data = dict(request.json)
    config = GoopConfig(**data)
    update = config.update(name)
    if not update:
        abort(404)
    return "", 200


@app.route("/logs")
def logs():
    return render_template("logs.html")


@app.route("/configuration")
def configuration():
    return render_template("config.html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
