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


TOKEN = os.getenv("BOT_TOKEN")
HONEYPOT_CHANNEL_ID = get_int("HONEYPOT_CHANNEL_ID")
BAN_REASON = os.getenv(
    "BAN_REASON",
    "Auto-ban: user posted in restricted honeypot channel.",
)
LOG_CHANNEL_ID = get_int("LOG_CHANNEL_ID")
BAN_DELETE_MESSAGE_SECONDS = get_int("BAN_DELETE_MESSAGE_SECONDS", 86400)

if not TOKEN:
    raise RuntimeError("Missing BOT_TOKEN environment variable.")

if not HONEYPOT_CHANNEL_ID:
    raise RuntimeError("Missing HONEYPOT_CHANNEL_ID environment variable.")

if BAN_DELETE_MESSAGE_SECONDS is None:
    BAN_DELETE_MESSAGE_SECONDS = 0

BAN_DELETE_MESSAGE_SECONDS = max(0, min(BAN_DELETE_MESSAGE_SECONDS, 604800))


intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.messages = True
intents.message_content = True

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

    if message.channel.id != HONEYPOT_CHANNEL_ID:
        return

    member = message.author
    guild = message.guild
    if guild is None or not isinstance(member, discord.Member):
        return

    try:
        await guild.ban(
            member,
            reason=BAN_REASON,
            delete_message_seconds=BAN_DELETE_MESSAGE_SECONDS,
        )
        await send_log(
            guild,
            f"Banned {member.mention} ({member.id}) for posting in <#{HONEYPOT_CHANNEL_ID}>.",
        )
    except discord.Forbidden:
        await send_log(
            guild,
            f"Failed to ban {member.mention} ({member.id}) due to missing permissions.",
        )
    except discord.HTTPException:
        await send_log(guild, f"Discord API error while banning user {member.id}.")


bot.run(TOKEN)
