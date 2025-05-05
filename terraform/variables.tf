variable "project" {}

variable "region" {
  default = "asia-northeast1"
}

variable "zone" {
  default = "asia-northeast1-c"
}

variable "services" {
  type = list(string)
  default = [
    "aiplatform.googleapis.com",
    "logging.googleapis.com",
    "monitoring.googleapis.com",
    "cloudtrace.googleapis.com",
    "maps-backend.googleapis.com",
    "directions-backend.googleapis.com",
    "routes.googleapis.com",
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
