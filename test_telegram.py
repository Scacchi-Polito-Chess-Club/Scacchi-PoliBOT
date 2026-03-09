import requests

# INSERISCI QUI IL TUO NUOVO TOKEN
TELEGRAM_TOKEN = 'REDACTED'
TELEGRAM_CHAT_ID = '-1001434145810' # 1163968938 (personale)
TELEGRAM_TOPIC_ID = '18204'

print("Inviando il messaggio di test...")

url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
dati = {
    "chat_id": TELEGRAM_CHAT_ID,
    "message_thread_id": TELEGRAM_TOPIC_ID,
    "text": "🤖 Ciao! Questo è un messaggio di test dal tuo script Python. Se lo leggi, funziona!"
}

risposta = requests.post(url, data=dati)

# Stampiamo la risposta del server per capire se è andata a buon fine
if risposta.status_code == 200:
    print("✅ Messaggio inviato con successo! Controlla il telefono.")
else:
    print(f"❌ Errore. Telegram ha risposto così:\n{risposta.text}")