"""Python Flask WebApp Auth0 integration example
"""
#https://manage.auth0.com/dashboard/us/dev-om1yl9xu/applications/ES9xKv9sofGKjAXQ7cPem8w5m4m5A6yX/quickstart

import json
import http.client
from urllib.parse import quote
from os import environ as env
from urllib.parse import quote_plus, urlencode

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")


oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration',
)


# Controllers API
@app.route("/")
def home():

    conn = http.client.HTTPSConnection("dev-om1yl9xu.us.auth0.com")
    payload = "{\"client_id\":\"K8A17ZUn5GYly6loWmKsyGsFf25aFfd1\",\"client_secret\":\"tQt-KR24t7GUvHDM02Ekh_T3WRC_euntojCEB6ITbeZPc8NXYpuL6bomEx8a7KfW\",\"audience\":\"https://dev-om1yl9xu.us.auth0.com/api/v2/\",\"grant_type\":\"client_credentials\"}"
    headers = { 'content-type': "application/json" }
    conn.request("POST", "/oauth/token", payload, headers)
    res = conn.getresponse()
    data = res.read()
    #print(data.decode("utf-8"))
    stud_obj = json.loads(data.decode("utf-8"))
    access_token = stud_obj['access_token']
    #print(stud_obj['access_token'])
    authoriz = 'Bearer ' + access_token
    user_str = json.dumps(session.get("user"), indent=4)
    #print(data.decode("utf-8"))
    print(user_str)
    print('-----')
    user = json.loads(user_str)
    user_nickname = json.dumps(user['userinfo']['nickname'])
    print("The type of object is: ", type(user))
    #print(user_nickname)

    conn = http.client.HTTPSConnection("dev-om1yl9xu.us.auth0.com")

    headers = { 'authorization': authoriz }
    url_quote = quote('nickname:"'+user_nickname+'"')
    print(url_quote)
    conn.request("GET", "/api/v2/users?q="+url_quote+"&search_engine=v3", headers=headers)

    res = conn.getresponse()
    data2 = res.read()
    data_psw = json.loads(data2.decode("utf-8"))
    return render_template(
        "home.html",
        session=session.get("user"),
        pretty=json.dumps(session.get("user"), indent=4),
        json_psw=json.dumps(data_psw, indent=4),
    )


@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/")


@app.route("/login")
def login():
    #print(url_for("callback", _external=True))
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://"
        + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=env.get("PORT", 3000))
