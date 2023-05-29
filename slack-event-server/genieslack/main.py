import datetime
import os

import dotenv
import slack_sdk
from slack_bolt import App
from slack_bolt.context.say import Say
from slack_bolt.adapter.socket_mode import SocketModeHandler

import html
from slack_bolt.oauth.oauth_settings import OAuthSettings
from slack_bolt.oauth.oauth_flow import OAuthFlow
from slack_bolt.request import BoltRequest
from slack_sdk.oauth.installation_store import FileInstallationStore
from slack_sdk.oauth.state_store import FileOAuthStateStore

from slack_bolt.oauth.callback_options import CallbackOptions, SuccessArgs, FailureArgs
from slack_bolt.response import BoltResponse
from slack_sdk.errors import SlackApiError

import random
import string

import chatgpt, esa_api, slack

dotenv.load_dotenv()




# 初回メッセージの際に、パラメータrand_valueを生成して、esaのoauthのurlを作成する。
def generate_esa_oauth_url(slack_team_id: str) -> str:
	rand_value = ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(16)])
	# TODO: dbにslack_team_idとrandvalueを保存する (DB用のモジュールが完成したら実装)
	return f"https://genieslack.kusshi.dev/esa/oauth?rand_value={rand_value}"



# インストール成功時に呼び出される
# 初回メッセージの送信
def success(args: SuccessArgs) -> BoltResponse:
    installation = args.installation
    print("installations:")
    print(installation.team_id)
    client = args.request.context.client
    try:
        esa_oauth_url=generate_esa_oauth_url(installation.team_id)
        first_msg=[
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "こんにちは！ 👋 私はGenieSlackです！:slack:\n Slack, ChatGPT, esa を使って、Slack内のナレッジを簡単にesaにまとめられる機能をあなたに提供します！"
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "GenieSlackを始めるために取り組んでいただきたいことが2点あります！"
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "*1️⃣ ”ワークスペース上で、「要約して(summarize)」 リアクションを作成してください。* \n 以下、要約してリアクションの作成方法の説明..."
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": f"*2️⃣ GenieSlack と esa を連携させてください.*\n 以下、esa と連携させる方法の説明... \n:star: <{esa_oauth_url}|esa API へのリンク（今はテスト用にgoogle）> \n"
			}
		},
		{
			"type": "image",
			"title": {
				"type": "plain_text",
				"text": "image1"
			},
			"image_url": "https://api.slack.com/img/blocks/bkb_template_images/onboardingComplex.jpg",
			"alt_text": "image1"
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "以上、よろしくお願いいたします!:pray:"
			}
		}
	]
        client.chat_postMessage(
            token=installation.bot_token, # Use the token you just got from oauth.v2.access API response
            channel=installation.user_id,  # Only with chat.postMessage API, you can use user_id here
            text="Hello!",
            blocks=first_msg
        )
        return args.default.success(args)
    except SlackApiError as e:
        # TODO error handling
        print("error")


def failure(args: FailureArgs) -> BoltResponse:
    assert args.request is not None
    assert args.reason is not None
    return BoltResponse(
        status=args.suggested_status_code,
        body="Your own response to end-users here"
    )   
       
callback_options = CallbackOptions(success=success, failure=failure)       






# add to slack ページの生成に関してオーバーライド
class OAuthFlow2(OAuthFlow):
    def build_install_page_html(self, url: str, request: BoltRequest) -> str:
        return f"""<html>
<head>
<link rel="icon" href="data:,">
<style>
body {{
  padding: 10px 15px;
  font-family: verdana;
  text-align: center;
}}
</style>
</head>
<body>
<h2>GenieSlack  Installation</h2>
<p><a href="{html.escape(url)}"><img alt=""Add to Slack"" height="40" width="139" src="https://platform.slack-edge.com/img/add_to_slack.png" srcset="https://platform.slack-edge.com/img/add_to_slack.png 1x, https://platform.slack-edge.com/img/add_to_slack@2x.png 2x" /></a></p>
</body>
</html>
""" 


oauth_settings = OAuthSettings(
    client_id=os.environ["SLACK_CLIENT_ID"],
    client_secret=os.environ["SLACK_CLIENT_SECRET"],
    scopes=["app_mentions:read", "channels:history", "channels:read","chat:write",
            "groups:history","groups:read","reactions:read","reactions:write",],
    # user_scopes=["channels:read", "chat:write"],
    installation_store=FileInstallationStore(base_dir="./data/installations"),
    state_store=FileOAuthStateStore(expiration_seconds=600, base_dir="./data/states"),
    callback_options=callback_options,
)


app = App(
    signing_secret=os.environ["SLACK_SIGNING_SECRET"],
    oauth_flow=OAuthFlow2(
        settings=oauth_settings
    )
)




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
            message = response["message"]['text']

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


app.start(port=3000)
