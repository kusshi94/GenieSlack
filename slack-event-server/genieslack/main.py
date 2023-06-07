import datetime
import html
import os
import random
import string
from typing import List
from urllib import parse

import dotenv
import slack_sdk
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_bolt.context.say import Say
from slack_bolt.oauth.callback_options import CallbackOptions, SuccessArgs, FailureArgs
from slack_bolt.oauth.oauth_flow import OAuthFlow
from slack_bolt.oauth.oauth_settings import OAuthSettings
from slack_bolt.request import BoltRequest
from slack_bolt.response import BoltResponse
from slack_sdk.errors import SlackApiError
from slack_sdk.oauth.installation_store import FileInstallationStore
from slack_sdk.oauth.state_store import FileOAuthStateStore

import chatgpt, esa_api, slack
from dbmgr import mysql_driver

dotenv.load_dotenv()

DEFAULT_CATEGORIES = ['Tips', '予定', 'タスク']


# 初回メッセージの際に、パラメータrand_valueを生成して、esaのoauthのurlを作成する。
def generate_esa_oauth_url(slack_team_id: str) -> str:
    rand_value = ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(16)])
    with mysql_driver.EsaDB() as esa_db:
        esa_db.insert_oauthinfo(url_id=rand_value, team_id=slack_team_id, generated_at=str(datetime.datetime.utcnow()))
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
				"text": "こんにちは 👋 GenieSlackを追加していただきありがとうございます！:slack:\n Slackの情報を簡潔に要約・カテゴライズして、esaでその情報を見れる機能を提供いたします!"
			}
		},
		{
			"type": "divider"
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "GenieSlackを始めるために取り組んでいただきたいことが *3つ* あります！\n"
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": ":star:より初期設定のより詳しい説明は<https://www.genieslack.kusshi.dev/how-to-use/|こちら>をご覧ください👉"
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "*1️⃣  「要約して(summarize)」リアクションの作成* \n ① Slackを開いて、メッセージ送信欄にある絵文字ボタンをクリックします\n ②ポップアップメニューから *「絵文字を追加する」ボタン* をクリックします\n③ *「画像をアップロードする」ボタン* を押し、「要約して」用の画像を指定します\n④ *「名前を付ける」* で `:summarize:` を入力します\n⑤ 最後に *「保存する」ボタン* をクリックして、新たな絵文字の追加を完了します"
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "*2️⃣  esaとの連携*"
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": f"① Webブラウザで<{esa_oauth_url}|こちら>にアクセスします\n"
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "②esaにログインします (ログイン済みの場合は省略されます)\n③GenieSlackから権限が要求されます。問題なければ承認してください\n\n⚠️承認が失敗した場合はお手数ですが①からやり直してください。"
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "*3️⃣  esaのワークスペースを選択*\n\n⚠️ 2️⃣を終了した後に取り組んでください."
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "① 右のボタンを押して、ワークスペースを選択してください👉\n"
			},
			"accessory": {
				"type": "button",
				"text": {
					"type": "plain_text",
					"text": "Esaワークスペースの選択"
				},
				"value": "hoge",
				"action_id": "select-esa-team"
			}
		},
		{
			"type": "divider"
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "初期設定は以上になります！\n *GenieSlackの初期設定を完了して、効果的な情報管理を実現しましょう！*"
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
        return f"""<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Add GenieSlack to Slack</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300&family=Oswald:wght@500&family=Work+Sans:wght@800&display=swap" rel="stylesheet">
    <style>
        body {{
            margin: 0;
            padding: 0;
            background-color: #ebe4f7; /* 淡い紫色の背景 */
            overflow: hidden; /* スクロールを禁止 */
        }}
        
        .container {{
            display: flex;
            height: 100vh;
        }}
        
        .logo-section {{
            flex: 1;
            display: flex;
            align-items: flex-start;
            justify-content: flex-start;
            padding: 20px;
            position: fixed;
            top: 0;
            left: 0;
        }}
        
        .logo-section h1 {{
            font-size: 30px;
            font-weight: bold;
            color: #4f008f; /* ポップな文字の色 */
            font-family: 'Work Sans', sans-serif;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3); /* テキストに影をつける */
        }}
        
        .content-section {{
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            background-color: #ebe4f7; /* 淡い紫色の背景 */
        }}
        
        .content-box {{
            padding: 20px;
            background-color: #fff5e5; /* 淡いクリーム色の背景 */
            border-radius: 10px; /* 角がなく丸みを帯びた形 */
            text-align: center;
        }}
        
        .add-to-slack {{
            max-width: 200px;
            height: auto;
        }}
        
        .subtitle {{
            font-size: 38px;
            color: #48442f; /* ポップな文字の色 */
            font-family: 'Oswald', sans-serif;
            margin: 0.2em 0px;
            text-align:left
        }}

        .appname {{
            font-size: 80px;
            color: #3b3827; /* ポップな文字の色 */
            font-family: 'Work Sans', sans-serif;
            margin: 0.2em 0px;
            text-align:left
        }}
        
        .description {{
            margin: 0.8em 0px;
            font-size: 20px;
            font-weight: bold;
            color: #6e6849; /* ポップな文字の色 */
            text-align:left
        }}

        #footer {{
            border-top: solid 1px lightgray;
            padding-bottom: 10px;
          }}
        #footer p {{
            text-align: center;
            font-family: 'Noto Sans JP', sans-serif;
        }}
    </style>
</head>

<body>
    <div class="container">
        <div class="logo-section">
            <a href="https://www.genieslack.kusshi.dev/">
                <h1>GenieSlack</h1>
            </a>
        </div>
        <div class="content-section">
            <div class="content-box">
                <p class="subtitle">Let's manage <br> your knowledge easily!</p>
                <p class="appname">GenieSlack</p>
                <p class="description">重要な情報の見逃しや情報の散在を防ぎ、<br>チーム全体のコラボレーションを強化できます。</p>
                <a href="{html.escape(url)}"><img alt="Add to Slack" height="48" width="167" src="https://platform.slack-edge.com/img/add_to_slack.png" srcset="https://platform.slack-edge.com/img/add_to_slack.png 1x, https://platform.slack-edge.com/img/add_to_slack@2x.png 2x" /></a>
            </div>
        </div>
    </div>
    <footer id="footer">
        <p>©︎ チーム勝成</p>    
    </footer>
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


@app.action('select-esa-team')
def show_esa_team_select_modal(ack, client, body):
    ack()

    slack_team_id = body['team']['id']

    with mysql_driver.EsaDB() as esa_db:
        esa_access_token, _ = esa_db.get_token_and_team_name(slack_team_id)

    # esaのOAuth認可がまだ完了していない場合
    if esa_access_token is None:
        show_send_btn = False
        blocks = [
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "*esaのOAuth認可が完了していません。*\n*認可が完了してからもう一度試してください。*"
                    }
                ]
            }
        ]
    # esaのOAuth認可は完了している = esaのチーム選択ができる場合
    else:
        team_list = esa_api.get_teams(esa_access_token)

        show_send_btn = True
        blocks = [
            {
                "type": "input",
                "block_id": "select-block",
                "element": {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select an item",
                        "emoji": True
                    },
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": team_name,
                                "emoji": True
                            },
                            "value": team_name
                        }
                        for team_name in team_list
                    ],
                    "action_id": "static_select-action"
                },
                "label": {
                    "type": "plain_text",
                    "text": "esaのチームを選択してください",
                    "emoji": True
                }
            }
        ]

    send_dict = {
        'submit': {
            'type': 'plain_text',
            'text': '決定',
        },
        'close': {
            'type': 'plain_text',
            'text': 'キャンセル',
        }
    } if show_send_btn else {}

    client.views_open(
        trigger_id=body['trigger_id'],
        view={
            'type': 'modal',
            'callback_id': 'esa-team-select-modal',
            'title': {
                'type': 'plain_text',
                'text': 'esa: チーム選択',
            },
            **send_dict,
            'blocks': blocks,
        }
    )


@app.view('esa-team-select-modal')
def handle_esa_team_select_modal(ack, view, say, body):
    slack_team_id = body['team']['id']
    slack_user_id = body['user']['id']
    inputs = view['state']['values']
    esa_team_name = inputs.get('select-block', {}).get('static_select-action', {}).get('selected_option', {}).get('value')

    # チーム名が取得できなかったとき
    if esa_team_name is None:
        print('error')
        ack()
        say(
            text='esaのチーム名の選択に失敗しました。\n選択をもう一度やり直してください。',
            channel=slack_user_id,
        )
        return


    with mysql_driver.EsaDB() as esa_db:
        esa_db.update_esa_team_name(slack_team_id, esa_team_name)

    ack()
    say(
        text=f"esaのチーム名の選択に成功しました！\nチーム: {esa_team_name}",
        channel=slack_user_id
    )


@app.event("reaction_added")
def reaction_summarize(client: slack_sdk.web.client.WebClient, event, body):
    # リアクションを取得
    reaction = event["reaction"]

    # リアクションが:summarize:なら処理開始
    if reaction == "summarize":
        item = event["item"]
        
        # esaのトークンとワークスペース名を取得
        slack_team_id = body['team_id']
        with mysql_driver.EsaDB() as esa_db:
            esa_token, esa_team_name = esa_db.get_token_and_team_name(slack_team_id)
            if esa_token is None:
                slack.reply_to_message(
                    client=client,
                    channel_id=item['channel'],
                    message_ts=item['ts'],
                    message_content='esaのOAuth認証が完了していません。初期設定をやり直してください。'
                )
                return
            elif esa_team_name is None:
                slack.reply_to_message(
                    client=client,
                    channel_id=item['channel'],
                    message_ts=item['ts'],
                    message_content='esaのチーム選択が完了していません。初期設定をやり直してください。'
                )
                return
        
        try:
            # リアクションが押されたメッセージの内容を取得
            response = client.reactions_get(
                channel=item["channel"],
                timestamp=item["ts"],
                name=reaction
            )
            message = response["message"]['text']

            # esaから分類時に使用するカテゴリ一覧を取得
            categories = esa_api.get_genieslack_categories(esa_token, esa_team_name)

            # 投稿先がない場合、作成する
            if len(categories) == 0:
                # デフォルト記事を作成
                post_default_posts(esa_token, esa_team_name)
                # デフォルトのカテゴリをセットする
                categories = DEFAULT_CATEGORIES

            # メッセージを要約
            print('Start summarize')
            summarized_message_gift = chatgpt.summarize_message(message, categories)
            summarized_message = summarized_message_gift["message"]
            genre = summarized_message_gift["genre"]
            print('Finish summarize')

            # ChatGPTの出力したgenreがesaのカテゴリ一覧に含まれているか確認
            if genre not in categories:
                # HACK: 含まれていない場合は適当に選択
                genre = categories[0]

            # 要約したメッセージを投稿
            url = post_message_to_esa(esa_token, esa_team_name, summarized_message, genre)

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
    for genre in DEFAULT_CATEGORIES:
        response = esa_api.send_post(esa_token, team_name, esa_api.PostedInfo(
            name=f'GenieSlack/{genre}',
            body_md=f'# {genre}\n'
        ))
        urls.append(response['url'])
    return urls


if __name__ == '__main__':
    app.start(port=3000)
