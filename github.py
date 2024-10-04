import subprocess
import http.client
import json
from decouple import config

PYTHONPATH = config('PYTHON_PATH')
TWEETPATH = config('TWEET_PATH')
TOKEN = config('GITHUB_TOKEN')

conn = http.client.HTTPSConnection("api.github.com")

payload = json.dumps({
    "query": """
query { 
  user(login: \"lithium-lamp\"){
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            contributionCount
            date
          }
        }
      }
    }
  }
}
"""
    })

headers = {
    'Content-Type': 'application/json',
    'User-Agent': 'python-requests/2.28.2',
    'Authorization': f"Bearer {TOKEN}"
    }

conn.request("POST", "/graphql", payload, headers)
res = conn.getresponse()
data = res.read()

decoded_data = data.decode("utf-8")
#print(decoded_data)

json_data = json.loads(decoded_data)
all_items = json_data.get('data').get('user').get('contributionsCollection').get('contributionCalendar').get('weeks')

recentweek = all_items[len(all_items) - 1].get('contributionDays')
today = recentweek[len(recentweek) - 1]

fulltext = "Today I made " + str(today.get('contributionCount')) + " contributions on github!"

command = [
    f"{PYTHONPATH}",
    f"{TWEETPATH}",
    "--user=xautocount",
    f'--text={fulltext}',
    '--crudtype=POST'
]

result = subprocess.run(command, capture_output=True, text=True)

print(result)