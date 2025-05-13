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

# resource "google_parameter_manager_parameter" "slack-token" {
#   parameter_id = "slack-token"

#   labels = {
#     label = "ai-bot-bot"
#   }
# }

# resource "google_parameter_manager_parameter_version" "slack-token-production" {
#   parameter            = google_parameter_manager_parameter.slack-token.id
#   parameter_version_id = "production"
#   parameter_data       = "__REF__(\"//secretmanager.googleapis.com/${data.google_secret_manager_secret_version.slack-token.name}\")"
# }

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

# resource "google_parameter_manager_parameter" "agent-engine" {
#   parameter_id = "agent-engine"

#   labels = {
#     label = "ai-bot-bot"
#   }
# }

# resource "google_parameter_manager_parameter_version" "agent-engine-production" {
#   parameter            = google_parameter_manager_parameter.agent-engine.id
#   parameter_version_id = "production"
#   parameter_data       = "__REF__(\"//secretmanager.googleapis.com/${data.google_secret_manager_secret_version.agent-engine.name}\")"
# }

resource "google_service_account" "bot-executor" {
  account_id   = "bot-executor"
  display_name = "bot executor"
}

resource "google_project_iam_member" "bot-executor-iam" {
  for_each = toset([
    "roles/editor",
    "roles/secretmanager.secretAccessor",
  ])

  project = var.project
  role    = each.value
  member  = "serviceAccount:${google_service_account.bot-executor.email}"
}

data "google_compute_default_service_account" "default" {
}

resource "google_service_account_iam_member" "gce-default-account-iam" {
  service_account_id = data.google_compute_default_service_account.default.name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${google_service_account.bot-executor.email}"
}

resource "google_cloud_run_v2_service" "ai-bot" {
  name     = "ai-bot"
  location = var.region
  invoker_iam_disabled = true

  template {
    service_account = google_service_account.bot-executor.email
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project}/ai-bot/bot:latest"
      resources {
        cpu_idle = false
      }
      startup_probe {
        failure_threshold = 10
        http_get {
          path = "/healthz"
          port = "8080"
        }
      }
      env {
        name = "SLACK_BOT_TOKEN"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.slack-token-secret.secret_id
            version = data.google_secret_manager_secret_version.slack-token.version
          }
        }
      }
      env {
        name = "AGENT_ENGINE_RESOURCE"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.agent-engine-secret.secret_id
            version = data.google_secret_manager_secret_version.agent-engine.version
          }
        }
      }
    }
  }
}

resource "google_artifact_registry_repository" "ai-bot" {
  repository_id = "ai-bot"
  description   = "ai-bot docker registery"
  format        = "DOCKER"
}

output "gh-actions-pool-provider-name" {
  value = google_iam_workload_identity_pool_provider.gh-actions-pool-provider.name
}

output "gh-actions-service-account-name" {
  value = google_service_account.bot-deployer.email
}

output "bot-service-name" {
  value = google_cloud_run_v2_service.ai-bot.name

}
