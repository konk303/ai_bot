variable "region" {}
variable "project" {}

resource "google_storage_bucket" "ai-bot" {
  name     = "ai-agent-staging"
  location = var.region
}
