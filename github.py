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

cont_count = today.get('contributionCount')

fulltext = "Today I made " + str(cont_count) + " contributions on github."

if (cont_count == 0):
    fulltext += " Aww man 😢"
elif (cont_count == 1):
    fulltext = "Today I made 1 contribution on github. That is okay I suppose 🙂"
elif (cont_count <= 3):
    fulltext += " Hmm yeah that is pretty good 😮"
elif (cont_count <= 6):
    fulltext += " Oh wow 😲"
elif (cont_count <= 9):
    fulltext += " That's a lot for one day 😶‍🌫️"
else:
    fulltext = "I made " + str(cont_count) + " contributions today??? Seriously?? 🤯"

command = [
    f"{PYTHONPATH}",
    f"{TWEETPATH}",
    "--user=xautocount",
    f'--text={fulltext}',
    '--crudtype=POST'
]

result = subprocess.run(command, capture_output=True, text=True)

print(result)