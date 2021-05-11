# Data provider for client

data "google_client_config" "current" {
}

# New project name generation

resource "random_string" "random" {
  length           = 8
  special          = false
  upper            = false
}

locals {
    new_project_id = "goop-4-all-${random_string.random.result}"
}

# Creation of new project to host Goop

resource "google_project" "goop_project" {
  name       = "Goop 4 All"
  project_id = local.new_project_id
  folder_id = var.project_folder_id
  billing_account = var.billing_account
}

# Uploads Goop package to GCS
resource "google_storage_bucket" "goop_bucket" {
  name = "${local.new_project_id}-appengine"
  project = local.new_project_id
  uniform_bucket_level_access = true
  depends_on = [google_project.goop_project]
}

resource "google_storage_bucket_object" "goop_package" {
  name   = "goop.zip"
  bucket = google_storage_bucket.goop_bucket.name
  source = "./packages/goop.zip"
  depends_on = [google_storage_bucket.goop_bucket]
}

#resource "google_service_account" "cloud_build_service_account" {
#  account_id   = "${google_project.goop_project.number}@cloudbuild.gserviceaccount.com"
#  display_name = "Service Account"
#}

resource "google_project_service" "cloudbuild_api" {
  project                    = local.new_project_id
  service                    = "cloudbuild.googleapis.com"
  disable_dependent_services = false
  disable_on_destroy         = false
  depends_on = [google_storage_bucket.goop_bucket]
}

resource "google_storage_bucket_iam_member" "member" {
  bucket = google_storage_bucket.goop_bucket.name
  role = "roles/storage.admin"
  member = "serviceAccount:${google_project.goop_project.number}@cloudbuild.gserviceaccount.com"
  depends_on = [google_app_engine_application.app, google_storage_bucket.goop_bucket, google_project_service.cloudbuild_api]
}

# Creates App Engine 

resource "google_app_engine_application" "app" {
  project     = local.new_project_id
  location_id = var.location
  depends_on = [google_project.goop_project]
}

resource "google_app_engine_standard_app_version" "goop_application" {
  version_id = "v1"
  service    = "default"
  runtime    = "python39"
  project = local.new_project_id

  entrypoint {
      shell = "flask"
  }

  deployment {
    zip {
      source_url = "https://storage.googleapis.com/${google_storage_bucket.goop_bucket.name}/${google_storage_bucket_object.goop_package.name}"
    }
  }

  env_variables = {
    port = "8080"
  }

  automatic_scaling {
    max_concurrent_requests = 10
    min_idle_instances = 1
    max_idle_instances = 1
    min_pending_latency = "1s"
    max_pending_latency = "5s"
    standard_scheduler_settings {
      target_cpu_utilization = 0.5
      target_throughput_utilization = 0.75
      min_instances = 2
      max_instances = 10
    }
  }
  noop_on_destroy = true

  depends_on = [google_app_engine_application.app, google_storage_bucket_object.goop_package, google_storage_bucket_iam_member.member]
}