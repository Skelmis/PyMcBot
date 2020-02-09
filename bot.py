import discord
from discord.ext import commands
import asyncio
import logging
import sys, traceback
from pathlib import Path
import os

import cogs._json

cwd = Path(__file__).parents[0]
cwd = str(cwd)

secret_file = cogs._json.read_json('token')
config_file = cogs._json.read_json('config')

def get_prefix(bot, message):
    return commands.when_mentioned_or("--")(bot, message)

bot = commands.Bot(command_prefix=get_prefix, case_insensitive=True)
bot.config_token = secret_file['token']

bot.server = config_file['server']
print(bot.server)
bot.channel = config_file['channel']
bot.username = config_file['username']
bot.password = config_file['password']

@bot.event
async def on_ready():
    print('------')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    await bot.change_presence(activity=discord.Game(name="https://github.com/Skelmis/PyMcBot"))

if __name__ == '__main__':
    for file in os.listdir(cwd+"/cogs"):
        if file.endswith(".py") and not file.startswith("_"):
            bot.load_extension(f"cogs.{file[:-3]}")
    bot.run(bot.config_token)
