// lambdaの関数名
variable "function_name" {}
variable "iam_role_arn" {}
// 環境変数
variable "environment" {
    type = "map"
}
variable "cloudwatch_event_rule_arn" {}