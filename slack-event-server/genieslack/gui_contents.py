import html
from typing import List
# SlackのメッセージブロックとインストールページのGUI定義

# インストール時の初期メッセージ
def get_first_message_block(esa_oauth_url :str) -> List[dict]:
	return [
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

# esaのOAuth認可未完了時
def get_esa_oauth_not_completed_block() -> List[dict]:
	return [
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

# esaのワークスペース選択
def get_esa_team_select_block(team_list :List[str]) -> List[dict]:
	return [
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

# インストールページのhtmlを取得
def get_install_page_html(url :str) -> str:
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
                <p>アプリのインストールにより、<a href="https://www.genieslack.kusshi.dev/terms-of-service/">利用規約</a>に同意したものとみなします。</p>
            </div>
        </div>
    </div>
    <footer id="footer">
        <p>©︎ チーム勝成</p>    
    </footer>
</body>

</html>
"""