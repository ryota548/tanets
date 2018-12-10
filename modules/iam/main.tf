// AWS lambda用のIAMロール
resource "aws_iam_role" "iam_role" {
  name = "${var.iam_role_name}"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow"
    }
  ]
}
EOF
}

# LambdaからElasticsearchを実行するためのポリシー作成
resource "aws_iam_role_policy_attachment" "iam_policy_es" {
  role = "${aws_iam_role.iam_role.id}"

  policy_arn = "arn:aws:iam::aws:policy/AmazonESReadOnlyAccess"
}

# Lambdaを実行するためのポリシー作成
resource "aws_iam_role_policy_attachment" "iam_policy_lambda" {
  role = "${aws_iam_role.iam_role.id}"

  policy_arn = "arn:aws:iam::aws:policy/AWSLambdaExecute"
}