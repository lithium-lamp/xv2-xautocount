import http.client
import json
import base64
import hashlib
import os
from urllib.parse import urlencode, urlparse, parse_qs
from flask import Flask, request
from decouple import config

app = Flask(__name__)

CLIENTID = config('SPOTIFY_CLIENTID')
SPOTIY_USERNAME = config('SPOTIY_USERNAME')
REDIRECT_URI = 'http://localhost:12345/callback'
SCOPES = "user-read-playback-state user-read-currently-playing"
SCOPES += " playlist-read-collaborative user-follow-read user-read-playback-position"
SCOPES += " user-read-playback-position user-top-read user-read-recently-played"
SCOPES += " user-library-read"

code_verifier = None

def generate_code_verifier():
    return base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8').rstrip('=')

def generate_code_challenge(code_verifier):
    code_challenge = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    return base64.urlsafe_b64encode(code_challenge).decode('utf-8').rstrip('=')

@app.route('/callback')
def callback():
    global code_verifier

    code = request.args.get('code')
    if code:
        exchange_code_for_token(code)
        return "Authorization successful! You can close this window."

def exchange_code_for_token(authorization_code):
    token_url = "https://accounts.spotify.com/api/token"
    payload = {
        'grant_type': 'authorization_code',
        'code': authorization_code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENTID,
        'code_verifier': code_verifier
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    conn = http.client.HTTPSConnection("accounts.spotify.com")
    conn.request("POST", "/api/token", urlencode(payload), headers)
    res = conn.getresponse()
    data = res.read()

    decoded_data = data.decode("utf-8")
    access_data = json.loads(decoded_data)
    access_token = access_data.get('access_token')

    
    print(f"\naccess_token: {access_token}\n")

    fetch_user_data(access_token, SPOTIY_USERNAME)

def fetch_user_data(access_token, spotify_username):
    conn = http.client.HTTPSConnection("api.spotify.com")
    headers = {
        'Authorization': f"Bearer {access_token}"
    }

    conn.request("GET", f"/v1/users/{spotify_username}", '', headers)
    res = conn.getresponse()
    data = res.read()

    decoded_data = data.decode("utf-8")
    print(decoded_data)

if __name__ == "__main__":
    code_verifier = generate_code_verifier()
    code_challenge = generate_code_challenge(code_verifier)

    auth_url = f"https://accounts.spotify.com/authorize?{urlencode({
        'response_type': 'code',
        'client_id': CLIENTID,
        'redirect_uri': REDIRECT_URI,
        'scope': SCOPES,
        'code_challenge_method': 'S256',
        'code_challenge': code_challenge
    })}"

    print(f"Please go to this URL and authorize the app: {auth_url}")

    app.run(port=12345)