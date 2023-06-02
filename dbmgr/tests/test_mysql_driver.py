import os
import dotenv
import datetime
import time

import pytest
import sqlalchemy
from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker, scoped_session
from sqlalchemy.sql import text

from database.mysql_driver import slack_db_url, MyInstallationStore, MyOAuthStateStore, EsaDB


dotenv.load_dotenv()

@pytest.fixture(scope='session')
def esa_url() -> str:
    host, user, passwd, dbname = (
        os.getenv('DB_HOST'),
        os.getenv('DB_USER'),
        os.getenv('DB_PASSWD'),
        os.getenv('ESA_DB_NAME'),
    )
    return f'mysql://{user}:{passwd}@{host}/{dbname}'

@pytest.fixture(scope='session')
def slack_url() -> str:
    host, user, passwd, dbname = (
        os.getenv('DB_HOST'),
        os.getenv('DB_USER'),
        os.getenv('DB_PASSWD'),
        os.getenv('SLACK_DB_NAME'),
    )
    return f'mysql://{user}:{passwd}@{host}/{dbname}'

@pytest.fixture(scope='session')
def slack_engine(slack_url: str) -> Engine:
    return sqlalchemy.create_engine(slack_url)


@pytest.fixture(scope='session')
def esa_session(esa_url: str) -> Session:
    engine: Engine = sqlalchemy.create_engine(esa_url)
    session = scoped_session(sessionmaker(bind=engine))()
    yield session
    session.execute(text('TRUNCATE TABLE esa_access_token;'))
    session.execute(text('TRUNCATE TABLE esa_oauthinfo;'))
    session.close()



@pytest.fixture
def my_installation_store():
    client_id = 'test_client_id'
    return MyInstallationStore(client_id=client_id)

@pytest.fixture
def my_oauth_state_store():
    expiration_seconds=600
    return MyOAuthStateStore(expiration_seconds=expiration_seconds)

@pytest.fixture
def esa_db() -> EsaDB:
    return EsaDB()


def test_slack_db_url(slack_url: str):
    assert slack_db_url() == slack_url


def test_my_installation_store(my_installation_store: MyInstallationStore, slack_engine: Engine):
    assert my_installation_store.client_id == 'test_client_id'
    assert my_installation_store.engine.url == slack_engine.url



def test_my_oauth_state_store(my_oauth_state_store: MyOAuthStateStore, slack_engine: Engine):
    assert my_oauth_state_store.expiration_seconds == 600
    assert my_oauth_state_store.engine.url == slack_engine.url



def test_esa_db(esa_db: EsaDB, esa_session: Session):
    with esa_db:
        n = 10
        team_id = [f'team_id_{i}' for i in range(n)]
        url_id = [f'url_id_{i}' for i in range(n)]
        token = [f'token_{i}' for i in range(n)]


        # insert_oauthinfo, insert_tokenのテスト
        
        for i in range(n):
            esa_db.insert_oauthinfo(url_id[i], team_id[i], datetime.datetime.now())
            esa_db.insert_token(team_id[i], token[i])
        
        result_oauth = esa_session.execute(text('SELECT count(*) FROM esa_oauthinfo;'))
        result_token = esa_session.execute(text('SELECT count(*) FROM esa_access_token;'))
        esa_session.commit() # 明示的にトランザクションを切る
        
        assert result_oauth.fetchone()[0] == n
        assert result_token.fetchone()[0] == n


        # get_team_id, get_tokenのテスト
        for i in range(n):
            assert esa_db.get_team_id(url_id[i]) == team_id[i]
            assert esa_db.get_token(team_id[i]) == token[i]
        

        # delete_tokenのテスト
        for i in range(n-1):
            esa_db.delete_token(team_id[i])
            esa_db.delete_oauthinfo(url_id[i])
        result_token = esa_session.execute(text('SELECT slack_team_id, esa_access_token FROM esa_access_token;'))
        result_oauth = esa_session.execute(text('SELECT esa_oauth_url_id, slack_team_id FROM esa_oauthinfo;'))
        esa_session.commit() # 明示的にトランザクションを切る
        assert result_token.fetchone() == (team_id[n-1], token[n-1])
        assert result_oauth.fetchone() == (url_id[n-1], team_id[n-1])


        # delete_old_oauthinfoのテスト
        s = 5
        time.sleep(s) # s秒スリープ
        
        esa_db.insert_oauthinfo(f'url_id_{n}', f'team_id_{n}', datetime.datetime.now()) # 新たにデータを挿入
        esa_db.delete_old_oauthinfo(datetime.timedelta(seconds=s-1)) # s-1秒以上前のデータを削除
        result_oauth = esa_session.execute(text('SELECT * FROM esa_oauthinfo;'))
        esa_session.commit()
        print(result_oauth.fetchall())
        result_oauth = esa_session.execute(text('SELECT esa_oauth_url_id, slack_team_id FROM esa_oauthinfo;'))
        assert result_oauth.fetchone() == (f'url_id_{n}', f'team_id_{n}')

