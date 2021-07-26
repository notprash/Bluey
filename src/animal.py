# Imports
import discord
from discord.ext import commands
from discord.embeds import Embed
from requests import get

# Links for API Call
dkey = 'https://dog.ceo/api/breeds/image/random'  # Dog API
ckey = 'https://api.thecatapi.com/v1/images/search' # Cat API
pkey = 'https://some-random-api.ml/img/panda' #Panda API
rpkey = 'https://some-random-api.ml/img/red_panda' #Red Panda API


class Animal(commands.Cog):
    def __init__(self, bot):
        self.client = bot

#### Command for Dog pics

    @commands.command()
    async def dog(self, ctx):
        data = get(dkey).json()
        dog = data['message']
        emb = discord.Embed(title = 'Dogs', color = discord.Color.blue())
        emb.set_image(url = dog)
        await ctx.send(embed = emb)

#### Command for Cat pics

    @commands.command()
    async def cat(self, ctx):
        data = get(ckey).json()
        cat = data[0]['url']
        emb = discord.Embed(title = 'Cats', color = discord.Color.blue())
        emb.set_image(url = cat)
        await ctx.send(embed = emb)

#### Command for Panda pics

    @commands.command()
    async def panda(self, ctx):
        data = get(pkey).json()
        panda = data['link']
        emb = discord.Embed(title = 'Pandas', color = discord.Color.blue())
        emb.set_image(url = panda)
        await ctx.send(embed = emb)

    @commands.command()
    async def rpanda(self, ctx):
        data = get(rpkey).json()
        panda = data['link']
        emb = discord.Embed(title = 'Red Pandas', color = discord.Color.blue())
        emb.set_image(url = panda)
        await ctx.send(embed = emb)

def setup(bot):
    bot.add_cog(Animal(bot))
