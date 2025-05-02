variable "project" {}

variable "region" {
  default = "us-central1"
}

variable "zone" {
  default = "us-central1-c"
}

variable "services" {
  type = list(string)
  default = [
    "aiplatform.googleapis.com",
    "artifactregistry.googleapis.com",
    "run.googleapis.com",
    # "compute.googleapis.com",
    "storage.googleapis.com",
    "bigquery.googleapis.com",
    # "pubsub.googleapis.com",
    # "cloudfunctions.googleapis.com",
    # "cloudbuild.googleapis.com",
    # "container.googleapis.com",
    "iam.googleapis.com"
  ]
}
