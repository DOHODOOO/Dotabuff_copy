import os
import json
import subprocess
import requests
from flask import Flask, render_template

app = Flask(__name__)

TARGET_URL = "https://ru.dotabuff.com/heroes?show=heroes&view=winning&mode=all-pick&date=7d&rankTier=crusader"
DATA_FILE = "scraped_data.json"

@app.route('/')
def index():
    # Шаг 1: Проверяем доступность сайта с корректным User-Agent
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    try:
        response = requests.head(TARGET_URL, headers=headers, timeout=5)
        if response.status_code == 403:
            # Некоторые сервера запрещают HEAD, но разрешают GET — это нормально для Dotabuff, идем дальше.
            pass
        elif response.status_code != 200:
            return f"Dotabuff вернул код ошибки: {response.status_code}", 502
    except requests.RequestException:
        return "Не удалось связаться с целевым сайтом.", 503

    # Шаг 2: Запускаем Scrapy
    try:
        subprocess.run(['python', 'spider.py', DATA_FILE], check=True)
    except subprocess.CalledProcessError as e:
        return f"Ошибка при запуске Scrapy: {e}", 500

    # Шаг 3: Читаем JSON
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            try:
                scraped_items = json.load(f)
            except json.JSONDecodeError:
                scraped_items = []
    else:
        scraped_items = []

    # Шаг 4: Отрендерим в HTML
    return render_template('index.html', items=scraped_items, url=TARGET_URL)

if __name__ == '__main__':
    app.run(debug=True, port=5000)