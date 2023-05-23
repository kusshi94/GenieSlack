import os

import MySQLdb
import dotenv
import datetime

# デバッグ用
import json

dotenv.load_dotenv()

class Authentication:
    def __init__(self):
        self.conn = MySQLdb.connect(
            host=os.getenv('DB_HOST'), 
            user=os.getenv('DB_USER'), 
            passwd=os.getenv('DB_PASSWD'),
            db='genieslack_authentication'
        )
        self.cur = self.conn.cursor()
    
    def __del__(self):
        self.conn.close()


    # esaのurlのidからteam_idを同定する
    def team_id(self, esa_url_id: str) -> str:
        n = self.cur.execute('''
            SELECT slack_team_id FROM esa_oauth WHERE esa_oauth_url_id = %s;
        ''', (esa_url_id, ))
        return self.cur.fetchone()[0] if n != 0 else None


    # Slackの認証情報をまとめて読み出す
    def slack_installations(self):
        self.cur.execute('''
            SELECT slack_team_id, slack_access_token
            FROM slack_access_token;
        ''')
        installations = self.cur.fetchall()
        #TODO DBからまとめて情報を読み出す。まとめて復号化。
        return installations


    def slack_token(self, team_id: str) -> str:
        n = self.cur.execute('''
            SELECT slack_access_token
            FROM slack_access_token
            WHERE slack_team_id = %s;
        ''', (team_id, ))
        token = self.cur.fetchone()[0] if n != 0 else None
        #TODO 復号化処理
        return token


    # esaの認証情報を読み出す
    def esa_token(self, team_id: str) -> str:
        n = self.cur.execute('''
            SELECT esa_access_token
            FROM esa_access_token
            WHERE slack_team_id = %s;
        ''', (team_id, ))

        token = self.cur.fetchone()[0] if n != 0 else None
        #TODO 復号化処理
        return token


    def insert_slack_token(self, team_id: str, access_token: str):
        #TODO 暗号化処理
        #TODO データ重複時の処理 (とりあえず重複時は挿入しない)
        self.cur.execute('''
            INSERT IGNORE INTO slack_access_token (slack_team_id, slack_access_token) VALUES (%s, %s);
        ''', (team_id, access_token))

        self.conn.commit()


    def insert_esa_token(self, team_id: str, access_token: str):
        #TODO 暗号化処理
        self.cur.execute('''
            INSERT IGNORE INTO esa_access_token (slack_team_id, esa_access_token) VALUES (%s, %s);
        ''', (team_id, access_token))

        self.conn.commit()


    def insert_esa_oauth(self, url_id: str, team_id: str):
        self.cur.execute('''
            INSERT IGNORE INTO esa_oauth (esa_oauth_url_id, slack_team_id, generated_at) VALUES (%s, %s, %s);
        ''', (url_id, team_id, datetime.datetime.now()))

        self.conn.commit()

    def del_slack_token(self, team_id: str):
        self.cur.execute('''
            DELETE FROM slack_access_token WHERE slack_team_id = %s;
        ''', (team_id,))

        self.conn.commit()

    
    def del_esa_token(self, team_id: str):
        self.cur.execute('''
            DELETE FROM esa_access_token WHERE slack_team_id = %s;
        ''', (team_id, ))

        self.conn.commit()
    
    def del_esa_oauth(self, url_id: str):
        self.cur.execute('''
            DELETE FROM esa_oauth WHERE esa_oauth_url_id = %s;
        ''', (url_id, ))

        self.conn.commit()





if __name__ == '__main__':

    # デバッグ用
    def insertdb(n):
        for i in range(n):
            auth.insert_slack_token(
                slack_access_tokens['slack_team_id'][i],
                slack_access_tokens['slack_access_token'][i]
            )

            auth.insert_esa_token(
                esa_access_tokens['slack_team_id'][i],
                esa_access_tokens['esa_access_token'][i]
            )

            auth.insert_esa_oauth(
                esa_oauth['esa_url_id'][i],
                esa_oauth['slack_team_id'][i]
            )

    def printdb(n):
        print('Auth.slack_token()')
        for i in range(n):
            print(i, auth.slack_token(slack_access_tokens['slack_team_id'][i]))

        print()
        print('Auth.esa_token()')
        for i in range(n):
            print(i, auth.esa_token(esa_access_tokens['slack_team_id'][i]))
        
        print()
        print('Auth.esa_token()')
        for i in range(n):
            print(i, auth.team_id(esa_oauth['esa_url_id'][i]))
        
        print()
        print('Auth.slack_installations()')
        print(auth.slack_installations())
        print()

    def deldb(n):
        for i in range(n):
            auth.del_slack_token(slack_access_tokens['slack_team_id'][i])

        for i in range(n):
            auth.del_esa_token(esa_access_tokens['slack_team_id'][i])

        for i in range(n):
            auth.del_esa_oauth(esa_oauth['esa_url_id'][i])


    # テスト用データ生成 (データ数: n)
    n = 10
    
    slack_access_tokens = {
        'slack_team_id': [],
        'slack_access_token': []
    }

    esa_access_tokens = {
        'slack_team_id': [],
        'esa_access_token': []
    }

    esa_oauth = {
        'esa_url_id': [],
        'slack_team_id': []
    }

    for i in range(n):
        slack_team_id = 'slack_team_id_{:02d}'.format(i)
        slack_access_token = 'slack_access_token_{:02d}'.format(i)
        esa_access_token = 'esa_access_token_{:02d}'.format(i)
        esa_url_id = 'esa_url_id_{:02d}'.format(i)
        
        slack_access_tokens['slack_team_id'].append(slack_team_id)
        slack_access_tokens['slack_access_token'].append(slack_access_token)
        
        esa_access_tokens['slack_team_id'].append(slack_team_id)
        esa_access_tokens['esa_access_token'].append(esa_access_token)
        
        esa_oauth['esa_url_id'].append(esa_url_id)
        esa_oauth['slack_team_id'].append(slack_team_id)

    print(json.dumps(slack_access_tokens, indent=4))
    print(json.dumps(esa_access_tokens, indent=4))
    
    auth = Authentication()

    # insertできているか
    insertdb(n)

    # 出力できるか
    printdb(n)

    # 削除できるか
    deldb(n)

    
    # 表示
    printdb(n)


