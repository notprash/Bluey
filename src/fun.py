# Imports
import discord
from discord.ext import commands
import aiohttp
import random
from requests import get
from bs4 import BeautifulSoup

key = 'https://meme-api.herokuapp.com/gimme/'

class Fun(commands.Cog):
    def __init__(self, bot):
        self.client = bot

#### Command for Memes

    @commands.command()
    async def meme(self, ctx, sub = 'memes'):
        data = get(key).json()
        title = data['title']
        embed = discord.Embed(title=title)
        embed.set_image(url=data['url'])
        await ctx.send(embed=embed)

#### Command for Wallpapers

    @commands.command()
    async def w(self, ctx, *query):
        query = ' '.join(query)
        site = get(f'https://www.wallpaperflare.com/search?wallpaper={query}').text
        soup = BeautifulSoup(site, 'lxml')
        link = soup.find_all('a')

        wallpaper = []
        for i in link:
            if i.get('itemprop') == 'url':
                wallpaper.append(i)
        wallpaper.pop(0)
        
        random_wall = random.choice(wallpaper)
        image = random_wall.contents[1].get('data-src') 
        
        emb = discord.Embed(title = query) 
        emb.set_image(url = image)
        await ctx.send(embed = emb)

def setup(bot):
    bot.add_cog(Fun(bot))
