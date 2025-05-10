terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "6.34.0"
    }
  }
}

provider "google" {
  project = var.project
  region  = var.region
  zone    = var.zone
}

resource "google_project_service" "services" {
  for_each           = toset(var.services)
  project            = var.project
  service            = each.value
  disable_on_destroy = false
}

module "bot" {
  source     = "./modules/bot"
  project    = var.project
  region     = var.region
  depends_on = [google_project_service.services]
}

module "agent" {
  source     = "./modules/agent"
  project    = var.project
  region     = var.region
  depends_on = [google_project_service.services]
}
