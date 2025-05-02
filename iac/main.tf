// S3 
// Lambda with public endpoint
// Lambda permissions 

provider "aws" {
  region = "us-east-1"
}

module "lambda_function" {
  source = "terraform-aws-modules/lambda/aws"
  function_name = "napland-adventure-nexus-bot"
  handler = "main.lambda_handler"
  runtime = "python3.11"
  source_path = "${path.module}/../app"
  attach_cloudwatch_logs_policy = true
  snap_start = true

}