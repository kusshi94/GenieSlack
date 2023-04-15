import os

import slack_sdk
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from os.path import join, dirname
from dotenv import load_dotenv

load_dotenv()

## TODO 下でエラー発生：ImportError: cannot import name 'chatgpt' from partially initialized module 'genieslack'
# from genieslack import chatgpt, esa_api


SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")


app = App(token=SLACK_BOT_TOKEN)


# @app.message("hello")  # 送信されたメッセージ内に"hello"が含まれていたときのハンドラ
# def ask_who(say):
#     print("can I help you?")
    

# @app.event("message") # ロギング
# def handle_message_events(body, logger):
#     # logger.info(body)
#     print("OK")


@app.event("reaction_added")
def reaction_summarize(client: slack_sdk.web.client.WebClient, event):
    # print("event", event)

    reaction = event["reaction"]
    if reaction == "summarize":
        #print("summarize")
        item = event["item"]

        try:
            response = client.reactions_get(
                channel=item["channel"],
                timestamp=item["ts"],
                name=reaction
            )
            message = response["message"]
            print("summarize", message["text"])

        except slack_sdk.errors.SlackApiError as e:
            print("Error: {}".format(e))

    
SocketModeHandler(app, SLACK_APP_TOKEN).start()
