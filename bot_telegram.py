"""
Bot Telegram per creare tornei Lichess via GitHub Actions.

Usage:
    python bot_telegram.py

Il bot risponde ai comandi:
    /start - Mostra il menu dei tornei
    /bullet - Crea tournament 1+0 Bullet
    /blitz - Crea tournament 2+1 Blitz
    /chess960 - Crea tournament 3+2 Chess960
    /aiuto - Mostra l'aiuto

Richiede env:
    TELEGRAM_TOKEN: token del bot Telegram
    GH_TOKEN: GitHub personal access token con repo access
    GH_REPO: formato "username/repository" (es. "filippogreco/Scacchi-PoliBOT")
"""

import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GH_TOKEN = os.getenv("GH_TOKEN")
GH_REPO = os.getenv("GH_REPO")

# Whitelist di User ID autorizzati
AUTHORIZED_USERS = {
    652283475,  # Filippo
    1163968938 # Leonardo
}

# File di log
LOG_FILE = "torneo_log.txt"

TIPI_TORNEO = {
    "1": {"nome": "1+0 Bullet", "cmd": "/bullet"},
    "2": {"nome": "2+1 Blitz", "cmd": "/blitz"},
    "3": {"nome": "3+2 Chess960", "cmd": "/chess960"},
}

COMANDI = {v["cmd"]: k for k, v in TIPI_TORNEO.items()}


def log_torneo(user_id: int, username: str, tipo: str) -> None:
    """Registra nel file chi ha lanciato il torneo."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nome_tipo = TIPI_TORNEO[tipo]["nome"]
    log_entry = f"[{timestamp}] {username} ({user_id}) ha lanciato: {nome_tipo}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry)
    print(log_entry.strip())


def is_authorized(user_id: int) -> bool:
    """Controlla se l'utente è autorizzato."""
    return user_id in AUTHORIZED_USERS


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
            [{"text": "2+1 Blitz", "callback_data": "torneo_2"}],
            [{"text": "3+2 Chess960", "callback_data": "torneo_3"}],
        ]
    }


def handle_message(update: dict) -> None:
    message = update.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    user_id = message.get("from", {}).get("id")
    username = message.get("from", {}).get("username", "Unknown")
    text = message.get("text", "")

    # Controlla autorizzazione
    if not is_authorized(user_id):
        send_message(chat_id, "❌ Non sei autorizzato a usare questo bot.")
        return

    if text == "/start":
        send_message(
            chat_id,
            "🏆 <b>Gestore Tornei Lichess</b>\n\nSeleziona il tipo di torneo:",
            reply_markup=get_keyboard(),
        )
    elif text == "/aiuto":
        send_message(
            chat_id,
            "Comandi disponibili:\n/start - Menu tornei\n/bullet - 1+0 Bullet\n/blitz - 2+1 Blitz\n/chess960 - 3+2 Chess960",
        )
    elif text in COMANDI:
        tipo = COMANDI[text]
        nome = TIPI_TORNEO[tipo]["nome"]
        send_message(chat_id, f"🚀 Creazione torneo {nome}...")
        if trigger_github_action(tipo):
            log_torneo(user_id, username, tipo)
            send_message(
                chat_id,
                f"✅ Tournament {nome} avviato! Riceverai il link su Telegram.",
            )
        else:
            send_message(chat_id, "❌ Errore nell'avvio del tournament. Riprova.")


def handle_callback(update: dict) -> None:
    callback = update.get("callback_query", {})
    chat_id = callback.get("message", {}).get("chat", {}).get("id")
    user_id = callback.get("from", {}).get("id")
    username = callback.get("from", {}).get("username", "Unknown")
    data = callback.get("data", "")

    # Controlla autorizzazione
    if not is_authorized(user_id):
        send_message(chat_id, "❌ Non sei autorizzato a usare questo bot.")
        return

    if data.startswith("torneo_"):
        tipo = data.split("_")[1]
        nome = TIPI_TORNEO[tipo]["nome"]
        send_message(chat_id, f"🚀 Creazione torneo {nome}...")
        if trigger_github_action(tipo):
            log_torneo(user_id, username, tipo)
            send_message(chat_id, f"✅ Tournament {nome} avviato!")
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
