import os
import dotenv
import datetime
import logging
from logging import Logger

import MySQLdb
import sqlalchemy
from sqlalchemy import Engine
from slack_sdk.oauth.state_store.sqlalchemy import SQLAlchemyOAuthStateStore
from slack_sdk.oauth.installation_store.sqlalchemy import SQLAlchemyInstallationStore

dotenv.load_dotenv()


def slack_db_url() -> str:
    host, user, passwd, dbname = (
        os.getenv('DB_HOST'),
        os.getenv('DB_USER'),
        os.getenv('DB_PASSWD'),
        os.getenv('SLACK_DB_NAME')
    )
    return f'mysql://{user}:{passwd}@{host}/{dbname}'



class MyInstallationStore(SQLAlchemyInstallationStore):
    def __init__(
        self,
        client_id: str,
        bots_table_name: str = SQLAlchemyInstallationStore.default_bots_table_name,
        installations_table_name: str = SQLAlchemyInstallationStore.default_installations_table_name,
        logger: Logger = logging.getLogger(__name__),
    ):
        engine: Engine = sqlalchemy.engine.create_engine(slack_db_url())

        super().__init__(
            client_id=client_id, 
            engine=engine, 
            bots_table_name=bots_table_name, 
            installations_table_name=installations_table_name, 
            logger=logger,
        )

        # データベースにslack_installationsが存在しないとテーブルを作成する
        self.metadata.create_all(engine)

        # TODO: 暗号化、復号化処理


class MyOAuthStateStore(SQLAlchemyOAuthStateStore):
    
    def __init__(
        self,
        expiration_seconds: int,
        logger: Logger = logging.getLogger(__name__),
        table_name: str = SQLAlchemyOAuthStateStore.default_table_name,
    ):
        
        engine: Engine = sqlalchemy.engine.create_engine(slack_db_url())

        super().__init__(
            expiration_seconds=expiration_seconds,
            engine=engine,
            logger=logger,
            table_name=table_name,
        )

        # データベースにslack_oauth_statesが存在しないとテーブルを作成する
        self.metadata.create_all(engine)



class EsaDB:

    def __enter__(self):
        self.conn = MySQLdb.connect(
            host=os.getenv('DB_HOST'), 
            user=os.getenv('DB_USER'), 
            passwd=os.getenv('DB_PASSWD'),
            db=os.getenv('ESA_DB_NAME')
        )
        self.cur = self.conn.cursor()
        
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS esa_access_token (
                slack_team_id varchar(16) NOT NULL PRIMARY KEY,
                esa_access_token varchar(128) NOT NULL,
                created_at datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at datetime NOT NULL DEFAULT CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP
            );
        """)
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS esa_oauthinfo (
                esa_oauth_url_id varchar(128) NOT NULL PRIMARY KEY,
                slack_team_id varchar(16) NOT NULL,
                generated_at datetime NOT NULL,
                created_at datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at datetime NOT NULL DEFAULT CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP
            );
        """)
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.conn.close()


    # esaのurlのidからteam_idを同定する
    def get_team_id(self, esa_url_id: str) -> str:
        n = self.cur.execute("""
            SELECT slack_team_id FROM esa_oauthinfo WHERE esa_oauth_url_id = %s;
        """, (esa_url_id, ))
        return self.cur.fetchone()[0] if n != 0 else None



    # esaの認証情報を読み出す
    def get_token(self, team_id: str) -> str:
        n = self.cur.execute("""
            SELECT esa_access_token
            FROM esa_access_token
            WHERE slack_team_id = %s;
        """, (team_id, ))

        token = self.cur.fetchone()[0] if n != 0 else None
        #TODO: 復号化処理
        return token


    def insert_token(self, team_id: str, access_token: str):
        #TODO: 暗号化処理
        self.cur.execute("""
            INSERT IGNORE INTO esa_access_token (slack_team_id, esa_access_token) VALUES (%s, %s);
        """, (team_id, access_token))

        self.conn.commit()


    def insert_oauthinfo(self, url_id: str, team_id: str, generated_at: datetime.datetime):
        self.cur.execute("""
            INSERT IGNORE INTO esa_oauthinfo (esa_oauth_url_id, slack_team_id, generated_at) VALUES (%s, %s, %s);
        """, (url_id, team_id, generated_at))

        self.conn.commit()


    
    def delete_token(self, team_id: str):
        self.cur.execute("""
            DELETE FROM esa_access_token WHERE slack_team_id = %s;
        """, (team_id, ))

        self.conn.commit()
    
    def delete_oauthinfo(self, url_id: str):
        self.cur.execute("""
            DELETE FROM esa_oauthinfo WHERE esa_oauth_url_id = %s;
        """, (url_id, ))

        self.conn.commit()

    
    def delete_old_oauthinfo(self, period: datetime.timedelta = datetime.timedelta(hours=3)):
        print(datetime.datetime.now())
        print(datetime.datetime.now() - period)
        self.cur.execute("""
            DELETE FROM esa_oauthinfo WHERE generated_at < %s;
        """, (datetime.datetime.now() - period, ))

        self.conn.commit()


