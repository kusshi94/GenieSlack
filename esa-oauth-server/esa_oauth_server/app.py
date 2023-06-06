import datetime
import os

import dotenv
from flask import Flask, render_template, redirect, request, session
from oauthlib.oauth2.rfc6749.errors import InvalidGrantError
from requests_oauthlib import OAuth2Session

from dbmgr import mysql_driver

dotenv.load_dotenv()
client_id = os.environ['ESA_CLIENT_ID']
client_secret = os.environ['ESA_CLIENT_SECRET']

redirect_uri = 'https://genieslack.kusshi.dev/esa/redirect_uri'
scope = ['read', 'write']
session_min = 10

app = Flask(__name__, template_folder='../templates')
app.secret_key = os.urandom(24)
app.permanent_session_lifetime = datetime.timedelta(minutes=session_min)


# 認可開始エンドポイント /esa/oauth?team_id=<rand_value>
@app.route('/esa/oauth')
def start_oauth():
    if 'rand_value' not in request.args:
        return render_template(
            'error.html', 
            error_statement='Slackのワークスペース情報がありません。もう一度、正しいEsaの認可URLにアクセスして下さい。'
        )

    rand_value = request.args['rand_value']
    with mysql_driver.EsaDB() as esa_db:
        slack_team_id = esa_db.get_team_id(rand_value)

    session.parmanet = True
    session['slack_team_id'] = slack_team_id
    
    oauth = OAuth2Session(
        client_id=client_id,
        redirect_uri=redirect_uri,
        scope=scope,
    )

    authorization_url, state = oauth.authorization_url('https://api.esa.io/oauth/authorize')
    print(authorization_url, state)

    session['state'] = state

    return redirect(authorization_url)


# リダイレクトURI /esa/redirect_uri?code=<認可コード>&state=<Stateの値>
@app.route('/esa/redirect_uri')
def callback():
    if 'state' not in session:
        return render_template(
            'error.html', 
            error_statement=f"認可に{session_min}分以上かかり、セッションが切れています。再度SlackのURLからやり直してください。"
        )
    elif 'state' not in request.args:
        return render_template(
            'error.html', 
            error_statement=f"state情報がありません。もう一度、正しいEsaの認可URLにアクセスして下さい。"
        )
    elif session['state'] != request.args['state']:
        return render_template(
            'error.html', 
            error_statement=f"stateが一致しません。再度、アクセスしてください"
        )

    oauth = OAuth2Session(
        client_id=client_id,
        redirect_uri=redirect_uri,
        scope=scope,
    )

    try:
        token = oauth.fetch_token(
            token_url='https://api.esa.io/oauth/token',
            client_secret=client_secret,
            code=request.args.get('code'),
        )
    except InvalidGrantError:
        return render_template(
            'error.html', 
            error_statement=f"認可コードが正しくありません。再度、アクセスしてください"
        )

    with mysql_driver.EsaDB() as esa_db:
        esa_db.insert_token(team_id=session['slack_team_id'], access_token=token['access_token'])

    return render_template('finish.html')


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
