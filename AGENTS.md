# AGENTS.md - Developer Guidelines

## Project Overview

This is a Python project that manages chess tournaments on Lichess and sends notifications via Telegram. It creates tournaments, monitors registrations, and sends notifications to users.

## Technology Stack

- **Language**: Python 3
- **Dependencies**: `requests`, `python-dotenv`
- **APIs**: Lichess API, Telegram Bot API

## Build & Run Commands

### Installation

```bash
pip install requests python-dotenv
```

### Running the Application

```bash
python gestore_tornei.py
```

This launches an interactive menu to create tournaments:
1. 1+0 Bullet Arena (10 min players)
2. 2+1 Bullet Arena (10 min players)
3. 3+2 Chess960 Arena (10 min players)

### Environment Variables

Create a `.env` file in the project root:

```env
LICHESS_TOKEN=your_lichess_api_token
TEAM_ID=your_team_id
TELEGRAM_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_chat_id
TELEGRAM_TOPIC_ID=your_topic_id
```

### Running Tests

This project does not have a formal test framework. Tests are currently manual:

```bash
python test_telegram.py
```

To run a specific test function, use pytest (if added):

```bash
pytest test_file.py::test_function_name
```

To add pytest:

```bash
pip install pytest
pytest  # runs all tests
```

## Code Style Guidelines

### General Principles

- Keep functions small and focused (single responsibility)
- Use descriptive names for functions and variables
- Handle errors gracefully with appropriate error messages

### Naming Conventions

- **Functions/variables**: `snake_case` (e.g., `invia_telegram`, `controlla_iscritti`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `LICHESS_TOKEN`, `HEADERS_LICHESS`)
- **Files**: `snake_case.py` (e.g., `gestore_tornei.py`)

### Imports

```python
# Standard library first
import os
import time
from datetime import datetime, timedelta

# Third-party libraries
import requests
from dotenv import load_dotenv
```

Order: standard library → third-party → local

### Formatting

- Use f-strings for string formatting: `f"text {variable}"`
- Use 4 spaces for indentation (no tabs)
- Maximum line length: 120 characters
- Add spaces around operators: `minuti_pausa = p['attesa'] - p['ctrl']`
- Use blank lines to separate logical sections (max 2 consecutive)

### Type Hints

Type hints are encouraged but not required. When used:

```python
def invia_telegram(messaggio: str) -> None:
    ...

def crea_torneo_lichess(nome: str, tempo: int, incremento: int, variante: str, min_attesa: int) -> str | None:
    ...
```

### Error Handling

- Check HTTP response status codes
- Print descriptive error messages in Italian
- Return `None` on failure instead of raising exceptions (for this project)

```python
if risposta.status_code != 200:
    print(f"⚠️ Impossibile inviare messaggio Telegram: {risposta.text}")
```

### Comments

- Use Italian comments (project convention)
- Comment sections with separators:

```python
# ==========================================
# API (TELEGRAM E LICHESS)
# ==========================================
```

- Add inline comments for non-obvious logic:

```python
disable_web_page_preview = True  # evita che Telegram crei un'anteprima gigante del link
```

### API Conventions

- Use uppercase headers dictionary names: `HEADERS_LICHESS`
- Pass headers as keyword arguments: `requests.post(url, headers=HEADERS_LICHESS, data=dati)`
- Use `requests` library (not `httpx` or `aiohttp`)

### Configuration

- Store configuration in dictionary for menu options:

```python
p = {"nome": "Scacchi PoliTO - 1+0 Bullet", "tempo": 1, "inc": 0, "var": "standard", "attesa": 60, "min_g": 10, "ctrl": 5}
```

- Use environment variables for secrets (never hardcode tokens)

## Project Structure

```
Scacchi-PoliBOT/
├── .gitignore                    # Git ignore rules
├── gestore_tornei.py             # Main tournament management script (CLI: --tipo 1|2|3)
├── bot_telegram.py               # Telegram bot to trigger tournaments via GitHub Actions
├── test_telegram.py              # Simple Telegram API test
├── .github/
│   └── workflows/
│       └── crea_torneo.yml       # GitHub Action workflow
└── .env                          # Environment variables (not committed)
```

## GitHub Actions (Cloud)

### Trigger via CLI

```bash
python gestore_tornei.py --tipo 1   # 1+0 Bullet
python gestore_tornei.py --tipo 2   # 2+1 Bullet
python gestore_tornei.py --tipo 3   # 3+2 Chess960
```

### GitHub Secrets

Imposta in GitHub Settings > Secrets and variables > Actions:

- `LICHESS_TOKEN` - Lichess API token
- `TEAM_ID` - Team ID su Lichess
- `TELEGRAM_TOKEN` - Bot Telegram token
- `TELEGRAM_CHAT_ID` - Chat ID
- `TELEGRAM_TOPIC_ID` - Topic ID

### Trigger via GitHub API

```bash
curl -X POST https://api.github.com/repos/USERNAME/Scacchi-PoliBOT/dispatches \
  -H "Authorization: token GH_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  -d '{"event_type": "crea_torneo", "client_payload": {"tipo": "1"}}'
```

### Trigger Manually (da telefono)

1. Apri GitHub Mobile/App
2. Vai su Scacchi-PoliBOT > Actions
3. Clicca "Crea Torneo Lichess" > "Run workflow"
4. Seleziona tipo e clicca "Run workflow"

## Telegram Bot

### Setup

1. Crea un bot su @BotFather
2. Crea un GitHub Personal Access Token (repo scope)
3. Imposta le variabili d'ambiente:

```env
TELEGRAM_TOKEN=your_bot_token
GH_TOKEN=your_github_pat
GH_REPO=username/Scacchi-PoliBOT
```

### Esecuzione

```bash
python bot_telegram.py
```

### Comandi

- `/start` - Menu interattivo
- `/1` - Crea 1+0 Bullet
- `/2` - Crea 2+1 Bullet
- `/3` - Crea 3+2 Chess960

### Hosting (gratuito)

Il bot puo' girare su:
- **Render/Railway** (free tier)
- **Raspberry Pi** a casa
- **GitHub Codespaces** (temporaneo)

## Common Tasks

### Creating a New Tournament Type

Add a new option in the menu (around line 99-113) and corresponding dictionary entry:

```python
# In menu
print("4) 5+3 Standard Arena - Minimo 8 giocatori")

# In dictionary
elif scelta == '4':
    p = {"nome": "Scacchi PoliTO - 5+3 Standard", "tempo": 5, "inc": 3, "var": "standard", "attesa": 60, "min_g": 8, "ctrl": 5}
```

### Adding a New Notification

Create a new function or reuse `invia_telegram()`:

```python
def invia_risultati(risultati: dict) -> None:
    messaggio = formatta_messaggio_risultati(risultati)
    invia_telegram(messaggio)
```
