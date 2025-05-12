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

resource "google_cloud_run_v2_service" "ai-bot" {
  name     = "ai-bot"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_INTERNAL_ONLY"
  deletion_protection = false

  template {
    scaling {
      min_instance_count = 1
      max_instance_count = 1
    }
    # containers {
    #   image = "${var.region}-docker.pkg.dev/${var.project}/ai-bot/bot:latest"
    #   resources {
    #     cpu_idle = true
    #   }

    #   env {
    #     name = "SLACK_BOT_TOKEN"
    #     value_source {
    #       secret_key_ref {
    #         secret  = google_secret_manager_secret.slack-token-secret.secret_id
    #         version = data.google_secret_manager_secret_version.slack-token.version
    #       }
    #     }
    #   }
    #   env {
    #     name = "AGENT_ENGINE_RESOURCE"
    #     value_source {
    #       secret_key_ref {
    #         secret  = google_secret_manager_secret.agent-engine-secret.secret_id
    #         version = data.google_secret_manager_secret_version.agent-engine.version
    #       }
    #     }
    #   }
    # }
    containers {
      image = "nginx"
      startup_probe {
        http_get {
          port = 80
        }
      }
      ports {
        container_port = 80
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
