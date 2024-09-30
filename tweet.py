import http.client
import json
import time
import random
import hmac
import hashlib
import base64
import urllib.parse
import argparse
from decouple import config

parser = argparse.ArgumentParser()

parser.add_argument('--text', action="store", dest='text', default='')
parser.add_argument('--crudtype', action="store", dest='crudtype', default='')
parser.add_argument('--tweetid', action="store", dest='tweetid', default='')

args = parser.parse_args()

def validCrudType(crudtype):
    switcher = {
        "POST": True,
        "GET": True,
        "DELETE": True,
        "UPDATE": True,
    }

    return switcher.get(crudtype, False)

if validCrudType(args.crudtype) == False:
    print("Invalid crudtype ", args.crudtype)
    exit(1)

# Consumer keys
TOKEN = config('TOKEN')
TOKEN_SECRET = config('TOKEN_SECRET')

#Access keys
ACCESS_TOKEN = config('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = config('ACCESS_TOKEN_SECRET')

# Timestamp and Nonce
TIMESTAMP = str(int(time.time()))
NONCE = ''.join([chr(random.randint(97, 122)) for i in range(32)])

# HMAC-SHA1 as the signature method
HMAC_METHOD = "HMAC-SHA1"
OAUTH_VERSION = "1.0"

# Twitter API endpoint
URL = "https://api.twitter.com/2/tweets"

# Parameters for the OAuth signature
params = {
    'oauth_consumer_key': TOKEN,
    'oauth_token': ACCESS_TOKEN,
    'oauth_signature_method': HMAC_METHOD,
    'oauth_timestamp': TIMESTAMP,
    'oauth_nonce': NONCE,
    'oauth_version': OAUTH_VERSION
}

# Function to percent-encode parameters
def percent_encode(s):
    return urllib.parse.quote(s, safe='')

# Create the base string for signing
def create_base_string(method, url, params):
    # Sort the parameters
    sorted_params = '&'.join([f'{percent_encode(k)}={percent_encode(v)}' for k, v in sorted(params.items())])
    
    # Construct the base string
    base_string = f"{method.upper()}&{percent_encode(url)}&{percent_encode(sorted_params)}"
    return base_string

# Create the signing key
def create_signing_key(consumer_secret, token_secret):
    return f"{percent_encode(consumer_secret)}&{percent_encode(token_secret)}"

# Generate the HMAC-SHA1 signature
def generate_signature(base_string, signing_key):
    hashed = hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha1)
    signature = base64.b64encode(hashed.digest()).decode()
    return signature

oauth_params = {
    'oauth_consumer_key': TOKEN,
    'oauth_token': ACCESS_TOKEN,
    'oauth_signature_method': HMAC_METHOD,
    'oauth_timestamp': TIMESTAMP,
    'oauth_nonce': NONCE,
    'oauth_version': OAUTH_VERSION,
}

base_string = create_base_string(args.crudtype, URL, oauth_params)

signing_key = create_signing_key(TOKEN_SECRET, ACCESS_TOKEN_SECRET)

OAUTH_SIGNATURE = generate_signature(base_string, signing_key)

oauth_params['oauth_signature'] = OAUTH_SIGNATURE

authorization_header = (
    'OAuth ' +
    ', '.join([f'{percent_encode(k)}="{percent_encode(v)}"' for k, v in oauth_params.items()])
)

conn = http.client.HTTPSConnection("api.twitter.com")
headers = {
    'Content-Type': 'application/json',
    'Authorization': authorization_header
}

if args.crudtype == "POST":
    # POST body data
    payload = json.dumps({
    "text": args.text
    })

    conn.request("POST", "/2/tweets", payload, headers)
    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))

if args.crudtype == "DELETE":
    # DELETE post

    conn.request("DELETE", "/2/tweets/" + args.tweetid, '', headers)
    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))