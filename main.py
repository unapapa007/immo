
import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime

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
    with open(path, "r") as f:
        return set(line.strip() for line in f if line.strip())

def save_seen(path, seen):
    with open(path, "w") as f:
        for h in seen:
            f.write(h + "\n")

# === Telegram senden ===
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
        log(f"HTTP {resp.status_code} OK für {site['name']}")
        soup = BeautifulSoup(resp.text, 'html.parser')
        neue = []
        for elem in soup.select(site['selector']):
            href = elem.get('href')
            title_tag = elem.find('img') or elem.find('h3')
            title = title_tag.get('title') if title_tag and title_tag.get('title') else elem.get_text(strip=True)
            if href and href not in seen:
                seen.add(href)
                neue.append((href, title))
        if neue:
            save_seen(site['seen_file'], seen)
            for href, title in neue:
                volle_url = site['base'] + href if href.startswith('/') else href
                sende_telegram(f"📢 Neues Inserat ({site['name']}): {title}\n🔗 {volle_url}")
        else:
            log(f"Keine neuen Inserate für {site['name']}")
    except Exception as e:
        log(f"Fehler beim Abruf {site['name']}: {e}")
        sende_telegram(f"⚠️ Fehler in {site['name']} Bot: {e}")

# === Einmalige Ausführung ===
if __name__ == "__main__":
    log("Bot-Run gestartet")
    for site in SITES:
        pruefe_site(site)
    log("Bot-Run beendet")
