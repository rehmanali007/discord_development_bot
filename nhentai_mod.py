import nhentai
import requests
import json
import os
import discord
import asyncio
from discord.ext.commands import command
from discord.ext.commands import Cog
from discord import Embed
from disputils import BotEmbedPaginator, BotConfirmation, BotMultipleChoice
from random import randint
from zipfile import ZipFile

MAX_UPLOAD_SIZE = 8000000


class Hentai(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.nhentai = nhentai
        f = open('config/nhentai.json', 'r')
        self.config = json.load(f)
        root_location = os.getcwd()
        self.dl_location = f'{root_location}/Downloads'
        print('NHentai extension has loaded!')

    @command(name='nhs.by.id', description='')
    async def search_by_id(self, ctx, *, id: int):
        await ctx.send('Searching ...')
        results = self.nhentai.get_doujin(id)
        if len(results.pages) != 0:
            x = 0
            embeds = []
            for page in results.pages:
                x += 1
                e = Embed(title=f"Page {x}", color=0x115599)
                e.add_field(name='Book ID', value=results.id, inline=False)
                e.add_field(name='Book Title',
                            value=results.titles['english'], inline=True)
                e.add_field(name='Link To Story',
                            value=results.url, inline=False)
                e.set_image(url=page.url)
                embeds.append(e)

            paginator = BotEmbedPaginator(ctx, embeds)
            await paginator.run()
        else:
            await ctx.send('No results found for the given id...\nPlease check if id is valid nhenati id.')

    @search_by_id.error
    async def error_handle(self, ctx, error):
        if isinstance(error, discord.ext.commands.UserInputError):
            await ctx.send('Book id is missing ...')
            print(error)

    @command(name='nhs', description='')
    async def search_by_keyword(self, ctx, *, query: str):
        if query in self.config.get("bannedKeywords"):
            await ctx.send('Sorry! This keyword is banned in our server for the TOS of discord.')
            return
        await ctx.send('Searching for query ...')
        results = self.nhentai.search(query)
        if results:
            x = 0
            embeds = []
            for res in results:
                for t in res.tags:
                    if t.name in self.config.get('bannedKeywords'):
                        continue
                x += 1
                e = Embed(title=f"Result {x}", color=0x115599)
                e.set_image(url=res.cover)
                e.add_field(name='Book Id', value=res.id, inline=False)
                e.add_field(name='Book Title',
                            value=res.titles['english'], inline=False)
                e.add_field(name='Book URL',
                            value=res.url, inline=False)
                embeds.append(e)
            if not embeds:
                await ctx.send('No results found for the given keyword...')
                return
            paginator = BotEmbedPaginator(ctx, embeds)
            await paginator.run()
        else:
            await ctx.send('No results found for the given keyword...')

    @command(name='dl_nh')
    async def download_nh(self, ctx, *, illustration_id: int):
        await ctx.send('Finding the illustration ..')
        results = self.nhentai.get_doujin(illustration_id)
        if len(results.pages) != 0:
            await ctx.send('Downloading the illustration ..')
            ill_dl_location = f'{self.dl_location}/{illustration_id}'
            if not os.path.exists(ill_dl_location):
                os.makedirs(ill_dl_location)
            zipped = f'{ill_dl_location}/{illustration_id}.zip'
            ziph = ZipFile(zipped, 'w')
            parts_enabled = False
            part = 1
            for res in results.pages:
                dl_file = f'{ill_dl_location}/{results.pages.index(res)}.png'
                await self.download_file(res.url, dl_file)
                if os.path.getsize(zipped) + os.path.getsize(dl_file) >= MAX_UPLOAD_SIZE:
                    print(f'Sending part {part}')
                    parts_enabled = True
                    ziph.close()
                    to_send = open(zipped, 'rb')
                    ill = discord.File(
                        to_send, filename=f'{illustration_id}_part{part}.zip')
                    part += 1
                    await ctx.send(file=ill)
                    os.remove(zipped)
                    ziph = ZipFile(zipped, 'w')

                ziph.write(dl_file)
                os.remove(dl_file)
            ziph.close()
            to_send = open(zipped, 'rb')
            if parts_enabled:
                filename = f'{illustration_id}_part{part}.zip'
            else:
                filename = f'{illustration_id}.zip'
            ill = discord.File(to_send, filename=filename)
            print('Created discord file!')
            await ctx.send(file=ill)
            print('Zip file sent!')
        else:
            await ctx.send('Could not find the illustration!')

    async def download_file(self, url, file_name):
        with open(file_name, "wb") as file:
            # get request
            response = requests.get(url)
            # write to file
            file.write(response.content)

    @command(name='test')
    async def test(self, ctx):
        send = discord.File(open('config/main.json', 'rb'))
        await ctx.send(file=send)

    @search_by_keyword.error
    @download_nh.error
    async def error_handle_query(self, ctx, error):
        if isinstance(error, discord.ext.commands.UserInputError):
            await ctx.send('Search query string is missing ...')
            print(error)


def setup(bot):
    bot.add_cog(Hentai(bot))


'''
export HTTP_PROXY="http://83.97.23.90:18080"
export HTTPS_PROXY="https://83.97.23.90:18080"

'''
