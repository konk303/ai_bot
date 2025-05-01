variable "region" {}
variable "project" {}

resource "google_artifact_registry_repository" "ai-bot" {
  repository_id = "ai-bot"
  description   = "ai-bot docker registery"
  format        = "DOCKER"
}

resource "google_cloud_run_service" "ai-bot" {
  name     = "ai-bot"
  location = var.region

  template {
    spec {
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project}/ai-bot:latest"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}
