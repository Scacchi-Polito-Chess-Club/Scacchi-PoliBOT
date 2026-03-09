# Scacchi PoliBOT

Bot per la gestione di tornei di scacchi su Lichess con notifiche Telegram.

## Funzionalità

- Creazione tornei Lichess (Bullet, Blitz, Chess960) via GitHub Actions
- Notifiche Telegram con link diretto al torneo
- Trigger remoto da telefono

## Configurazione GitHub

Imposta i secret in **GitHub Settings > Secrets and variables > Actions**:

- `LICHESS_TOKEN` - API token Lichess
- `TELEGRAM_TOKEN` - Token bot Telegram
- `TELEGRAM_CHAT_ID` - Chat ID
- `TELEGRAM_TOPIC_ID` - Topic ID
- `TEAM_ID` - Team ID Lichess

## Utilizzo

### Da GitHub Mobile/App

1. Apri GitHub Mobile > Repository > Actions
2. Clicca "Crea Torneo Lichess" > "Run workflow"
3. Seleziona tipo (1, 2, 3) e avvia

### Da Bot Telegram

1. Crea bot su @BotFather
2. Crea GitHub PAT (repo scope)
3. Esegui `python bot_telegram.py` (richiede hosting)

## Tipi di Turno

| Tipo | Cadenza | Variante |
|------|---------|----------|
| 1    | 1+0     | Standard |
| 2    | 2+1     | Standard |
| 3    | 3+2     | Chess960 |
