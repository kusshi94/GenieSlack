import os

import MySQLdb
import dotenv

dotenv.load_dotenv()

class Installations:
    def __init__(self):
        self.conn = MySQLdb.connect(os.getenv('DB_HOST'), os.getenv('DB_USER'), os.getenv('DB_PASSWD'))
        self.cur = self.conn.cursor()
    
    def __del__(self):
        self.conn.close()


    # esaのurlのidからteam_idを同定する
    def get_team_id(self, esa_url_id: str) -> str:
        #TODO 動作テスト
        team_ids = self.cur.execute('''
            SELECT slack_team_id FROM esa_oauth WHERE esa_authorize_url_id = ?;
        ''', (esa_url_id, ))
        return team_ids.fetchone()


    # Slackの認証情報をまとめて読み出す
    def slack_installations(self):
        #TODO DBからまとめて情報を読み出す。まとめて復号化。pandasを使って実装予定
        self.cur.execute('''
            SELECT slack_team_id, encrypted_slack_access_token
            FROM slack_access_token;
        ''')
    
    # esaの認証情報を読み出す
    def get_esa_token(self, team_id: str) -> str:
        encrypted_tokens = self.cur.execute('''
            SELECT encrypted_esa_access_token
            FROM esa_access_token
            WHERE slack_team_id = ?;
        ''', (team_id, ))

        encrypted_token = encrypted_tokens.fetchone()
        #TODO 復号化処理
        token = encrypted_token
        return token

    def insert_slack(self, team_id: str, access_token: str):
        #TODO 暗号化処理
        encrypted_access_token = access_token
        self.cur.execute('''
            INSERT INTO slack_access_token KEYS (slack_team_id, encrypted_slack_access_token) VALUES (?, ?);
        ''', (team_id, encrypted_access_token))

        self.conn.commit()


    def insert_esa(self, team_id: str, access_token: str):
        #TODO 暗号化処理
        encrypted_access_token = access_token
        self.cur.execute('''
            INSERT INTO esa_access_token KEYS (slack_team_id, encrypted_esa_access_token) VALUES (?, ?);
        ''', (team_id, encrypted_access_token))

        self.conn.commit()


    def insert_esa_oauth(self, rand_id: str, team_id: str):
        self.cur.execute('''
            INSERT INTO esa_oauth KEYS (esa_authorize_url_id, slack_team_id) VALUES (?, ?);
        ''', (rand_id, team_id))

        self.conn.commit()

    