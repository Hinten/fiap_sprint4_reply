//https://developer.hashicorp.com/terraform/tutorials/aws-get-started/aws-create
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

resource "aws_budgets_budget" "budget-test" {
  name              = "budget-test"
  budget_type       = "COST"
  limit_amount      = "40.0"
  limit_unit        = "USD"
  time_unit         = "MONTHLY"
  time_period_start = "2025-09-26_00:00"
}