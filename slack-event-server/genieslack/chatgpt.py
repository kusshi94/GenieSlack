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
            except (openai.error.RateLimitError, openai.error.APIConnectionError):
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
    # 要約用プロンプト
    message_prompt = f"""\
以下の文章を要約してください。
すべてmarkdown形式のリストにして出力して下さい。
URLがある場合は必ず含めて下さい。

{message}
"""

    # 分類用プロンプト
    genre_prompt = f"""\
上記の文章のジャンルを以下の中から1つ選択して下さい。

[ジャンル]

""" + '\n'.join(categories)

    # openai.ChatCompletion.create 毎にエラー処理したいのでこういう形にしています

    @retry_wrapper
    def inner_message():
        print('Call chatgpt.summarize_message.intter_message')
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[
                {'role': 'user', 'content': message_prompt},
            ],
            temperature=0.25,
        )
        print('Finish chatgpt.summarize_message.intter_message')
        return response['choices'][0]['message']['content']

    summarized_message = inner_message()

    @retry_wrapper
    def inner_genre():
        print('Call chatgpt.summarize_message.inner_genre')
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[
                {'role': 'user', 'content': message_prompt},
                {'role': 'system', 'content': summarized_message},
                {'role': 'user', 'content': genre_prompt},
            ],
            temperature=0.25,
        )
        print('Finish chatgpt.summarize_message.inner_genre')
        return response['choices'][0]['message']['content']

    return {
        'message': summarized_message,
        'genre': inner_genre(),
    }


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