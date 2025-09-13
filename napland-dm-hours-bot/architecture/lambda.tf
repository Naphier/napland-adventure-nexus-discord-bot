module "iam" {
    source = "./iam"
}

resource "aws_lambda_function" "lambda_naplanddnd_dmhours" {
    function_name = "lambda_naplanddnd_dmhours"
    role          = aws_iam_role.naplanddnd_dmhours_lambda_role.arn
    handler       = "index.handler"
    runtime       = "python3.8"
    filename      = "lambda_function.zip"

    source_code_hash = filebase64sha256("lambda_function.zip")
}

resource "aws_lambda_permission" "lambda_allow_api_gateway" {
    statement_id  = "AllowExecutionFromApiGateway"
    action        = "lambda:InvokeFunction"
    function_name = aws_lambda_function.lambda_naplanddnd_dmhours.function_name
    principal     = "apigateway.amazonaws.com"
}