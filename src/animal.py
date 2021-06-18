from discord.embeds import Embed
from discord.ext import commands
import discord
from requests import get
import random


dkey = 'https://dog.ceo/api/breeds/image/random'
ckey = 'https://api.thecatapi.com/v1/images/search'


class Animal(commands.Cog):
    def __init__(self, bot):
        self.client = bot

    @commands.command()
    async def dog(self, ctx):
        data = get(dkey).json()
        dog = data['message']

        emb = discord.Embed(title = 'Dogs') # The embed
        emb.set_image(url = dog)

        await ctx.send(embed = emb)

    @commands.command()
    async def cat(self, ctx):
        data = get(ckey).json()
        cat = data[0]['url']
        emb = discord.Embed(title = 'Cats') # The embed
        emb.set_image(url = cat)
        await ctx.send(embed = emb)

def setup(bot):
    bot.add_cog(Animal(bot)) 

# data = get(ckey).json()
# breed_num = len(data[0]['breeds'])
# breed_name = ''
# for breed in range(breed_num):
#     breed_name += data[0]['breeds'][breed]['name']
# breed = breed_name
# print(breed_name)