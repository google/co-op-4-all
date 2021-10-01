/***************************************************************************
*
*  Copyright 2021 Google Inc.
*
*  Licensed under the Apache License, Version 2.0 (the "License");
*  you may not use this file except in compliance with the License.
*  You may obtain a copy of the License at
*
*      https://www.apache.org/licenses/LICENSE-2.0
*
*  Unless required by applicable law or agreed to in writing, software
*  distributed under the License is distributed on an "AS IS" BASIS,
*  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
*  See the License for the specific language governing permissions and
*  limitations under the License.
*
*  Note that these code samples being shared are not official Google
*  products and are not formally supported.
*
***************************************************************************/

# Data provider for client

data "google_client_config" "current" {
}

resource "null_resource" "ng_cli" {
  provisioner "local-exec" {
    working_dir = "frontend"
    command = "npm install -g @angular/cli"
  }
}

resource "null_resource" "ng_dependencies" {
  provisioner "local-exec" {
    working_dir = "frontend"
    command = "npm install"
  }
}

resource "null_resource" "angular_build" {
  provisioner "local-exec" {
    working_dir = "frontend"
    command = "ng build --configuration=production"
  }
  depends_on = [null_resource.ng_cli, null_resource.ng_dependencies]
}

# Create the App Engine application

resource "google_app_engine_application" "app" {
  project     = var.project_id
  location_id = var.location
  depends_on = [null_resource.ng_cli, null_resource.ng_dependencies, null_resource.angular_build]
}

# Deploy the default frontend service

resource "null_resource" "frontend_deploy" {
  provisioner "local-exec" {
    working_dir = "frontend"
    command = "gcloud app deploy frontend.yaml"
  }
  depends_on = [google_app_engine_application.app]
}

# Desploy the backend api-service

resource "null_resource" "backend_deploy" {
  provisioner "local-exec" {
    working_dir = "backend"
    command = "gcloud app deploy backend.yaml"
  }
  depends_on = [null_resource.frontend_deploy]
}

# Desploy the backend ads-conversions-proxy

resource "null_resource" "ads_conversions_proxy_deploy" {
  provisioner "local-exec" {
    working_dir = "backend/proxy"
    command = "gcloud app deploy proxy.yaml"
  }
  depends_on = [null_resource.backend_deploy]
}

# Desploy the dispatch rules for the api-service and ads-conversions-proxy endpoints

resource "null_resource" "dispatch_deploy" {
  provisioner "local-exec" {
    working_dir = "backend"
    command = "gcloud app deploy dispatch.yaml"
  }
  depends_on = [null_resource.backend_deploy, null_resource.ads_conversions_proxy_deploy]
}

# Enable the Cloud Scheduler API

resource "google_project_service" "cloud_scheduler_api" {
  project                    = var.project_id
  service                    = "cloudscheduler.googleapis.com"
  disable_dependent_services = false
  disable_on_destroy         = false
  depends_on = [null_resource.dispatch_deploy]
}

# Desploy the cron for the api-service and ads-conversions-proxy endpoints

resource "null_resource" "cron_deploy" {
  provisioner "local-exec" {
    working_dir = "backend"
    command = "gcloud app deploy cron.yaml"
  }
  depends_on = [google_project_service.cloud_scheduler_api]
}

# Enable the Campaign Manager API

resource "google_project_service" "campaign_manager_api" {
  project                    = var.project_id
  service                    = "dfareporting.googleapis.com"
  disable_dependent_services = false
  disable_on_destroy         = false
  depends_on = [null_resource.cron_deploy]
}

# Enable the Secret Manager API

resource "google_project_service" "enable_secret_manager_api" {
  project                    = var.project_id
  service                    = "secretmanager.googleapis.com"
  disable_dependent_services = false
  disable_on_destroy         = false
  depends_on = [null_resource.cron_deploy]
}

# Add Secret Manager Accessor role to the App Engine default service account

data "google_app_engine_default_service_account" "default" {
}

resource "google_project_iam_member" "secret_manager_accessor_iam_role" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${data.google_app_engine_default_service_account.default.email}"
  depends_on = [google_project_service.enable_secret_manager_api]
}

# Create the secrets in Secret Manager to access the CM API.

# Client ID
resource "google_secret_manager_secret" "secret_coop_client_id" {
  secret_id = "coop_client_id"
  labels = {
    label = "coopclientid"
  }
  replication {
    automatic = true
  }
  depends_on = [google_project_iam_member.secret_manager_accessor_iam_role]
}

resource "google_secret_manager_secret_version" "secret_version_coop_client_id" {
  secret = google_secret_manager_secret.secret_coop_client_id.id
  secret_data = var.coop_client_id
  depends_on = [google_secret_manager_secret.secret_coop_client_id]
}

# Client Secret
resource "google_secret_manager_secret" "secret_coop_client_secret" {
  secret_id = "coop_client_secret"
  labels = {
    label = "coopclientsecret"
  }
  replication {
    automatic = true
  }
  depends_on = [google_project_iam_member.secret_manager_accessor_iam_role]
}

resource "google_secret_manager_secret_version" "secret_version_coop_client_secret" {
  secret = google_secret_manager_secret.secret_coop_client_secret.id
  secret_data = var.coop_client_secret
  depends_on = [google_secret_manager_secret.secret_coop_client_secret]
}

# Access Token
resource "google_secret_manager_secret" "secret_coop_access_token" {
  secret_id = "coop_access_token"
  labels = {
    label = "coopaccesstoken"
  }
  replication {
    automatic = true
  }
  depends_on = [google_project_iam_member.secret_manager_accessor_iam_role]
}

resource "google_secret_manager_secret_version" "secret_version_coop_access_token" {
  secret = google_secret_manager_secret.secret_coop_access_token.id
  secret_data = var.coop_access_token
  depends_on = [google_secret_manager_secret.secret_coop_access_token]
}

# Refresh Token
resource "google_secret_manager_secret" "secret_coop_refresh_token" {
  secret_id = "coop_refresh_token"
  labels = {
    label = "cooprefreshtoken"
  }
  replication {
    automatic = true
  }
  depends_on = [google_project_iam_member.secret_manager_accessor_iam_role]
}

resource "google_secret_manager_secret_version" "secret_version_coop_refresh_token" {
  secret = google_secret_manager_secret.secret_coop_refresh_token.id
  secret_data = var.coop_refresh_token
  depends_on = [google_secret_manager_secret.secret_coop_refresh_token]
}