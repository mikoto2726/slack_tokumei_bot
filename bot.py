from flask import Flask, request, jsonify
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import configparser
import os

app = Flask(__name__)

# 設定ファイルの読み込み
config = configparser.ConfigParser()
config.read('config.ini')

# 設定ファイルからSlackのボットトークンを取得
SLACK_BOT_TOKEN = config.get('slack', 'bot_token')
client = WebClient(token=SLACK_BOT_TOKEN)

@app.route('/tokumei', methods=['POST'])
def tokumei():
    data = request.form
    text = data.get('text')
    channel_id = data.get('channel_id')

    try:
        # 匿名メッセージを送信
        response = client.chat_postMessage(channel=channel_id, text=f"{text}")
        return '', 200  # 空のレスポンスを返す
    except SlackApiError as e:
        error_message = e.response['error']
        return jsonify({
            "response_type": "ephemeral",
            "text": f"エラー: {error_message}"
        }), 200
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)