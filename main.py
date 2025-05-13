import requests
from bs4 import BeautifulSoup
import time
import os

# === Einstellungen ===
BOT_TOKEN = "7847636484:AAE2tkFgrsanbKk3Tyxh_Uxh-_NKGBfU7Rw"
CHAT_ID   = "1001291102"
URL       = 'https://www.harry-gerlach.de/wohnung-mieten-berlin/'
BASIS_URL = "https://www.harry-gerlach.de/"
SEEN_FILE = "seen.txt"
INTERVAL  = 1800  # 30 Minuten

def load_seen():
    if not os.path.isfile(SEEN_FILE):
        return set()
    with open(SEEN_FILE, "r") as f:
        return set(line.strip() for line in f)

def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        for href in seen:
            f.write(href + "\n")

def sende_telegram(text):
    url  = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {'chat_id': CHAT_ID, 'text': text}
    try:
        requests.post(url, data=data, timeout=10)
    except Exception:
        pass  # wir unterdrücken Telegram-Fehler

def pruefe_neue_inserate():
    seen = load_seen()
    try:
        resp = requests.get(URL, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        neue = []
        for t in soup.select('a.media'):
            href  = t.get('href')
            title = t.find('img')['title'] if t.find('img') else 'kein Titel'
            if href and href not in seen:
                seen.add(href)
                neue.append((href, title))
        if neue:
            save_seen(seen)
            for href, title in neue:
                volle_url = BASIS_URL + href.lstrip('/')
                sende_telegram(f"📢 Neues Inserat: {title}\n🔗 {volle_url}")
    except Exception as e:
        sende_telegram(f"⚠️ Fehler im Bot: {e}")

if __name__ == "__main__":
    while True:
        pruefe_neue_inserate()
        time.sleep(INTERVAL)
