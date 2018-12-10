# tanets

Tf-Aws-Notify-Elasticsearch-To-Slack

Elasticsearchに保存されているドキュメントから、指定文字列に当てはまるもののみ通知する

- Terraform
- AWS
- Slack

## 利用AWSサービス

- Lambda
- IAM
- CloudWatch

## プロジェクト構成

```
.
├── README.md                     # プロジェクト概要説明
├── main.tf                       # `terraform apply`した時に実行されるmainのTerraformファイル
├── modules                       # 実際に環境構築を行う各モジュール格納場所(AWS LambdaなどのAWSサービス単位で作成)
│   ├── iam                       # IAMでLambda用のロール/ポリシー作成
│   │   ├── main.tf
│   │   ├── outputs.tf
│   │   └── variables.tf
│   ├── cloudwatch                # CloudwatchでLambda関数の定期実行部分を作成
│   │   ├── main.tf
│   │   ├── outputs.tf
│   │   └── variables.tf
│   └── aws_lambda                # LambdaでエラーログのSlack通知部分を作成
│       ├── lambda_function.py
│       ├── main.tf
│       ├── output.tf
│       └── variables.tf
└── variables.tf                  # Slack通知設定用の変数定義
```

## パラメータ

設定するべき変数は以下の通りです。

|変数名            |説明|
|-----------------|---|
|name       |各サービスに登録する名前|
|notify_schedule  |定期実行のcron設定|
|SLACK_WEBHOOK_URL|Slack通知を行うWebhookURL|
|SLACK_CHANNEL    |Slack通知を行うチャンネル名|
|USER_NAME        |Slack通知を行う際のユーザ名|
|ES_ENDPOINT      |Elasticsearchのエンドポイント|
|KIBANA_URL       |通知内容に添付するkibanaのURL|
|ERROR_LEVEL      |ログ通知対象のエラーログレベル|
|UNIT_OF_TIME     |ログ件数平均算出の時間単位(h|m|s)|

## 別プロジェクトからの利用例

sourceとして本リポジトリを指定する。

例：

```
module "tf-es-aggregation-notify" {
    source = "git::https://github.com/ryota548/tanets"
    name          = "error_log_daily_notify"

    # 定期通知用cron設定
    notify_schedule = "cron(15 1 * * ? *)"

    # Lambda用
    environment   = {
        SLACK_WEBHOOK_URL = "slack.hoge"
        SLACK_CHANNEL     = "hoge"
        KIBANA_URL        = "kibana.hoge"
        ES_INDEXIS        = "hoge-index"
        ES_ENDPOINT       = "es.hoge"
        ERROR_LEVEL       = "Fatal,Warning"
        USER_NAME         = "ログ情報お知らせちゃん"
        UNIT_OF_TIME      = "h"
    }
}
```