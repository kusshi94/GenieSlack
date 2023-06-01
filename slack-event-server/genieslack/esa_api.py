import dataclasses
import json
import os
from typing import List, Optional, Union

import requests

from dotenv import load_dotenv

load_dotenv()

def get_posts(token: str, team_name: str, query: str = '') -> List[dict]:
    """記事の一覧を取得する
    (https://docs.esa.io/posts/102#GET%20/v1/teams/:team_name/posts)

    Args:
        token (str): esaのAPIトークン
        team_name (str): チーム名
        query (str, optional): 記事を絞り込むための条件. Defaults to ''.

    Returns:
        List[dict]: 記事の一覧の情報
    """
    # 記事一覧
    # 1記事1dict
    posts: List[dict] = []

    # ページネーション
    page: int = 1
    while True:
        # HTTP GET request
        # 1ページ分の記事一覧を取得
        resp = requests.get(
            f"https://api.esa.io/v1/teams/{team_name}/posts",
            params={
                'q': query,
                'page': page,
            },
            headers={
                'Authorization': f"Bearer {token}",
            },
        )
        
        # HTTP エラーチェック
        resp.raise_for_status()

        # レスポンスをdictに変換
        resp_body: dict = json.loads(resp.content)

        # 取得した記事を一覧に追加
        posts.extend(resp_body['posts'])

        # 次のページがなければ終了
        if resp_body['next_page'] is None:
            break
        # ページ番号を更新
        page = resp_body['next_page']        

    return posts


def get_post(token: str, team_name: str, post_number: str) -> dict:
    """指定された投稿を取得
    (https://docs.esa.io/posts/102#GET%20/v1/teams/:team_name/posts/:post_number)

    Args:
        team_name (str): チーム名
        post_number (str): 記事の番号

    Returns:
        dict: 記事の情報
    """
    r = requests.get(
        f"https://api.esa.io/v1/teams/{team_name}/posts/{post_number}",
        headers={
            'Authorization': f"Bearer {token}",
        },
    )
    j = json.loads(r.content)
    # print(j)

    r.raise_for_status()

    return j


@dataclasses.dataclass
class PostedInfo:
    name : str
    body_md : Optional[str] = None
    tags : Optional[Union[List[str], str]] = None
    category : Optional[str] = None
    wip : bool = True
    message : Optional[str] = None
    user : Optional[str] = None
    template_post_id : Optional[int] = None

    def to_dict(self):
        """name以外で値がNoneのものは除いてdictに変換"""
        return {
            'name': self.name,
            **{
                key: value for key, value in vars(self).items()
                if key != 'name' and value is not None
            }
        }


def send_post(token: str, team_name: str, post: PostedInfo) -> dict:
    """記事を新たに投稿
    (https://docs.esa.io/posts/102#POST%20/v1/teams/:team_name/posts)

    Args:
        team_name (str): チーム名
        post (PostedInfo): 投稿する記事の情報

    Returns:
        dict: 投稿された記事の情報
    """
    r = requests.post(
        f"https://api.esa.io/v1/teams/{team_name}/posts",
        headers={
            'Authorization': f"Bearer {token}",
            'Content-Type': 'application/json',
        },
        data=json.dumps({
            'post': post.to_dict(),
        }),
    )
    j = json.loads(r.content)
    # print(j)

    r.raise_for_status()

    return j


@dataclasses.dataclass
class OriginalRevision:
    body_md : Optional[str] = None
    number : Optional[int] = None
    user : Optional[str] = None

    def to_dict(self):
        """値がNoneのものは除いてdictに変換"""
        return {
            key: value for key, value in vars(self).items()
            if key != 'name' and value is not None
        }


@dataclasses.dataclass
class EditorialInfo:
    name : Optional[str] = None
    body_md : Optional[str] = None
    tags : Optional[Union[List[str], str]] = None
    category : Optional[str] = None
    wip : bool = True
    message : Optional[str] = None
    created_by : Optional[str] = None
    updated_by : Optional[str] = None
    original_revision: Optional[OriginalRevision] = None

    def to_dict(self):
        """値がNoneのものは除いてdictに変換"""
        return {
            key: (value.to_dict() if key == 'original_revision' else value) 
            for key, value in vars(self).items()
            if key != 'name' and value is not None
        }


def edit_post(token: str, team_name: str, post_number: str, post: EditorialInfo) -> dict:
    """指定した記事を編集

    Args:
        team_name (str): チーム名
        post_number (str): 記事の番号
        post (EditorialInfo): 編集する記事の情報

    Returns:
        dict: 編集された記事の情報
    """
    r = requests.patch(
        f"https://api.esa.io/v1/teams/{team_name}/posts/{post_number}",
        headers={
            'Authorization': f"Bearer {token}",
            'Content-Type': 'application/json',
        },
        data=json.dumps({
            'post': post.to_dict(),
        }),
    )
    j = json.loads(r.content)
    # print(j)

    r.raise_for_status()

    return j


def delete_post(token: str, team_name: str, post_number: str) -> None:
    """指定した投稿を削除

    Args:
        team_name (str): チーム名
        post_number (str): 記事の番号
    """
    r = requests.delete(
        f"https://api.esa.io/v1/teams/{team_name}/posts/{post_number}",
        headers={
            'Authorization': f"Bearer {token}",
        },
    )
    j = json.loads(r.content)
    # print(j)

    r.raise_for_status()

def get_genieslack_categories(token: str, team_name: str) -> List[str]:
    """GenieSlackが分類に使うカテゴリの一覧を取得

    Args:
        token (str): esaのAPIトークン
        team_name (str): チーム名
    
    Returns:
        List[str]: カテゴリの一覧
    """

    # GenieSlackの投稿する記事の一覧を取得
    posts = get_posts(token, team_name, 'in:"GenieSlack"')

    # GenieSlack/ 配下の記事名を取得し、ChatGPTに分類させる際のカテゴリとして扱う
    # ただし、プレフィックスのGenieSlack/は除く
    # 例：[GenieSlack/プログラミング/Python,
    #     GenieSlack/学会情報,
    #     GenieSlack/論文情報, ...]
    # -> [プログラミング/Python, 学会情報, 論文情報, ...]
    categories: List[str] = [
        post['full_name'][len('GenieSlack/'):]
        for post in posts
    ]

    return categories

if __name__ == '__main__':
    print(get_genieslack_categories(os.getenv('ESA_TOKEN'), 'ylab'))