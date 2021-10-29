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
 
# First build the bundles in the dist directory
# The bundles will be used to deploy the app to App Engine
 
echo ""
echo "This utility will help you set up Co-Op4all for the first time"
echo ""
echo "---------------------------------------------------------------------"
echo "This is a reference implementation only and not warrantied by Google."
echo "Co-Op4all will be configured in ${GOOGLE_CLOUD_PROJECT}"
echo ""
 

confirm() {
  while true; do
    read -r -p "${BOLD}${1:-Continue?} : ${NOFORMAT}"
    case ${REPLY:0:1} in
      [yY]) return 0 ;;
      [nN]) return 1 ;;
      *) echo "Please answer yes or no."
    esac
  done
}
 
enable_services() {
    echo "Activating Services..."
    echo ""
    gcloud services enable bigquery.googleapis.com
    gcloud services enable cloudscheduler.googleapis.com
    gcloud services enable dfareporting.googleapis.com
    gcloud services enable secretmanager.googleapis.com
}
 
deploy_frontend() {
    echo "Deploying frontend..."
    echo ""
    cd frontend/
    npm install -g --quiet @angular/cli
    npm install --silent
    ng build --configuration=production
    gcloud app deploy frontend.yaml
}
 
deploy_api_service(){
    echo "Deploying api-service..."
    echo ""
    cd ../backend
    gcloud app deploy backend.yaml --quiet
}
 
deploy_proxy(){
    echo "Deploying proxy..."
    echo ""
    cd proxy/
    envsubst < proxy.yaml | sponge proxy.yaml
    gcloud app deploy proxy.yaml --quiet
}
 
deploy_dispatch(){
    echo "Deploying dispatch..."
    echo ""
    cd ../
    gcloud app deploy dispatch.yaml --quiet
}
 
deploy_cron(){
    echo "Deploying cron..."
    echo ""
    gcloud app deploy cron.yaml --quiet
}

if confirm "Do you acknowledge and wish to proceed (Yy/Nn)?" ; then
    read -p "Enter the IAP client_id: " -r IAP_CLIENT_ID && export IAP_CLIENT_ID="$IAP_CLIENT_ID"
    enable_services;
    deploy_frontend;
    deploy_api_service;
    deploy_proxy;
    deploy_dispatch;
    deploy_cron;
fi

echo "Setup Completed!"
