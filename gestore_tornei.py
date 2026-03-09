import requests
import time
from datetime import datetime, timedelta

import os
from dotenv import load_dotenv

# carica le variabili nascoste dal file .env
load_dotenv()

LICHESS_TOKEN = os.getenv('LICHESS_TOKEN')
TEAM_ID = os.getenv('TEAM_ID')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
TELEGRAM_TOPIC_ID = os.getenv('TELEGRAM_TOPIC_ID')

HEADERS_LICHESS = {'Authorization': f'Bearer {LICHESS_TOKEN}'}


# ==========================================
# API (TELEGRAM E LICHESS)
# ==========================================
def invia_telegram(messaggio):

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    dati = {
        "chat_id": TELEGRAM_CHAT_ID,
        "message_thread_id": TELEGRAM_TOPIC_ID,
        "text": messaggio,
        "parse_mode": "HTML",
        "disable_web_page_preview": True  # evita che Telegram crei un'anteprima gigante del link
    }
    risposta = requests.post(url, data=dati)
    if risposta.status_code != 200:
        print(f"⚠️ Impossibile inviare messaggio Telegram: {risposta.text}")


def crea_torneo_lichess(nome, tempo, incremento, variante, min_attesa):
    orario_inizio = datetime.now() + timedelta(minutes=min_attesa)
    timestamp_inizio = int(orario_inizio.timestamp() * 1000)

    dati = {
        'name': nome,
        'clockTime': tempo,
        'clockIncrement': incremento,
        'variant': variante,
        'minutes': 60,  # durata totale del torneo impostata a 60 minuti
        'conditions.teamMember.teamId': TEAM_ID,
        'startDate': timestamp_inizio
    }
    risposta = requests.post('https://lichess.org/api/tournament', headers=HEADERS_LICHESS, data=dati)

    if risposta.status_code == 200:
        torneo = risposta.json()
        link = f"https://lichess.org/tournament/{torneo['id']}"
        print(f"\n✅ Torneo creato: {link}")

        testo_tg = (f"🏆 <b>NUOVO TORNEO CREATO!</b> 🏆\n\n"
                    f"♟️ <b>Nome:</b> {nome}\n"
                    f"⏱️ <b>Cadenza:</b> {tempo}+{incremento}\n"
                    f"⏳ Inizia tra {min_attesa} minuti!\n"
                    f"👉 Partecipa! {link}")
        invia_telegram(testo_tg)
        return torneo['id']
    else:
        print(f"\n❌ Errore nella creazione su Lichess: {risposta.text}")
        return None


def controlla_iscritti(id_torneo, min_giocatori):
    print(f"\n🔍 Controllo iscritti (Minimo richiesto: {min_giocatori})...")
    risposta = requests.get(f'https://lichess.org/api/tournament/{id_torneo}')

    if risposta.status_code == 200:
        iscritti = risposta.json().get('nbPlayers', 0)
        print(f"👤 Giocatori attuali: {iscritti}")

        if iscritti < min_giocatori:
            print("⚠️ Pochi iscritti. Annullamento in corso...")
            req_annulla = requests.post(f'https://lichess.org/api/tournament/{id_torneo}/terminate',
                                        headers=HEADERS_LICHESS)
            if req_annulla.status_code == 200:
                print("🚫 Torneo annullato.")
                invia_telegram("🚫 Il torneo di stasera è stato annullato per mancanza di giocatori sufficienti.")
            else:
                print(f"❌ Errore durante l'annullamento: {req_annulla.text}")
        else:
            print("✅ Iscritti sufficienti. Il torneo sta per iniziare!")
            invia_telegram("✅ Il torneo ha raggiunto il numero minimo e sta per iniziare! Buona partita a tutti.")
    else:
        print("❌ Impossibile recuperare i dati degli iscritti da Lichess.")


# ==========================================
# MENU INTERATTIVO E MAIN
# ==========================================
if __name__ == "__main__":
    print("=== GESTORE TORNEI LICHESS ===")
    print("1) 1+0 Bullet Arena - Minimo 10 giocatori")
    print("2) 2+1 Bullet Arena - Minimo 10 giocatori")
    print("3) 3+2 Chess960 Arena - Minimo 10 giocatori")

    scelta = input("\nDigita il numero del torneo da avviare e premi Invio: ")

    # Dizionario con i parametri per ogni scelta
    if scelta == '1':
        p = {"nome": "Scacchi PoliTO - 1+0 Bullet", "tempo": 1, "inc": 0, "var": "standard", "attesa": 60, "min_g": 10, "ctrl": 5}
    elif scelta == '2':
        p = {"nome": "Scacchi PoliTO - 2+1 Bullet", "tempo": 2, "inc": 1, "var": "standard", "attesa": 60, "min_g": 10, "ctrl": 5}
    elif scelta == '3':
        p = {"nome": "Scacchi PoliTO - 3+2 Chess960", "tempo": 3, "inc": 2, "var": "chess960", "attesa": 60, "min_g": 10, "ctrl": 5}
    else:
        print("Scelta non valida. Chiusura del programma.")
        exit()

    print(f"\nAvvio procedura per: {p['nome']}")
    id_torneo = crea_torneo_lichess(p['nome'], p['tempo'], p['inc'], p['var'], p['attesa'])

    if id_torneo:
        # calcola quanto tempo attendere prima di fare il controllo finale
        minuti_pausa = p['attesa'] - p['ctrl']
        if minuti_pausa > 0:
            print(f"⏱️ Il programma va in pausa per {minuti_pausa} minuti...")
            time.sleep(minuti_pausa * 60)

        controlla_iscritti(id_torneo, p['min_g'])