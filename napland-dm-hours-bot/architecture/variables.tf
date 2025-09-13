variable "aws_region" {
  description = "The AWS region to deploy resources"
  type = string
  default = "us-east-1"
}

variable "aws_az" {
  description = "The AWS availability zone to deploy resources"
  type = string
  default = "us-east-1a"
}

variable "bucket_name" {
  description = "The name of the S3 bucket"
  type = string
  default = "napland-dnd"
}