import discord
from discord.ext import commands
from decouple import config
import json
import random


client = commands.Bot(command_prefix='*')


@client.event
async def on_guild_join(guild):
    with open('Data/data.json', 'r') as f:
        guild_info = json.load(f)

    guild_info[guild.text_channels[0].id] = str(guild.text_channels[0])
    print(guild.text_channels[0])

    with open("Data/data.json", "w") as f:
        json.dump(guild_info, f)


@client.event
async def on_ready():
    print("Bot is ready")


@client.event
async def on_member_join(member):
    pass
client.run(config('TOKEN'))
print(client.guilds[0].text_channels[0].id)
