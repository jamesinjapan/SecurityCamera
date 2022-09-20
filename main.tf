terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.31.0"
    }
    dotenv = {
      source  = "jrhouston/dotenv"
      version = "~> 1.0"
    }
  }

  required_version = ">= 1.2.9"
}

data dotenv config {
  # NOTE there must be a file called `.env` in the same directory as the .tf config
  filename = ".env"
}

provider "aws" {
  region = "ap-northeast-1"
  access_key = sensitive(data.dotenv.config.env.AWS_ACCESS_KEY_ID)
  secret_key = sensitive(data.dotenv.config.env.AWS_SECRET_ACCESS_KEY)
}

resource "aws_s3_bucket" "bucket" {
  bucket = data.dotenv.config.env.S3_BUCKET_NAME

  tags = {
    project = "SecurityCamera"
  }
}

resource "aws_s3_bucket" "icon_bucket" {
  bucket = data.dotenv.config.env.S3_ICON_BUCKET_NAME

  tags = {
    project = "SecurityCamera"
  }
}

resource "aws_s3_bucket_acl" "bucket_acl" {
  bucket = aws_s3_bucket.bucket.id
  acl    = "public-read"
}

resource "aws_s3_bucket_acl" "icon_bucket_acl" {
  bucket = aws_s3_bucket.icon_bucket.id
  acl    = "public-read"
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

resource "aws_iam_role" "iam_role_for_send_to_line_lambda" {
  name = "iam_role_for_send_to_line_lambda"
  assume_role_policy = <<EOF
  {
  "Version": "2012-10-17",
  "Statement": [
    {
    "Action": "sts:AssumeRole",
    "Principal": {
      "Service": "lambda.amazonaws.com"
    },
    "Effect": "Allow",
    "Sid": ""
    }
  ]
  }
  EOF
}

resource "aws_lambda_function" "send_to_line_lambda" {
  filename  	= "lambdas/send_to_line/send_to_line_lambda.zip"
  function_name = "send_to_line"
  role      	= aws_iam_role.iam_role_for_send_to_line_lambda.arn
  handler   	= "lambda_function.lambda_handler"
  source_code_hash = filebase64sha256("lambdas/send_to_line/send_to_line_lambda.zip")
  runtime = "python3.9"
  environment {
    variables = {
      LINE_ACCESS_TOKEN = sensitive(data.dotenv.config.env.LINE_ACCESS_TOKEN)
      VERIFIED_USERS = sensitive(data.dotenv.config.env.VERIFIED_USERS)
    }
  }

  tags = {
    project = "SecurityCamera"
  }
}

resource "aws_lambda_permission" "allow_bucket" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.send_to_line_lambda.arn
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.bucket.arn
}

resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = aws_s3_bucket.bucket.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.send_to_line_lambda.arn
    events              = ["s3:ObjectCreated:*"]
  }

  depends_on = [aws_lambda_permission.allow_bucket]
}

resource "aws_iam_role_policy_attachment" "iam_role_policy_attachment_lambda_basic_execution" {
  role       = aws_iam_role.iam_role_for_send_to_line_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}
