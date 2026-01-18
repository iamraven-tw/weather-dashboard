"""
Personal Weather Dashboard
一個簡易的天氣查詢網站，用於教學 .env 與 .gitignore 的使用
"""

import os
from flask import Flask, render_template, request
from dotenv import load_dotenv
import requests

# 載入 .env 檔案中的環境變數
load_dotenv()

# 從環境變數讀取設定
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "default-secret-key")
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"
PORT = int(os.getenv("PORT", 5000))

# 建立 Flask 應用程式
app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY


def get_weather(city: str) -> dict | None:
    """
    呼叫 OpenWeatherMap API 取得天氣資料
    
    Args:
        city: 城市名稱 (英文)
    
    Returns:
        天氣資料字典，失敗則回傳 None
    """
    if not WEATHER_API_KEY:
        return {"error": "API Key 未設定！請檢查 .env 檔案"}
    
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": WEATHER_API_KEY,
        "units": "metric",  # 使用攝氏溫度
        "lang": "zh_tw"     # 中文描述
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if response.status_code == 200:
            return {
                "city": data["name"],
                "country": data["sys"]["country"],
                "temp": round(data["main"]["temp"]),
                "feels_like": round(data["main"]["feels_like"]),
                "humidity": data["main"]["humidity"],
                "description": data["weather"][0]["description"],
                "icon": data["weather"][0]["icon"],
            }
        elif response.status_code == 401:
            return {"error": "API Key 無效或尚未啟用（新申請的 Key 需等待約 10 分鐘）"}
        elif response.status_code == 404:
            return {"error": f"找不到城市：{city}"}
        else:
            return {"error": f"API 錯誤：{data.get('message', '未知錯誤')}"}
            
    except requests.exceptions.Timeout:
        return {"error": "連線逾時，請稍後再試"}
    except requests.exceptions.RequestException as e:
        return {"error": f"網路錯誤：{str(e)}"}


@app.route("/", methods=["GET", "POST"])
def index():
    """首頁：顯示天氣查詢表單與結果"""
    weather = None
    city = ""
    
    if request.method == "POST":
        city = request.form.get("city", "").strip()
        if city:
            weather = get_weather(city)
    
    return render_template("index.html", weather=weather, city=city)


if __name__ == "__main__":
    print(f"Weather Dashboard 啟動中...")
    print(f"請開啟瀏覽器訪問: http://localhost:{PORT}")
    print(f"Debug 模式: {DEBUG_MODE}")
    
    if not WEATHER_API_KEY:
        print("警告：WEATHER_API_KEY 未設定！請建立 .env 檔案")
    
    app.run(host="0.0.0.0", port=PORT, debug=DEBUG_MODE)
