import datetime
import os
from typing import List
from urllib import parse

import dotenv
import slack_sdk
from slack_bolt import App
from slack_bolt.context.say import Say
from slack_bolt.adapter.socket_mode import SocketModeHandler

import chatgpt, esa_api, slack

dotenv.load_dotenv()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")
ESA_TOKEN = os.getenv("ESA_TOKEN")

app = App (
    token=SLACK_BOT_TOKEN,
    signing_secret=SLACK_SIGNING_SECRET
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
        urls.append(response.url)
    return urls

app.start(port=3000)
