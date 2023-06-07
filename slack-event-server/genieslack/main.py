import datetime
import os
from typing import List
from urllib import parse

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

from dbmgr import mysql_driver


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
    installation_store=mysql_driver.MyInstallationStore(client_id=os.environ["SLACK_CLIENT_ID"]),
    state_store=mysql_driver.MyOAuthStateStore(expiration_seconds=600),
    callback_options=callback_options,
)


app = App(
    signing_secret=os.environ["SLACK_SIGNING_SECRET"],
    oauth_flow=OAuthFlow2(
        settings=oauth_settings
    )
)


@app.event("reaction_added")
def reaction_summarize(client: slack_sdk.web.client.WebClient, event):
    # リアクションを取得
    reaction = event["reaction"]

    # リアクションが:summarize:なら処理開始
    if reaction == "summarize":
        item = event["item"]
        try:
            # リアクションが押されたメッセージの内容を取得
            response = client.reactions_get(
                channel=item["channel"],
                timestamp=item["ts"],
                name=reaction
            )
            message = response["message"]['text']

            # esaから分類時に使用するカテゴリ一覧を取得
            categories = esa_api.get_genieslack_categories(ESA_TOKEN, 'ylab')

            # 投稿先がない場合、作成する
            if len(categories) == 0:
                # デフォルト記事を作成
                post_default_posts(ESA_TOKEN, 'ylab')
                # カテゴリ情報を再取得
                categories = esa_api.get_genieslack_categories(ESA_TOKEN, 'ylab')

            # メッセージを要約
            summarized_message_gift = chatgpt.summarize_message(message, categories)
            summarized_message = summarized_message_gift["message"]
            genre = summarized_message_gift["genre"]

            # ChatGPTの出力したgenreがesaのカテゴリ一覧に含まれているか確認
            if genre not in categories:
                # HACK: 含まれていない場合は適当に選択
                genre = categories[0]

            # 要約したメッセージを投稿
            url = post_message_to_esa(ESA_TOKEN, 'ylab', summarized_message, genre)

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


def post_message_to_esa(token: str, team_name: str, message: str, genre: str) -> str:
    """要約したメッセージをesa記事に追記する

    Args:
        token (str): esaのアクセストークン
        message (str): ChatGPTで要約したメッセージ
        genre (str): ChatGPTで判定した分類
        team_name (str): esaのチーム名

    Returns:
        str: 投稿先記事のフラグメント付きURL
    """
    # 投稿先の記事情報を取得
    post_info_list = esa_api.get_posts(token, team_name, f'title:{genre}')

    # 見出しとして使う時刻情報を取得
    title = str(datetime.datetime.now())

    # 追記する
    post_info = post_info_list[0]
    response = esa_api.edit_post(token, team_name, post_info['number'], esa_api.EditorialInfo(
        body_md=f"{post_info['body_md']}\n## {title}\n{message}\n"
    ))

    # HACK: 同じ名前の見出しが複数ある場合、一番上のものに飛んでしまう
    # 現在の実装ではは時刻情報を見出しとして使うため、重複しないことを想定している
    return f"{response['url']}#{parse.quote(title)}"

def post_default_posts(esa_token: str, team_name: str) -> List[str]:
    """デフォルト記事を作成する

    Args:
        esa_token (str): esaのアクセストークン
        team_name (str): esaのチーム名

    Returns:
        List[str]: 作成したデフォルト記事のURL
    """
    urls: List[str] = []
    for genre in ['Tips', '予定', 'タスク']:
        response = esa_api.send_post(esa_token, team_name, esa_api.PostedInfo(
            name=f'GenieSlack/{genre}',
            body_md=f'# {genre}\n'
        ))
        urls.append(response['url'])
    return urls

app.start(port=3000)
