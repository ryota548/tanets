// Lambdaで実行するファイルをアーカイブ
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/lambda_function.py"
  output_path = "${path.module}/tanets.zip"
}

// Lambda関数作成
resource "aws_lambda_function" "lambda_function" {
  filename         = "${data.archive_file.lambda_zip.output_path}"
  function_name    = "${var.function_name}"
  role             = "${var.iam_role_arn}"
  handler          = "lambda_function.lambda_handler"
  source_code_hash = "${base64sha256(file("${data.archive_file.lambda_zip.output_path}"))}"
  runtime          = "python3.6"
  timeout          = "60"

  // Lambda環境変数設定
  environment {
    variables = "${var.environment}"
  }  
}

# CloudWatchイベントからLambdaを実行する権限付与
resource "aws_lambda_permission" "lambda_permission" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.lambda_function.function_name}"
  principal     = "events.amazonaws.com"
  source_arn    = "${var.cloudwatch_event_rule_arn}"
}