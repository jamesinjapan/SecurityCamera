terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.31.0"
    }
  }

  required_version = ">= 1.2.9"
}

provider "aws" {
  region = "ap-northeast-1"
  access_key = local.envs["AWS_ACCESS_KEY_ID"]
  secret_key = local.envs["AWS_SECRET_ACCESS_KEY"]
}

resource "aws_s3_bucket" "bucket" {
  bucket = local.envs["S3_BUCKET_NAME"]

  tags = {
    project = "SecurityCamera"
  }
}

resource "aws_s3_bucket_acl" "bucket_acl" {
  bucket = aws_s3_bucket.bucket.id
  acl    = "private"
}

resource "aws_s3_bucket_lifecycle_configuration" "bucket-config" {
  bucket = aws_s3_bucket.bucket.id
  rule {
    id = "uploads"

    expiration {
      days = 365
    }

    status = "Enabled"
  }
}