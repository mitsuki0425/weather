import os
import requests
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, PushMessageRequest, TextMessage
from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

# 都市のリストを漢字＋座標で管理（lat/lonの方が確実）
CITIES = [
    {"name": "札幌", "lat": 43.06417, "lon": 141.34694},
    {"name": "千歳", "lat": 42.819, "lon": 141.652}
]


def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={city['lat']}&lon={city['lon']}&appid={OPENWEATHER_API_KEY}&lang=ja&units=metric"
    res = requests.get(url)
    data = res.json()

    weather_desc = data["weather"][0]["description"]
    temp = data["main"]["temp"]

    return f"{city['name']}の天気: {weather_desc}、気温: {temp}℃"


# 2地点の天気まとめ
weather_report = "\n".join([get_weather(city) for city in CITIES])
message_text = f"おはようございます！今日の天気です☀️\n\n{weather_report}"

# LINEに送信
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)

with ApiClient(configuration) as api_client:
    line_bot_api = MessagingApi(api_client)
    line_bot_api.push_message(
        PushMessageRequest(
            to="U2b8c739f1f2cce114f47e88d6e6b9fab",  # あなたのLINEユーザーID
            messages=[TextMessage(text=message_text)]
        )
    )
