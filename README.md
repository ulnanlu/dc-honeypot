# Discord Honeypot Bot

This bot watches one or more channels and, if anyone posts there, it bans the user and can delete their recent message history.

## Setup

1. Create your Discord bot in the Developer Portal.
2. Enable **Privileged Gateway Intents**:
   - `MESSAGE CONTENT INTENT`
   - `SERVER MEMBERS INTENT`
3. Invite the bot with these permissions:
   - `View Channels`
   - `Read Message History`
   - `Manage Messages`
   - `Ban Members`
4. Copy `.env.example` to `.env` and fill in values.

## Install and run

```bash
uv sync
uv run python bot.py
```

## Docker

Build and run locally:

```bash
docker build -t dc-honeypot .
docker run --env-file .env dc-honeypot
```

GitHub Actions runs Docker builds on pull requests, and pushes `linux/amd64` images to GHCR for `main` branch pushes and version tags (`v*`) via `.github/workflows/docker-build.yml`.

Example production Compose setup (pull from GHCR):

```bash
cp compose.example.yaml compose.yaml
GHCR_REPOSITORY=<owner>/<repo> IMAGE_TAG=latest docker compose up -d
```

## Environment variables

- `BOT_TOKEN`: your bot token
- `HONEYPOT_CHANNEL_ID`: single channel ID to monitor (backward compatible)
- `HONEYPOT_CHANNEL_IDS`: comma-separated channel IDs to monitor (recommended for multiple channels)
- `BAN_REASON`: optional custom ban reason
- `LOG_CHANNEL_ID`: optional channel ID for bot logs
- `BAN_DELETE_MESSAGE_SECONDS`: optional number of seconds of recent message history to delete on ban (0 to 604800, default `86400`)

## Notes

- The bot only acts in guild text channels.
- The bot ignores other bots.
- If role hierarchy prevents a ban, the bot logs the failure (if `LOG_CHANNEL_ID` is set).
