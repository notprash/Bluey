from discord.ext import commands
import discord
import aiohttp
import random
import requests

class Fun(commands.Cog):
    def __init__(self, bot):
        self.client = bot

    @commands.command()
    async def meme(self, ctx, sub = 'memes'):
        res = requests.get("https://meme-api.herokuapp.com/gimme/")
        data = res.json()
        title = data['title']
        embed = discord.Embed(title=title)
        embed.set_image(url=data['url'])
        await ctx.send(embed=embed)



def setup(bot):
    bot.add_cog(Fun(bot))