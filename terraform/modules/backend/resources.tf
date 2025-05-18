variable "region" {}
variable "project" {}

resource "google_storage_bucket" "default" {
  name     = "terraform-remote-backend-konk303"
  location = "ASIA1"

  force_destroy               = false
  public_access_prevention    = "enforced"
  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }
}
