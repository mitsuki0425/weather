import os
import requests
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, PushMessageRequest, TextMessage
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

# List of cities with coordinates
CITIES = [
    {"name": "札幌", "lat": 43.06417, "lon": 141.34694},
    {"name": "千歳", "lat": 42.819, "lon": 141.652}
]

# Keywords indicating rain
RAIN_KEYWORDS = ["雨", "雷", "霧", "にわか雨", "小雨", "豪雨", "雪"]


def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={city['lat']}&lon={city['lon']}&appid={OPENWEATHER_API_KEY}&lang=ja&units=metric"
    res = requests.get(url)
    data = res.json()

    if "weather" not in data or "main" not in data:
        return f"{city['name']}の天気情報を取得できませんでした（エラー: {data.get('message', '不明')})"

    weather_desc = data["weather"][0]["description"]
    temp = data["main"]["temp"]
    temp_min = data["main"]["temp_min"]
    temp_max = data["main"]["temp_max"]

    rain_note = "傘を忘れずに！" if any(
        keyword in weather_desc for keyword in RAIN_KEYWORDS) else ""

    return (
        f"{city['name']}の天気: {weather_desc}\n"
        f"現在の気温: {temp}℃\n"
        f"最高気温: {temp_max}℃ / 最低気温: {temp_min}℃\n"
        f"{rain_note}"
    )


# Compile weather report for all cities
weather_report = "\n\n".join([get_weather(city) for city in CITIES])
message_text = f"おはようございます！今日の天気です☀️\n\n{weather_report}"

# Send message via LINE
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)

with ApiClient(configuration) as api_client:
    line_bot_api = MessagingApi(api_client)
    line_bot_api.push_message(
        PushMessageRequest(
            # LINE user ID from environment variable
            to=os.getenv("LINE_USER_ID"),
            messages=[TextMessage(text=message_text)]
        )
    )
