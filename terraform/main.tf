terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "6.8.0"
    }
  }
}

provider "google" {
  project = "develop-458412"
  region  = "us-central1"
  zone    = "us-central1-c"
}

resource "google_project_service" "compute" {
  project = "develop-458412"
  service = "compute.googleapis.com"
}

resource "google_compute_network" "vpc_network" {
  depends_on = [google_project_service.compute]
  name       = "terraform-network"
}
