terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "6.8.0"
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

module "cloudrun" {
  source     = "./modules/cloudrun"
  project    = var.project
  region     = var.region
  depends_on = [google_project_service.services]
}
