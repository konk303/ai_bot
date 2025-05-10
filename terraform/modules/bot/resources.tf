variable "region" {}
variable "project" {}

resource "google_secret_manager_secret" "slack-token-secret" {
  secret_id = "slack-token"

  labels = {
    label = "ai-bot-bot"
  }

  replication {
    auto {}
  }
}

data "google_secret_manager_secret_version" "slack-token" {
  secret = google_secret_manager_secret.slack-token-secret.id
}

resource "google_parameter_manager_parameter" "slack-token" {
  parameter_id = "slack-token"

  labels = {
    label = "ai-bot-bot"
  }
}

resource "google_parameter_manager_parameter_version" "slack-token-production" {
  parameter            = google_parameter_manager_parameter.slack-token.id
  parameter_version_id = "production"
  parameter_data       = "__REF__(\"//secretmanager.googleapis.com/${data.google_secret_manager_secret_version.slack-token.name}\")"
}

resource "google_secret_manager_secret" "agent-engine-secret" {
  secret_id = "agent-engine"

  labels = {
    label = "ai-bot-bot"
  }

  replication {
    auto {}
  }
}

data "google_secret_manager_secret_version" "agent-engine" {
  secret = google_secret_manager_secret.agent-engine-secret.id
}

resource "google_parameter_manager_parameter" "agent-engine" {
  parameter_id = "agent-engine"

  labels = {
    label = "ai-bot-bot"
  }
}

resource "google_parameter_manager_parameter_version" "agent-engine-production" {
  parameter            = google_parameter_manager_parameter.agent-engine.id
  parameter_version_id = "production"
  parameter_data       = "__REF__(\"//secretmanager.googleapis.com/${data.google_secret_manager_secret_version.agent-engine.name}\")"
}

resource "google_artifact_registry_repository" "ai-bot" {
  repository_id = "ai-bot"
  description   = "ai-bot docker registery"
  format        = "DOCKER"
}

resource "google_iam_workload_identity_pool" "gh-actions-pool" {
  workload_identity_pool_id = "gh-actions-pool"
}

resource "google_iam_workload_identity_pool_provider" "example" {
  workload_identity_pool_id          = google_iam_workload_identity_pool.gh-actions-pool.workload_identity_pool_id
  workload_identity_pool_provider_id = "gh-actions"
  description                        = "GitHub Actions identity pool provider for automations"
  attribute_condition                = <<EOT
    assertion.repository_owner_id == "123456789" &&
    attribute.repository == "gh-org/gh-repo" &&
    assertion.ref == "refs/heads/main" &&
    assertion.ref_type == "branch"
EOT
  attribute_mapping = {
    "google.subject"       = "assertion.sub"
    "attribute.actor"      = "assertion.actor"
    "attribute.aud"        = "assertion.aud"
    "attribute.repository" = "assertion.repository"
  }
  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
}

# resource "google_cloud_run_service" "ai-bot" {
#   name     = "ai-bot"
#   location = var.region

#   template {
#     spec {
#       containers {
#         image = "${var.region}-docker.pkg.dev/${var.project}/ai-bot:latest"
#       }
#     }
#   }

#   traffic {
#     percent         = 100
#     latest_revision = true
#   }
# }
