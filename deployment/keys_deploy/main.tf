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

# Add Secret Manager Accessor role to the App Engine default service account

data "google_app_engine_default_service_account" "default" {
}

# Enable the Secret Manager API

resource "google_project_service" "enable_secret_manager_api" {
  project                    = var.project_id
  service                    = "secretmanager.googleapis.com"
  disable_dependent_services = false
  disable_on_destroy         = false
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