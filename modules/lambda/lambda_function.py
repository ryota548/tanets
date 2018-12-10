import json
import os
import boto3
import time
import math
import urllib.request
from botocore.awsrequest import AWSRequest
from botocore.auth import SigV4Auth
from botocore.endpoint import BotocoreHTTPSession
from botocore.credentials import Credentials
from datetime import date, timedelta

athena = boto3.client('athena')
s3 = boto3.resource('s3')

ERROR_LEVEL = os.environ['ERROR_LEVEL']
SLACK_CHANNEL = os.environ['SLACK_CHANNEL']
USER_NAME = os.environ['USER_NAME']
SLACK_WEBHOOK_URL = os.environ['SLACK_WEBHOOK_URL']
KIBANA_URL = os.environ['KIBANA_URL']
ES_INDEXES = os.environ['ES_INDEXES']
ES_ENDPOINT = os.environ['ES_ENDPOINT']
UNIT_OF_TIME = os.environ['UNIT_OF_TIME']

def lambda_handler(event, context):
    # ログ集計する対象のバケット一覧取得
    notifyIndexes = ES_INDEXES
    print("Indexes: {}".format(notifyIndexes))
    
    # 各バケットから特定の条件に当てはまるログを取得し合算
    notifyTargets = ERROR_LEVEL.split(',')
    numOfTarget = {}
    for targetLevel in notifyTargets:
        numOfTarget[targetLevel] = get_sum_error(notifyIndexes, targetLevel)
        print("{}の合計: {}".format(targetLevel, numOfTarget[targetLevel]))
    
    # 1日の合計、指定した時間単位の平均値を取得
    errorSum = 0
    for sum in numOfTarget.values():
        errorSum += sum
    print("errorSum: 約{0}".format(errorSum))
    unit_of_time, unit_string = get_unit_of_time()
    daily_avarage = math.floor(calc_daily_avarage(errorSum, unit_of_time))
    print("avarage: {}".format(daily_avarage))
    
    ## Slackへ通知 (成功: 0, 失敗: 1)
    result = 0
    if len(SLACK_CHANNEL) > 0 and len(SLACK_WEBHOOK_URL) > 0:
        result = notifyToSlack(numOfTarget, daily_avarage, unit_string, KIBANA_URL)
    
    return {
        "statusCode": 200,
        "body": json.dumps('Hey! {}'.format(result))
    }
    
# 対象の文字列に引っかかるログを集計(前日分のみ)
def get_sum_error(notifyIndexes, targetLevel):
    result = 0
    for index in notifyIndexes:
        url = 'https://{}/{}/_count'.format(ES_ENDPOINT, index)
        data = ('{"query":{"query_string":{"query":"message:%s"}}}' % targetLevel)
        response = execute_query_to_es(url, data)
        result += (response.json()['count']) if ('count' in response.json()) else 0
    return result
    
# Elasticsearchのクエリ実行
def execute_query_to_es(url, data):
    request = AWSRequest(method="GET", url=url, data=data)
    if ("AWS_ACCESS_KEY_ID" in os.environ):
        # AWSマネージドのElasticsearchを使うために必要
        credentials = Credentials(os.environ["AWS_ACCESS_KEY_ID"], os.environ["AWS_SECRET_ACCESS_KEY"], os.environ["AWS_SESSION_TOKEN"])
        SigV4Auth(credentials, "es", os.environ["AWS_REGION"]).add_auth(request)
    return BotocoreHTTPSession().send(request.prepare())

# 1日のエラー件数を割るための数値を算出
def get_unit_of_time():
    if UNIT_OF_TIME == 'h':
        return 24, '時間'
    elif UNIT_OF_TIME == 'm':
        return 24 * 60, '分間'
    elif UNIT_OF_TIME == 's':
        return 24 * 60 * 60, '秒間'
    return 24, '時間' 

# 1日の合計を時間単位の平均に変換する
def calc_daily_avarage(errorSum, unit_of_time):
    return errorSum / unit_of_time
    
# Slackへ通知する
def notifyToSlack(numOfTarget, avarage, unit_string, url):
    level_text = ""
    # 指定した文字列と、それに紐づく件数をセット
    for level, sum in numOfTarget.items():
        level_text += '{}: {}件 \n'.format(level, sum)
    # SlackにPOSTする内容をセット
    slack_message = {
        'channel': SLACK_CHANNEL,
        'icon_emoji': ':female-technologist:',
        'username': USER_NAME,
        'text': 'みんなちゅうもーく！昨日出力された{}を発表しちゃうよー！ \n {} 1{}の平均: {}件 \n 詳細はこちら(kibana)→{}'.format(ERROR_LEVEL, level_text, unit_string, avarage, url)
        
    }
    headers = {
        'Content-Type': 'application/json'
    }

    # SlackにPOST
    req = urllib.request.Request(SLACK_WEBHOOK_URL, json.dumps(slack_message).encode(), headers)
    try:
        with urllib.request.urlopen(req) as res:
            body = res.read()
    except urllib.error.HTTPError as err:
        print(err.code)
        return 1
    except urllib.error.URLError as err:
        print(err.reason)
        return 1
    return 0
    