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
