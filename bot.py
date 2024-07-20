from flask import Flask, request, jsonify
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import configparser
import re

app = Flask(__name__)

# 設定ファイルの読み込み
config = configparser.ConfigParser()
config.read('config.ini')

# 設定ファイルからSlackのボットトークンを取得
SLACK_BOT_TOKEN = config.get('slack', 'bot_token')
client = WebClient(token=SLACK_BOT_TOKEN)

#URLからチャンネルIDとスレッドタイムスタンプを取得する
def parse_slack_url(text):
    pattern = r'https://[\w-]+\.slack\.com/archives/(\w+)/p(\d+)'
    match = re.search(pattern, text)
    
    if match:
        channel_id = match.group(1)
        thread_ts = f"{match.group(2)[:10]}.{match.group(2)[10:]}"
        return channel_id, thread_ts, text.replace(match.group(0), '').strip()
    else:
        return None, None, text

@app.route('/tokumei', methods=['POST'])
def tokumei():
    data = request.form
    text = data.get('text')
    channel_id = data.get('channel_id')

    # URLの解析
    url_channel_id, thread_ts, message = parse_slack_url(text)

    # チャンネルIDとスレッドタイムスタンプが見つかった場合はスレッドに送信
    if url_channel_id and thread_ts:
        try:
            response = client.chat_postMessage(
                channel=url_channel_id,
                text=f"{message}",
                thread_ts=thread_ts
            )
            return '', 200  # 空のレスポンスを返す
        except SlackApiError as e:
            error_message = e.response['error']
            return jsonify({
                "response_type": "ephemeral",
                "text": f"エラー: {error_message}"
            }), 200
    else:
        try:
            # URLがない場合、通常の匿名メッセージを送信
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
