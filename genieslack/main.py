import datetime
import os

import dotenv
import slack_sdk
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from genieslack import chatgpt, esa_api, slack

dotenv.load_dotenv()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")

app = App(token=SLACK_BOT_TOKEN)

# TODO: 不要な権限を剥奪しておく
# @app.message("hello")  # 送信されたメッセージ内に"hello"が含まれていたときのハンドラ
# def ask_who(say):
#     print("can I help you?")

# @app.event("message") # ロギング
# def handle_message_events(body, logger):
#     # logger.info(body)
#     print("OK")

# TODO: 設計見直し


@app.event("reaction_added")
def reaction_summarize(client: slack_sdk.web.client.WebClient, event):
    # リアクションを取得
    reaction = event["reaction"]

    # リアクションが:summarize:なら処理開始
    if reaction == "summarize":
        item = event["item"]
        try:
            response = client.reactions_get(
                channel=item["channel"],
                timestamp=item["ts"],
                name=reaction
            )
            message = response["message"]

            # メッセージを要約
            summarized_message_gift = chatgpt.summarize_message(message)
            summarized_message = summarized_message_gift["message"]
            genre = summarized_message_gift["genre"]

            # 要約したメッセージを投稿
            url = post_message_to_esa(summarized_message, genre, "ylab")

            # urlをprint
            print(url)

            slack.reply_to_message(
                client=client,
                channel_id=item['channel'],
                message_ts=item['ts'],
                message_content=f"このメッセージを要約しました。\n以下の記事に書いてあります。\n{url}"
            )

        except slack_sdk.errors.SlackApiError as e:
            print("Error: {}".format(e))


def post_message_to_esa(message: str, genre: str, team_name: str) -> str:
    # 投稿先の記事情報を取得
    post_info_list = esa_api.get_posts(team_name, f'title:{genre}')

    if len(post_info_list['posts']) == 0:
        # 新規投稿
        response = esa_api.send_post(team_name, esa_api.PostedInfo(
            name=genre,
            body_md=f'# {genre}\n## {datetime.datetime.now()}\n{message}\n'
        ))
    else:
        # 追記
        post_info = post_info_list['posts'][0]
        response = esa_api.edit_post(team_name, post_info['number'], esa_api.EditorialInfo(
            body_md=f"{post_info['body_md']}\n## {datetime.datetime.now()}\n{message}\n"
        ))
    
    return response['url']


SocketModeHandler(app, SLACK_APP_TOKEN).start()
