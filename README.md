# Discord Honeypot Bot

This bot watches one or more channels and, if anyone posts there, it bans the user and can delete their recent message history.

## Setup

1. Create your Discord bot in the Developer Portal.
2. Leave **Privileged Gateway Intents** disabled. This bot does not read message content or member lists.
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

```bash
docker pull ghcr.io/ulnanlu/dc-honeypot:latest
docker run -d \
  --name dc-honeypot \
  --restart unless-stopped \
  --env-file .env \
  ghcr.io/ulnanlu/dc-honeypot:latest
```

```bash
cp compose.example.yaml compose.yaml
docker compose pull
docker compose up -d
```

## Environment variables

- `BOT_TOKEN`: your bot token
- `HONEYPOT_CHANNEL_IDS`: comma-separated channel IDs to monitor
- `BAN_REASON`: optional custom ban reason
- `LOG_CHANNEL_ID`: optional channel ID for bot logs
- `BAN_DELETE_MESSAGE_SECONDS`: optional number of seconds of recent message history to delete on ban (0 to 604800, default `86400`)

## Notes

- The bot only acts in guild text channels.
- The bot ignores other bots.
- If role hierarchy prevents a ban, the bot logs the failure (if `LOG_CHANNEL_ID` is set).
