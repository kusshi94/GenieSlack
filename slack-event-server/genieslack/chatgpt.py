import json
import os
import time
from typing import List

import openai
import dotenv

dotenv.load_dotenv()
openai.api_key = os.getenv("OPENAI_APIKEY")


def retry_wrapper(func):
    def wrapper(*args, **kwargs):
        for _ in range(10):
            try:
                value = func(*args, **kwargs)
                break
            except (openai.error.RateLimitError, openai.error.APIConnectionError, openai.error.ServiceUnavailableError):
                print('retry: sleep 20s')
                time.sleep(20)
                continue
        else:
            print('failed')
            return None

        print('pass')
        return value
    return wrapper


def summarize_message(message: str, categories: List[str]) -> dict:
    # function calling用の関数
    def get_summarize_info(title: str, category: str) -> dict:
        return json.dumps({
            'title': title,
            'category': category,
        })
    
    # 分類とタイトル用の関数
    functions = [{
        'name': 'get_summarize_info',
        'description': '要約結果の情報を得る',
        'parameters': {
            'type': 'object',
            'properties': {
                'title': {
                    'type': 'string',
                    'description': '要約したメッセージのタイトル',
                },
                'category': {
                    'type': 'string',
                    'description': f"要約したメッセージのカテゴリ"
                }
            },
            'required': ['title', 'category'],
        }
    }]

    # 要約用プロンプト
    message_prompt = f"""\
    以下の文章を要約してください。
    すべてmarkdown形式のリストにして出力して下さい。

    [文章]
    {message}
    """

    # 分類とタイトル用プロンプト
    genre_title_prompt = f"""
    以下の文章のタイトルとジャンルを教えて下さい。
    文章のジャンルを以下の中から1つ選択してください。

    [文章]
    {message}

    [ジャンル]
    {categories}
    """

    # openai.ChatCompletion.create 毎にエラー処理したいのでこういう形にしています

    @retry_wrapper
    def inner_message():
        print('Call chatgpt.summarize_message.intter_message')
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo-0613',
            messages=[
                {'role': 'user', 'content': message_prompt},
            ],
            temperature=0.25,
        )
        print('Finish chatgpt.summarize_message.intter_message')
        return response['choices'][0]['message']['content']

    @retry_wrapper
    def inner_genre():
        print('Call chatgpt.summarize_message.inner_genre')
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo-0613',
            messages=[
                {'role': 'user', 'content': genre_title_prompt},
            ],
            temperature=0.25,
            functions=functions,
            function_call='auto',
        )
        print('Finish chatgpt.summarize_message.inner_genre')
        return response['choices'][0]['message']['function_call']['arguments']

    result_text = inner_genre()
    result = json.loads(result_text)
    result['message'] = inner_message()

    return result


if __name__ == '__main__':
    print(summarize_message("""\
feature/機能名 という名前のブランチを作ってPRしていく

新しいブランチを作る
git branch feature/XXXX
新しいブランチを作って、ブランチを切り替える
git checkout -b feature/XXXX
ブランチ一覧を表示する
git branch
ブランチを切り替える
git checkout feature/XXX or git switch feature/XXXX\
""", ['日程', '研究', 'お知らせ', '技術']))

    print(summarize_message("""\
明日11時から開会式なので、間に合うように、10:30目安に研究室に集合しましょう。
勿論、調子が悪ければ決して無理せず休んでください。
既に無理して参加してくれてると思いますが、なるべく楽しめる範囲で！頑張りましょう！\
""", ['日程', '研究', 'お知らせ', '技術']))
