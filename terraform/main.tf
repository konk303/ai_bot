terraform {
  backend "gcs" {
    bucket = "terraform-remote-backend-konk303"
    prefix = "terraform/state"
  }

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

module "backend" {
  source     = "./modules/backend"
  project    = var.project
  region     = var.region
  depends_on = [google_project_service.services]
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

output "provider-name" {
  value = module.bot.gh-actions-pool-provider-name
}

output "deployer-name" {
  value = module.bot.gh-actions-service-account-name
}

output "bot-service-name" {
  value = module.bot.bot-service-name
}

output "bot-id" {
  value = module.bot.bot-id
}

output "bot-uri" {
  value = module.bot.bot-uri
}
