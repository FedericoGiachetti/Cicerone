import requests
import os

def get_weather(city="Milano"):
    key = os.getenv("OPENWEATHER_API_KEY")
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={key}&units=metric&lang=it"
    r = requests.get(url).json()
    desc = r["weather"][0]["description"]
    temp = r["main"]["temp"]
    return f"{desc}, temperatura di {round(temp)} gradi celsius"
