import discord
from discord.ext import commands
from decouple import config


client = discord.Client()


@client.event
async def on_ready():
    print("Bot is ready")


client.run(config('TOKEN'))
