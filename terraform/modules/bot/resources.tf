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

resource "google_cloud_run_v2_job" "ai-bot" {
  name     = "ai-bot"
  location = var.region

  template {
    template {
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project}/ai-bot/bot:latest"
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
    task_count = 1
  }
}

resource "google_artifact_registry_repository" "ai-bot" {
  repository_id = "ai-bot"
  description   = "ai-bot docker registery"
  format        = "DOCKER"
}

resource "google_iam_workload_identity_pool" "gh-actions-pool" {
  workload_identity_pool_id = "gh-actions"
}

resource "google_iam_workload_identity_pool_provider" "gh-actions-pool-provider" {
  workload_identity_pool_id          = google_iam_workload_identity_pool.gh-actions-pool.workload_identity_pool_id
  workload_identity_pool_provider_id = "gh-actions-provider"
  description                        = "GitHub Actions identity pool provider for automations"
  attribute_condition                = <<EOT
    assertion.repository_owner_id == "69647" &&
    attribute.repository == "konk303/ai_bot"
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

resource "google_service_account" "bot-deployer" {
  account_id   = "bot-deployer"
  display_name = "bot deploy executor"
}

resource "google_service_account_iam_member" "workload-identity-user" {
  service_account_id = google_service_account.bot-deployer.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.gh-actions-pool.name}/attribute.repository/konk303/ai_bot"
}

resource "google_project_iam_member" "artifact-registry-uploader" {
  project = var.project
  role    = "roles/artifactregistry.writer"
  member  = "serviceAccount:${google_service_account.bot-deployer.email}"
}

output "gh-actions-pool-provider-name" {
  value = google_iam_workload_identity_pool_provider.gh-actions-pool-provider.name
}

output "gh-actions-service-account-name" {
  value = google_service_account.bot-deployer.email
}

output "bot-job-name" {
  value = google_cloud_run_v2_job.ai-bot.id

}
