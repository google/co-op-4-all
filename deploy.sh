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

SEPARATOR="$(printf -- '-%.0s' {1..70})"

echo
echo "This utility will help you set up Co-op4all for the first time"
echo
echo $SEPARATOR
echo "This is a reference implementation only and not warrantied by Google."
echo "Co-op4all will be configured in the Google Cloud project ${GOOGLE_CLOUD_PROJECT}"
echo

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
    echo $SEPARATOR
    echo "Activating Services..."
    echo $SEPARATOR
    echo
    gcloud services enable bigquery.googleapis.com
    gcloud services enable cloudscheduler.googleapis.com
    gcloud services enable dfareporting.googleapis.com
    gcloud services enable cloudbuild.googleapis.com
    gcloud services enable iap.googleapis.com
}

deploy_frontend() {
    echo $SEPARATOR
    echo "Deploying frontend..."
    echo $SEPARATOR
    echo
    cd frontend/
    npm install -g @angular/cli@13.0.1
    npm install
    ng build --configuration=production
    gcloud app deploy frontend.yaml
}

deploy_api_service() {
    echo $SEPARATOR
    echo "Deploying api-service..."
    echo $SEPARATOR
    echo
    cd ../backend
    gcloud app deploy backend.yaml --quiet
}

deploy_proxy() {
    echo $SEPARATOR
    echo "Deploying proxy..."
    echo $SEPARATOR
    echo
    echo "The Identity Aware Proxy Client Id is required for deployment..."
    echo "Please follow the steps on the GitHub documentation here: https://github.com/google/co-op-4-all#get-the-identity-aware-proxy-client-id to get the IAP Client Id"
    echo
    read -p "Enter the IAP Client Id to continue: " -r IAP_CLIENT_ID
    export IAP_CLIENT_ID="$IAP_CLIENT_ID"
    cd proxy/
    envsubst < proxy.yaml | sponge proxy.yaml
    gcloud app deploy proxy.yaml --quiet
}

deploy_dispatch() {
    echo $SEPARATOR
    echo "Deploying dispatch..."
    echo $SEPARATOR
    echo
    cd ../
    gcloud app deploy dispatch.yaml --quiet
}

deploy_cron() {
    echo $SEPARATOR
    echo "Deploying cron..."
    echo $SEPARATOR
    echo
    gcloud app deploy cron.yaml --quiet
}

grant_permissions_to_default_service_account() {
    echo $SEPARATOR
    echo 'App Engine default service account permissions'
    echo $SEPARATOR
    dsa_command=$(gcloud iam service-accounts list --filter="displayName:App Engine default service account")
    # split string by spaces
    parts=(${dsa_command// / })
    default_service_account=${parts[8]}
    echo
    echo "Granting BigQuery Data Viewer role to the App Engine default service account ${default_service_account} in the project ${BQ_EXPORT_PROJECT_ID}..."
    echo
    gcloud projects add-iam-policy-binding $BQ_EXPORT_PROJECT_ID \
    --member="serviceAccount:${default_service_account}" --role='roles/bigquery.dataViewer'
    echo
    echo "Granting IAP-secured Web App User role to the App Engine default service account ${default_service_account} in the project ${GOOGLE_CLOUD_PROJECT}..."
    gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT \
    --member="serviceAccount:${default_service_account}" --role='roles/iap.httpsResourceAccessor'
    echo
}

grant_iap_permissions() {
    echo $SEPARATOR
    echo 'Identity Aware Proxy permissions'
    echo $SEPARATOR
    active_account=$(gcloud config list account --format "value(core.account)")
    echo "Granting IAP-secured Web App User role to the active account ${active_account}..."
    gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT \
    --member="user:${active_account}" --role='roles/iap.httpsResourceAccessor'
    echo "Please grant permissions to other users using the IAM UI."
}

if confirm "Do you acknowledge and wish to proceed (Yy/Nn)?" ; then
    echo
    read -p "Enter the Project Id where the BQ Export is (the user deploying Co-op4All must have at least Editor access in the BQ Export project): " -r BQ_EXPORT_PROJECT_ID
    echo
    echo "BigQuery Export Project: " $BQ_EXPORT_PROJECT_ID
    echo
    if confirm "Please confirm that the provided information is correct. Continue (Yy/Nn)?" ; then
        echo
        enable_services
        deploy_frontend
        deploy_api_service
        deploy_proxy
        deploy_dispatch
        deploy_cron
        grant_permissions_to_default_service_account
        grant_iap_permissions
        echo "Setup Completed!"
    else
        echo "Aborting... Please run the script again with the correct parameters."
    fi
fi
