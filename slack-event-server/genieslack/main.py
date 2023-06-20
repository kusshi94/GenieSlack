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

import chatgpt, esa_api, slack, gui_contents
from dbmgr import mysql_driver

# .envファイルから環境変数を読み込む
dotenv.load_dotenv()

# esaのデフォルトカテゴリ
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
        first_msg=gui_contents.get_first_message_block(esa_oauth_url)
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

# インストール失敗時に呼び出される
def failure(args: FailureArgs) -> BoltResponse:
    assert args.request is not None
    assert args.reason is not None
    return BoltResponse(
        status=args.suggested_status_code,
        body="Your own response to end-users here"
    )   

# インストール成功時と失敗時のコールバックを設定
callback_options = CallbackOptions(success=success, failure=failure)

# add to slack ページの生成部分に関してオーバーライド
class OAuthFlow2(OAuthFlow):
    def build_install_page_html(self, url: str, request: BoltRequest) -> str:
        return gui_contents.get_install_page_html(url)

# OAuthの設定
oauth_settings = OAuthSettings(
    client_id=os.environ["SLACK_CLIENT_ID"],
    client_secret=os.environ["SLACK_CLIENT_SECRET"],
    scopes=["channels:history", "chat:write", "groups:history", "reactions:read", "im:history"],
    installation_store=mysql_driver.MyInstallationStore(client_id=os.environ["SLACK_CLIENT_ID"]),
    state_store=mysql_driver.MyOAuthStateStore(expiration_seconds=600),
    callback_options=callback_options,
)

# Bolt Appの設定
app = App(
    signing_secret=os.environ["SLACK_SIGNING_SECRET"],
    oauth_flow=OAuthFlow2(
        settings=oauth_settings
    )
)

# esaワークスペース選択開始リクエスト受信時の処理
@app.action('select-esa-team')
def show_esa_team_select_modal(ack, client, body):
    ack()

    slack_team_id = body['team']['id']

    with mysql_driver.EsaDB() as esa_db:
        esa_access_token, _ = esa_db.get_token_and_team_name(slack_team_id)

    # esaのOAuth認可がまだ完了していない場合
    if esa_access_token is None:
        show_send_btn = False
        blocks = gui_contents.get_esa_oauth_not_completed_block()
    # esaのOAuth認可は完了している = esaのチーム選択ができる場合
    else:
        team_list = esa_api.get_teams(esa_access_token)

        show_send_btn = True
        blocks = gui_contents.get_esa_team_select_block(team_list)

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

# esaのチーム選択モーダルでsubmitボタンが押されたときの処理
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

# ダイレクトメッセージを受け取った時の処理
# DMでの質問に対応していない旨を伝えるメッセージを返す
@app.message('')
def response_dm_message(message, say):
    if message['channel'].startswith('D'):
        say(
            'DMでの質問には対応していません。\n'
            '以下のリンクを参考にしてください。\n'
            '・使い方: https://www.genieslack.kusshi.dev/how-to-use \n'
            '・問い合わせ: https://www.genieslack.kusshi.dev/contact'
        )

# Slackのリアクションを受け取った時の処理
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
            # DBからの情報取得
            esa_token, esa_team_name = esa_db.get_token_and_team_name(slack_team_id)
            # 認証が完了していない場合
            if esa_token is None:
                slack.reply_to_message(
                    client=client,
                    channel_id=item['channel'],
                    message_ts=item['ts'],
                    message_content='esaのOAuth認証が完了していません。初期設定をやり直してください。'
                )
                return
            # ワークスペースが選択されていない場合
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
            # メッセージの内容を取得
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
            print('main.reaction_summarize: Start summarize')
            summarized_message_gift = chatgpt.summarize_message(message, categories)
            title = summarized_message_gift['title']
            summarized_message = summarized_message_gift["message"]
            genre = summarized_message_gift["category"]
            print('main.reaction_summarize: Finish summarize')

            # ChatGPTの出力したgenreがesaのカテゴリ一覧に含まれているか確認
            if genre not in categories:
                # HACK: 含まれていない場合は適当に選択
                genre = categories[0]

            # 要約したメッセージを投稿
            url = post_message_to_esa(esa_token, esa_team_name, title, summarized_message, genre)

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
    else:
        print('main.reaction_summarize: the reaction is not :summarize:. ignore it.')


def post_message_to_esa(token: str, team_name: str, title: str, message: str, genre: str) -> str:
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

    # タイトルに日時を追加
    dt_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    title = f"{dt_str} {title}"

    # 追記する
    post_info = post_info_list[0]
    response = esa_api.edit_post(token, team_name, post_info['number'], esa_api.EditorialInfo(
        body_md=f"{post_info['body_md']}\n## {title}\n{message}\n"
    ))

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
