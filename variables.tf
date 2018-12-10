// cloudwatchのイベント名
variable "name" {
    default = "tanets"
}
// cloudwatchイベントのcron設定
variable "notify_schedule" {
    default = "cron(15 1 * * ? *)"
}
// 環境変数
variable "environment" {
    type = "map"
    default = {
        SLACK_WEBHOOK_URL = ""
        SLACK_CHANNEL     = ""
        KIBANA_URL        = ""
        ES_INDEXES        = ""
        ES_ENDPOINT       = ""
        ERROR_LEVEL       = ""
        USER_NAME         = "ログ情報お知らせbot"
        UNIT_OF_TIME      = "h" 
  }
}