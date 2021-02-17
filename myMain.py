import discord
from discord.ext.commands import Bot
import json
import logging
import os

f = open('config/main.json', 'r')
config = json.load(f)
TOKEN = config.get("bot_token")
prefix = '!'

logger = logging.getLogger()
logger.setLevel(logging.INFO)
consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.INFO)
formator = logging.Formatter(
    '[%(asctime)s] - [%(name)s] - %(levelname)s - %(message)s')
consoleHandler.setFormatter(formator)
if not os.path.exists('./logs'):
    os.mkdir('logs')
fileHandler = logging.FileHandler('logs/app.log')
fileHandler.setLevel(logging.DEBUG)
fileHandler.setFormatter(formator)
logger.addHandler(fileHandler)
logger.addHandler(consoleHandler)

bot = Bot(command_prefix=prefix)

extensions = ['nhentai_mod']


@bot.event
async def on_ready():
    channel = bot.guilds[0].channels[0]
    await channel.send('Now online!')
    print(' Bot is up!')


for e in extensions:
    bot.load_extension(e)
bot.run(TOKEN)
