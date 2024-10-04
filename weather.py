import subprocess
import http.client
import json
from decouple import config

PYTHONPATH = config('PYTHON_PATH')
TWEETPATH = config('TWEET_PATH')
KEY = config('WEATHER_KEY')
location = "Stockholm"

conn = http.client.HTTPSConnection("api.weatherstack.com")
payload = ''
headers = {}
conn.request("GET", f"/current?access_key={KEY}&query={location}", payload, headers)
res = conn.getresponse()
data = res.read()

decoded_data = data.decode("utf-8")
#print(decoded_data)

weather_data = json.loads(decoded_data)
current_weather = weather_data.get('current', {})
weather_descriptions = current_weather.get('weather_descriptions')[0].lower()
temperature = current_weather.get('temperature')
feelslike = current_weather.get('feelslike')
wind_speed = current_weather.get('wind_speed')

def get_weather_emoji(weather_code):
    weather_emoji_map = {
        395: "🌩️❄️",
        392: "🌩️🌨️",
        389: "⛈️",
        386: "🌩️🌧️",
        377: "🌨️",
        374: "🌨️",
        371: "❄️",
        368: "🌨️",
        365: "🌧️❄️",
        362: "🌧️❄️",
        359: "🌧️💧",
        356: "🌧️",
        353: "🌦️",
        350: "🧊",
        338: "❄️",
        335: "❄️",
        332: "❄️",
        329: "❄️",
        326: "🌨️",
        323: "🌨️",
        320: "🌧️❄️",
        317: "🌧️❄️",
        314: "🌧️❄️",
        311: "🌧️❄️",
        308: "🌧️🌧️",
        305: "🌧️",
        302: "🌧️",
        299: "🌧️",
        296: "🌦️",
        293: "🌦️",
        284: "❄️💧",
        281: "❄️💧",
        266: "🌧️",
        263: "🌧️",
        260: "🌫️❄️",
        248: "🌫️",
        230: "🌨️❄️",
        227: "🌬️❄️",
        200: "⛈️",
        185: "❄️💧",
        182: "🌧️❄️",
        179: "🌨️",
        176: "🌦️",
        143: "🌫️",
        122: "☁️",
        119: "☁️",
        116: "⛅",
        113: "☀️",
    }

    return weather_emoji_map.get(weather_code, "❓")

weather_emojis = get_weather_emoji(current_weather.get('weather_code'))

fulltext = f"The weather in {location} is currently {weather_descriptions} {weather_emojis}\n"
fulltext += f"The temperature is {temperature}°C, and feels like {feelslike}°C\n"
fulltext += f"The wind Speed is {wind_speed} km/h\n"

print(fulltext)

command = [
    f"{PYTHONPATH}",
    f"{TWEETPATH}",
    "--user=xautocount",
    f'--text={fulltext}',
    '--crudtype=POST'
]

result = subprocess.run(command, capture_output=True, text=True)

print(result)