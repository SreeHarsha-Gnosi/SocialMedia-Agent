# Social Agent

Claude-powered Streamlit app: feed it PDFs, images, CSV/Excel, Word, text files, web pages or YouTube
links and get Instagram carousel slides plus Telegram and WhatsApp messages to publish or schedule.

## Run
```
uv sync
cp .env.example .env   # optional; keys can also be pasted in the sidebar
uv run streamlit run main.py
```

## Features
- Multi-format input incl. web pages and YouTube transcripts
- 3 caption variants; per-slide / caption / message "rewrite with an instruction"
- History (SQLite in `data/`): reopen, repost, or generate a follow-up/reminder with new info
- Scheduling: a background thread publishes due posts while the app runs
- One-click publish to Telegram and WhatsApp; ZIP download for Instagram

## Layout (`src/socialagent`)
- `core/` models + settings/credentials
- `ingestion/` files and links -> `Attachment`
- `agent/` prompts, JSON schemas, Claude generator
- `rendering/` themes + Pillow slide renderer + ZIP export
- `publishers/` `Publisher` interface; Telegram and WhatsApp
- `storage/` SQLite history + schedule repositories
- `scheduling/` background publisher thread
- `ui/` Streamlit pages/components
