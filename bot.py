import os
from pathlib import Path

import discord
from discord.ext import commands

from utils.json_loader import read_json

cwd = Path(__file__).parents[0]
cwd = str(cwd)

secret_file = read_json("token")
config_file = read_json("config")


def get_prefix(bot, message):
    return commands.when_mentioned_or(bot.PREFIX)(bot, message)


bot = commands.Bot(
    command_prefix=get_prefix,
    case_insensitive=True,
    help_command=None,
    intents=discord.Intents.all(),
)
bot.config_token = secret_file["token"]

bot.PREFIX = "--"

bot.player = None
bot.server = config_file["server"]
bot.channel = config_file["channel"]
bot.username = config_file["username"]
bot.password = config_file["password"]


@bot.event
async def on_ready():
    print("------")
    print(bot.user.name)
    print(bot.user.id)
    print("------")
    await bot.change_presence(
        activity=discord.Game(name="https://github.com/Skelmis/PyMcBot")
    )


if __name__ == "__main__":
    for file in os.listdir(cwd + "/cogs"):
        if file.endswith(".py") and not file.startswith("_"):
            bot.load_extension(f"cogs.{file[:-3]}")
    bot.run(bot.config_token)
