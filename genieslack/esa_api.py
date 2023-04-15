import dataclasses
import json
import os
from typing import List, Optional, Union

import requests

from dotenv import load_dotenv

load_dotenv()


def get_posts(team_name: str, query : str = '') -> dict:
    """記事の一覧を取得する
    (https://docs.esa.io/posts/102#GET%20/v1/teams/:team_name/posts)

    Args:
        team_name (str): チーム名
        query (str, optional): 記事を絞り込むための条件. Defaults to ''.

    Returns:
        List[Post]: 記事の一覧の情報
    """
    r = requests.get(
        f"https://api.esa.io/v1/teams/{team_name}/posts",
        params={
            'q': query,
        },
        headers={
            'Authorization': f"Bearer {os.getenv('ESA_TOKEN')}",
        },
    )
    j = json.loads(r.content)
    print(j)

    r.raise_for_status()

    return j


def get_post(team_name: str, post_number: str) -> dict:
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
            'Authorization': f"Bearer {os.getenv('ESA_TOKEN')}",
        },
    )
    j = json.loads(r.content)
    print(j)

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


def send_post(team_name: str, post: PostedInfo) -> dict:
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
            'Authorization': f"Bearer {os.getenv('ESA_TOKEN')}",
            'Content-Type': 'application/json',
        },
        data=json.dumps({
            'post': post.to_dict(),
        }),
    )
    j = json.loads(r.content)
    print(j)

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


def edit_post(team_name: str, post_number: str, post: EditorialInfo) -> dict:
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
            'Authorization': f"Bearer {os.getenv('ESA_TOKEN')}",
            'Content-Type': 'application/json',
        },
        data=json.dumps({
            'post': post.to_dict(),
        }),
    )
    j = json.loads(r.content)
    print(j)

    r.raise_for_status()

    return j


def delete_post(team_name: str, post_number: str) -> None:
    """指定した投稿を削除

    Args:
        team_name (str): チーム名
        post_number (str): 記事の番号
    """
    r = requests.delete(
        f"https://api.esa.io/v1/teams/{team_name}/posts/{post_number}",
        headers={
            'Authorization': f"Bearer {os.getenv('ESA_TOKEN')}",
        },
    )
    j = json.loads(r.content)
    print(j)

    r.raise_for_status()


# TODO: ただの実行例なので、使わくなったら if __name__ ... 以下は消して下さい
if __name__ == '__main__':
    post_info_list = get_posts('ylab', 'Title1')

    # 重複確認
    if len(post_info_list) == 0:
        # 新規投稿
        post_info = send_post('ylab', PostedInfo(
            name='Title1',
            body_md='# title\n- line1\n- line2\n- line3'
        ))
    else:
        # 追記
        post_info = post_info_list['posts'][0]
        edit_post('ylab', post_info['number'], EditorialInfo(
            body_md=f"{post_info['body_md']}\n- 追記部分"
        ))
