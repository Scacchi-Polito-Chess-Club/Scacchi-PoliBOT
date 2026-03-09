# Scacchi PoliBOT

Bot per la gestione di tornei di scacchi su Lichess con notifiche Telegram.

## Funzionalità

- Creazione tornei Lichess (Bullet, Blitz, Chess960)
- Notifiche Telegram con link diretto al torneo
- Controllo minimo iscritti e annullamento automatico
- Trigger remoto via GitHub Actions o bot Telegram

## Installazione

```bash
pip install requests python-dotenv
```

## Configurazione

Crea un file `.env`:

```env
LICHESS_TOKEN=your_lichess_api_token
TELEGRAM_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_chat_id
TELEGRAM_TOPIC_ID=your_topic_id
TEAM_ID=your_lichess_team_id
```

## Utilizzo Locale

```bash
# Menu interattivo
python gestore_tornei.py

# Tramite argomento
python gestore_tornei.py --tipo 1   # 1+0 Bullet
python gestore_tornei.py --tipo 2   # 2+1 Bullet
python gestore_tornei.py --tipo 3   # 3+2 Chess960
```

## Utilizzo Remoto (da telefono)

### Opzione 1: GitHub Mobile

1. Imposta i secret in GitHub Settings > Secrets and variables > Actions:
   - `LICHESS_TOKEN`, `TELEGRAM_TOKEN`, `TELEGRAM_CHAT_ID`, `TELEGRAM_TOPIC_ID`, `TEAM_ID`

2. Apri GitHub Mobile > Repository > Actions > "Crea Torneo Lichess" > Run workflow

### Opzione 2: Bot Telegram

1. Crea un bot su @BotFather
2. Crea un GitHub Personal Access Token (repo scope)
3. Imposta i secret: `TELEGRAM_TOKEN`, `GH_TOKEN`, `GH_REPO`
4. Esegui `python bot_telegram.py` (richiede hosting, es. Render/Railway)

## Tipi di Turno

| Tipo | Cadenza | Variante | Min. Giocatori |
|------|---------|----------|-----------------|
| 1    | 1+0     | Standard | 10              |
| 2    | 2+1     | Standard | 10              |
| 3    | 3+2     | Chess960 | 10              |
