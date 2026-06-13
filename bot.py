import os
from typing import Optional

import discord
from discord.ext import commands
from dotenv import load_dotenv


load_dotenv()


def get_int(name: str, default: Optional[int] = None) -> Optional[int]:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    return int(value)


def get_int_set(name: str) -> set[int]:
    value = os.getenv(name, "")
    if value.strip() == "":
        return set()

    result: set[int] = set()
    for part in value.split(","):
        token = part.strip()
        if token:
            result.add(int(token))
    return result


TOKEN = os.getenv("BOT_TOKEN")
HONEYPOT_CHANNEL_IDS = get_int_set("HONEYPOT_CHANNEL_IDS")
BAN_REASON = os.getenv(
    "BAN_REASON",
    "Auto-ban: user posted in restricted honeypot channel.",
)
LOG_CHANNEL_ID = get_int("LOG_CHANNEL_ID")
BAN_DELETE_MESSAGE_SECONDS = get_int("BAN_DELETE_MESSAGE_SECONDS", 86400)

if not TOKEN:
    raise RuntimeError("Missing BOT_TOKEN environment variable.")

if not HONEYPOT_CHANNEL_IDS:
    raise RuntimeError("Missing honeypot channels. Set HONEYPOT_CHANNEL_IDS.")

if BAN_DELETE_MESSAGE_SECONDS is None:
    BAN_DELETE_MESSAGE_SECONDS = 0

BAN_DELETE_MESSAGE_SECONDS = max(0, min(BAN_DELETE_MESSAGE_SECONDS, 604800))


intents = discord.Intents.default()
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)


async def send_log(guild: discord.Guild, text: str) -> None:
    if not LOG_CHANNEL_ID:
        return

    channel = guild.get_channel(LOG_CHANNEL_ID)
    if isinstance(channel, discord.TextChannel):
        try:
            await channel.send(text)
        except discord.HTTPException:
            pass


@bot.event
async def on_ready() -> None:
    print(f"Logged in as {bot.user} (ID: {bot.user.id if bot.user else 'unknown'})")


@bot.event
async def on_message(message: discord.Message) -> None:
    if message.author.bot:
        return

    if not isinstance(message.channel, discord.TextChannel):
        return

    if message.channel.id not in HONEYPOT_CHANNEL_IDS:
        return

    guild = message.guild
    if guild is None:
        return

    user = message.author

    try:
        await guild.ban(
            user,
            reason=BAN_REASON,
            delete_message_seconds=BAN_DELETE_MESSAGE_SECONDS,
        )
        await send_log(
            guild,
            f"Banned {user.mention} ({user.id}) for posting in <#{message.channel.id}>.",
        )
    except discord.Forbidden:
        await send_log(
            guild,
            f"Failed to ban {user.mention} ({user.id}) due to missing permissions.",
        )
    except discord.HTTPException:
        await send_log(guild, f"Discord API error while banning user {user.id}.")


bot.run(TOKEN)
