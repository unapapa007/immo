import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime

# === Einstellungen ===
BOT_TOKEN = "7847636484:AAE2tkFgrsanbKk3Tyxh_Uxh-_NKGBfU7Rw"
CHAT_ID   = "1001291102"
SITES = [
    {
        "name": "Harry-Gerlach",
        "url": "https://www.harry-gerlach.de/wohnung-mieten-berlin/",
        "base": "https://www.harry-gerlach.de",
        "selector": "a.media",
        "seen_file": "seen_harry.txt"
    },
    {
        "name": "GESOBAU",
        "url": "https://www.gesobau.de/mieten/wohnungssuche/",
        "base": "https://www.gesobau.de",
        # präziser Selector für Gesobau: Link im Titel
        "selector": "h3.basicTeaser__title a[href]",
        "seen_file": "seen_gesobau.txt"
    }
]
TIMEOUT  = 20    # Sekunden Timeout
LOG_FILE = "bot.log"

# === Logging-Funktion ===
def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")

# === Seen-Management ===
def load_seen(path):
    if not os.path.isfile(path):
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
        requests.post(url, data=data, timeout=TIMEOUT)
        log(f"Telegram gesendet: {text}")
    except Exception as e:
        log(f"Telegram-Fehler: {e}")

# === Prüfen einer einzelnen Seite ===
def pruefe_site(site):
    log(f"Starte Abruf: {site['name']} ({site['url']})")
    seen = load_seen(site['seen_file'])
    try:
        resp = requests.get(site['url'], timeout=TIMEOUT)
        resp.raise_for_status()
        log(f"HTTP {resp.status_code} OK für {site['name']}")
        soup = BeautifulSoup(resp.text, 'html.parser')
        elements = soup.select(site['selector'])
        log(f"Gefundene Elemente für {site['name']}: {len(elements)}")
        neue = []
        for elem in elements:
            href = elem.get('href')
            title = elem.get_text(strip=True)
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

 