# 定期的に実行するためのイベントルール作成
resource "aws_cloudwatch_event_rule" "event_rule" {
  name                = "${var.event_name}"
  schedule_expression = "${var.schedule_expression}"
}

# イベントルールに紐づくLambda関数の設定
resource "aws_cloudwatch_event_target" "event_target" {
  rule = "${aws_cloudwatch_event_rule.event_rule.name}"
  arn  = "${var.lambda_arn}"
}