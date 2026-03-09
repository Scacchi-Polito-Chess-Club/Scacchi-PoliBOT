# AGENTS.md - Developer Guidelines

## Project Overview

Python project that creates Lichess tournaments via GitHub Actions and sends Telegram notifications.

## Technology Stack

- **Language**: Python 3
- **Dependencies**: `requests`
- **APIs**: Lichess API, Telegram Bot API, GitHub API

## Project Structure

```
Scacchi-PoliBOT/
├── .github/workflows/
│   └── crea_torneo.yml       # GitHub Action (contiene la logica)
├── bot_telegram.py            # Telegram bot per trigger remoto
├── AGENTS.md
└── README.md
```

## GitHub Actions

### Secrets (Settings > Secrets and variables > Actions)

- `LICHESS_TOKEN` - Lichess API token
- `TELEGRAM_TOKEN` - Bot Telegram token
- `TELEGRAM_CHAT_ID` - Chat ID
- `TELEGRAM_TOPIC_ID` - Topic ID
- `TEAM_ID` - Lichess team ID

### Workflow Trigger

- **GitHub Mobile**: Actions > "Crea Torneo Lichess" > Run workflow
- **API**: `repository_dispatch` event
- **Manual**: `workflow_dispatch`

### Tipi Turno

| Tipo | Cadenza | Variante |
|------|---------|----------|
| 1    | 1+0     | standard |
| 2    | 2+1     | standard |
| 3    | 3+2     | chess960 |

## Telegram Bot

### Environment Variables

```env
TELEGRAM_TOKEN=bot_token
GH_TOKEN=github_pat
GH_REPO=username/repo
```

### Comandi

- `/start` - Menu
- `/1`, `/2`, `/3` - Crea torneo

## Code Style

- Use `requests` library
- f-strings for formatting
- 4 spaces indentation
- Italian comments

## Adding New Tournament Type

Edit `.github/workflows/crea_torneo.yml`, aggiungi al dizionario TORNEO:

```yaml
'4': {'nome': 'Nome', 'tempo': 5, 'inc': 3, 'var': 'standard'}
```
