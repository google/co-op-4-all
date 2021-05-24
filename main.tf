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
    new_project_id = "co-op-4-all-${random_string.random.result}"
}

resource "null_resource" "ng_cli" {
  provisioner "local-exec" {
    working_dir = "frontend"
    command = "sudo npm install -g @angular/cli"
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

resource "null_resource" "zip_dist" {
  provisioner "local-exec" {
    command = "zip co-op-4-all.zip app.yaml requirements.txt frontend/dist/*"
  }

  depends_on = [null_resource.angular_build]
}

# Creation of new project to host Co-op 4 All

resource "google_project" "co_op_4_all_project" {
  name       = "Co-op 4 All"
  project_id = local.new_project_id
  folder_id = var.project_folder_id
  billing_account = var.billing_account
  depends_on = [null_resource.angular_build]
}

# Uploads Co-op 4 all package to GCS
resource "google_storage_bucket" "co_op_4_all_bucket" {
  name = "${local.new_project_id}-appengine"
  project = local.new_project_id
  uniform_bucket_level_access = true
  depends_on = [google_project.co_op_4_all_project, null_resource.zip_dist]
}

resource "google_storage_bucket_object" "co_op_4_all_package" {
  name   = "co-op-4-all.zip"
  bucket = google_storage_bucket.co_op_4_all_bucket.name
  source = "./co-op-4-all.zip"
  depends_on = [google_storage_bucket.co_op_4_all_bucket]
}

resource "google_project_service" "cloudbuild_api" {
  project                    = local.new_project_id
  service                    = "cloudbuild.googleapis.com"
  disable_dependent_services = false
  disable_on_destroy         = false
  depends_on = [google_storage_bucket.co_op_4_all_bucket]
}

resource "google_project_service" "campain_manager_api" {
  project                    = local.new_project_id
  service                    = "dfareporting.googleapis.com"
  disable_dependent_services = false
  disable_on_destroy         = false
  depends_on = [google_project.co_op_4_all_project]
}

resource "google_storage_bucket_iam_member" "member" {
  bucket = google_storage_bucket.co_op_4_all_bucket.name
  role = "roles/storage.admin"
  member = "serviceAccount:${google_project.co_op_4_all_project.number}@cloudbuild.gserviceaccount.com"
  depends_on = [google_app_engine_application.app, google_storage_bucket.co_op_4_all_bucket, google_project_service.cloudbuild_api]
}

# Creates App Engine 

resource "google_app_engine_application" "app" {
  project     = local.new_project_id
  location_id = var.location
  depends_on = [google_project.co_op_4_all_project]
}

resource "google_app_engine_standard_app_version" "co_op_4_all_application" {
  version_id = "v1"
  service    = "default"
  runtime    = "python39"
  project = local.new_project_id

  entrypoint {
      shell = "flask"
  }

  deployment {
    zip {
      source_url = "https://storage.googleapis.com/${google_storage_bucket.co_op_4_all_bucket.name}/${google_storage_bucket_object.co_op_4_all_package.name}"
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

  depends_on = [google_app_engine_application.app, google_storage_bucket_object.co_op_4_all_package, google_storage_bucket_iam_member.member]
}
