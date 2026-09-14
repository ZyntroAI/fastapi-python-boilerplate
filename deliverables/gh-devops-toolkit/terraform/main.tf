# Branch protection + required checks via Terraform (GitHub provider).
# Reference: apply with the repo's org. Adjust repo name / required checks.
terraform {
  required_providers {
    github = { source = "integrations/github" }
  }
}

variable "repository" {
  type    = string
  default = "fastapi-python-boilerplate"
}

variable "required_status_checks" {
  type    = list(string)
  default = ["pr-checks", "gitleaks"]
}

resource "github_branch_protection" "main" {
  repository_id = var.repository
  pattern       = "main"

  required_pull_request_reviews {
    required_approving_review_count = 1
  }

  required_status_checks {
    strict   = true
    contexts = var.required_status_checks
  }

  require_conversation_resolution = true
}
