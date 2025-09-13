resource "aws_iam_role" "naplanddnd_dmhours_lambda_role" {
    name = "naplanddnd_dmhours_lambda_role"

    assume_role_policy = jsonencode({
        Version = "2012-10-17"
        Statement = [
            {
                Action = "sts:AssumeRole"
                Effect = "Allow"
                Principal = {
                    Service = "lambda.amazonaws.com"
                }
            }
        ]
    })
}

resource "aws_iam_policy" "naplanddnd_dmhours_lambda_s3_write_policy" {
    name        = "naplanddnd_dmhours_lambda_s3_write_policy"
    description = ("Policy to allow read, write, and delete access to " +
                   "the S3 bucket for the Napland DND DM hours data")

    policy = jsonencode({
        Version = "2012-10-17"
        Statement = [
            {
                Action = [
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:PutObjectAcl",
                    "s3:DeleteObject"
                ]
                Effect   = "Allow"
                Resource = "arn:aws:s3:::${var.bucket_name}/dm_hours/*"
            }
        ]
    })
}

resource "aws_iam_role_policy_attachment" "s3_write_policy_attachment" {
    role       = aws_iam_role.naplanddnd_dmhours_lambda_role.name
    policy_arn = aws_iam_policy.naplanddnd_dmhours_lambda_s3_write_policy.arn
}

resource "aws_iam_role_policy_attachment" "lambda_policy_attachment" {
    role       = aws_iam_role.naplanddnd_dmhours_lambda_role.name
    policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}
