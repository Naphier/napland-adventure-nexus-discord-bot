// S3 
// Lambda with public endpoint
// Lambda permissions 

provider "aws" {
  region = "us-east-1"
}

// Create S3 bucket
resource "aws_s3_bucket" "napland_adventure_nexus_bucket" {
  bucket = "napland-adventure-nexus-bucket"
}

resource "aws_s3_bucket_versioning" "napland_adventure_nexus_bucket_versioning" {
  bucket = aws_s3_bucket.napland_adventure_nexus_bucket.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_public_access_block" "napland_adventure_nexus_bucket_block" {
    bucket                  = aws_s3_bucket.napland_adventure_nexus_bucket.id
    block_public_acls       = true
    block_public_policy     = true
    ignore_public_acls      = true
    restrict_public_buckets = true
}

resource "aws_s3_bucket_acl" "bucket_acl" {
  bucket = aws_s3_bucket.napland_adventure_nexus_bucket.id
  acl    = "private" 
}

module "lambda_function" {
  source = "terraform-aws-modules/lambda/aws"
  function_name = "napland-adventure-nexus-bot"
  handler = "main.lambda_handler"
  runtime = "python3.11"
  source_path = [
        {
            path = "${path.module}/../app"
            commands = [
                ":zip",
                "cd `mktemp -d`",
                "pip install --platform manylinux2014_x86_64 --only-binary=:all: --python-version 3.11 --target ./package -r requirements.txt",
                ":zip . vendor/"
            ]
            pattern = [
                "!vendor/.venv/**",
            ]
        }
    ]
  attach_cloudwatch_logs_policy = true
  snap_start = true

  policy_statements = {
    list_bucket = {
      effect = "Allow"
      actions = ["s3:ListBucket"]
      resources = [aws_s3_bucket.napland_adventure_nexus_bucket.arn]
    },
    write_bucket = {
      effect = "Allow"
      actions = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"]
      resources = ["${aws_s3_bucket.napland_adventure_nexus_bucket.arn}/*"]
    }
  }

  environment_variables = {
    BOT_TOKEN = var.BOT_TOKEN,
    APP_ID = "1350493471747739728",
    SERVER_ID = "925804924158230639",
    PUBLIC_KEY="719a85a5f77779a0fae4feafe223e1f0673871350d39fcbefc488f36de3cdb7c"
  }
}

# create API gateway with no auth
resource "aws_apigatewayv2_api" "lambda_api" {
  name          = "napland-adventure-nexus-bot-api"
  protocol_type = "HTTP"
  target        = module.lambda_function.lambda_function_arn
}