import os
import requests
from datetime import datetime
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, PushMessageRequest, TextMessage
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_USER_ID = os.getenv("LINE_USER_ID")

# List of cities with coordinates
CITIES = [
    {"name": "札幌", "lat": 43.06417, "lon": 141.34694},
    {"name": "千歳", "lat": 42.819, "lon": 141.652}
]

# Rain-related keywords
RAIN_KEYWORDS = ["雨", "にわか雨", "小雨", "豪雨"]


def get_forecast(city):
    url = f"http://api.openweathermap.org/data/2.5/forecast?lat={city['lat']}&lon={city['lon']}&appid={OPENWEATHER_API_KEY}&lang=ja&units=metric"
    res = requests.get(url)
    data = res.json()

    if "list" not in data:
        return f"{city['name']}の天気予報を取得できませんでした（エラー: {data.get('message', '不明')})"

    today = datetime.utcnow().date()
    today_forecasts = [entry for entry in data["list"]
                       if datetime.fromtimestamp(entry["dt"]).date() == today]

    if not today_forecasts:
        return f"{city['name']}の今日の天気予報が見つかりませんでした。"

    temps = [entry["main"]["temp"] for entry in today_forecasts]
    weather_descriptions = [entry["weather"][0]["description"]
                            for entry in today_forecasts]
    pops = [entry.get("pop", 0) for entry in today_forecasts]

    temp_min = min(temps)
    temp_max = max(temps)
    weather_desc = weather_descriptions[0]
    max_pop = max(pops)

    has_rain_keyword = any(keyword in " ".join(weather_descriptions)
                           for keyword in RAIN_KEYWORDS)
    rain_note = "傘を忘れずに！" if max_pop > 0.3 or has_rain_keyword else ""

    return (
        f"{city['name']}の天気予報: {weather_desc}\n"
        f"予想最高気温: {temp_max:.1f}℃ / 予想最低気温: {temp_min:.1f}℃\n"
        f"{rain_note}"
    )


# Compile weather report for all cities
weather_report = "\n\n".join([get_forecast(city) for city in CITIES])
message_text = f"おはようございます！今日の天気予報です☀️\n\n{weather_report}"

# Send message via LINE
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)

with ApiClient(configuration) as api_client:
    line_bot_api = MessagingApi(api_client)
    line_bot_api.push_message(
        PushMessageRequest(
            to=LINE_USER_ID,
            messages=[TextMessage(text=message_text)]
        )
    )
