#!/bin/bash

# Copyright 2021 Google LLC

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    https://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Deploy the backend api-service
gcloud app deploy backend.yaml

echo '-----------------------------'
echo

# Deploy the ads-conversions-proxy proxy service
gcloud app deploy proxy/proxy.yaml

echo '-----------------------------'
echo

# Desploy the dispatch rules for the api-service and ads-conversions-proxy endpoints

gcloud app deploy dispatch.yaml
