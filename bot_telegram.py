"""
Bot Telegram per creare tornei Lichess via GitHub Actions.

Usage:
    python bot_telegram.py

Il bot risponde ai comandi:
    /start - Mostra il menu dei tornei
    /1 - Crea tournament 1+0 Bullet
    /2 - Crea tournament 2+1 Bullet
    /3 - Crea tournament 3+2 Chess960
    /aiuto - Mostra l'aiuto

Richiede env:
    TELEGRAM_TOKEN: token del bot Telegram
    GH_TOKEN: GitHub personal access token con repo access
    GH_REPO: formato "username/repository" (es. "filippogreco/Scacchi-PoliBOT")
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GH_TOKEN = os.getenv("GH_TOKEN")
GH_REPO = os.getenv("GH_REPO")

TIPI_TORNEO = {
    "1": {"nome": "1+0 Bullet Arena", "desc": "1 min + 0 sec"},
    "2": {"nome": "2+1 Bullet Arena", "desc": "2 min + 1 sec"},
    "3": {"nome": "3+2 Chess960 Arena", "desc": "3 min + 2 sec"},
}


def send_message(chat_id: int, text: str, reply_markup: dict = None) -> None:
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    dati = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
    }
    if reply_markup:
        dati["reply_markup"] = reply_markup
    requests.post(url, json=dati)


def trigger_github_action(tipo: str) -> bool:
    url = f"https://api.github.com/repos/{GH_REPO}/dispatches"
    headers = {
        "Authorization": f"token {GH_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }
    data = {"event_type": "crea_torneo", "client_payload": {"tipo": tipo}}
    risposta = requests.post(url, headers=headers, json=data)
    return risposta.status_code == 204


def get_keyboard() -> dict:
    return {
        "inline_keyboard": [
            [{"text": "1+0 Bullet", "callback_data": "torneo_1"}],
            [{"text": "2+1 Bullet", "callback_data": "torneo_2"}],
            [{"text": "3+2 Chess960", "callback_data": "torneo_3"}],
        ]
    }


def handle_message(update: dict) -> None:
    message = update.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "")

    if text == "/start":
        send_message(
            chat_id,
            "🏆 <b>Gestore Tornei Lichess</b>\n\nSeleziona il tipo di torneo:",
            reply_markup=get_keyboard(),
        )
    elif text == "/aiuto":
        send_message(
            chat_id,
            "Comandi disponibili:\n/start - Menu tornei\n/1 - 1+0 Bullet\n/2 - 2+1 Bullet\n/3 - 3+2 Chess960",
        )
    elif text in ["/1", "/2", "/3"]:
        tipo = text[1]
        send_message(chat_id, f"🚀 Creazione torneo {TIPI_TORNEO[tipo]['nome']}...")
        if trigger_github_action(tipo):
            send_message(
                chat_id,
                f"✅ Tournament {TIPI_TORNEO[tipo]['nome']} avviato! Riceverai il link su Telegram.",
            )
        else:
            send_message(chat_id, "❌ Errore nell'avvio del tournament. Riprova.")


def handle_callback(update: dict) -> None:
    callback = update.get("callback_query", {})
    chat_id = callback.get("message", {}).get("chat", {}).get("id")
    data = callback.get("data", "")

    if data.startswith("torneo_"):
        tipo = data.split("_")[1]
        send_message(chat_id, f"🚀 Creazione torneo {TIPI_TORNEO[tipo]['nome']}...")
        if trigger_github_action(tipo):
            send_message(chat_id, f"✅ Tournament {TIPI_TORNEO[tipo]['nome']} avviato!")
        else:
            send_message(chat_id, "❌ Errore. Riprova.")


def polling() -> None:
    offset = 0
    print("Bot Telegram in esecuzione... (CTRL+C per fermare)")

    while True:
        risposta = requests.get(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates",
            params={"offset": offset, "timeout": 30},
        )
        dati = risposta.json()

        for update in dati.get("result", []):
            offset = update["update_id"] + 1

            if "message" in update:
                handle_message(update)
            elif "callback_query" in update:
                handle_callback(update)


if __name__ == "__main__":
    if not all([TELEGRAM_TOKEN, GH_TOKEN, GH_REPO]):
        print("ERRORE: Variabili d'ambiente mancanti!")
        print("Richiede: TELEGRAM_TOKEN, GH_TOKEN, GH_REPO")
        exit(1)

    polling()
