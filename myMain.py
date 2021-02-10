import discord
from discord.ext.commands import Bot
import json

f = open('config/main.json', 'r')
config = json.load(f)

prefix = '!'

bot = Bot(command_prefix=prefix)

extensions = ['nhentai_mod']


@bot.event
async def on_ready():
    channel = bot.guilds[0].channels[0]
    await channel.send('Now online!')
    print(' Bot is up!')


for e in extensions:
    bot.load_extension(e)
bot.run('NzEyMjE1Nzk4OTY1NjAwMzc3.XsOUpg.5UEFCqDS9rQAJ9NJF-PgKUHkUgw')
