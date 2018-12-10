# Cloudwatchアラームと定期通知用イベント作成
module "cloudwatch" {
  source              = "./modules/cloudwatch"
  event_name          = "${var.name}"
  lambda_arn          = "${module.lambda.lambda_function_arn}"
  # 定期通知用cron設定
  schedule_expression = "${var.notify_schedule}"
}

# LambdaからCloudwatch, ElasticsearchをReadするロール/ポリシー作成
module "iam" {
  source = "./modules/iam"
  iam_role_name = "${var.name}"
}

# Lambda関数作成
module "lambda" {
  source                    = "./modules/lambda"
  function_name             = "${var.name}"
  # iam/output.tfで出力されたroleのARN
  iam_role_arn              = "${module.iam.iam_role_arn}"
  environment               = "${var.environment}"
  # cloudwatch/output.tfで出力されたevent_ruleのARN
  cloudwatch_event_rule_arn = "${module.cloudwatch.event_rule_arn}"
}