import discord
from discord.ext import commands
from decouple import config
from utilities import read_database
import random
import os
import sqlite3


intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix='*', intents=intents)

@client.event
async def on_ready():
    print("Bot is ready")

    # Changes Bot Status
    await client.change_presence(activity=discord.Game(name=" *help"))


@client.event
async def on_guild_join(guild):
    # Creates Basic Data Structure 
    guildData = {"GuildId": guild.id, "welcomeChannel": guild.text_channels[0].id, "userLeaveChannel": guild.text_channels[0].id, "welcomeMsg": False, "userLeaveMsg": False}

    # Create DataBase 
    with sqlite3.connect('db.sqlite3') as db:
        command = "INSERT INTO Settings VALUES(?, ?, ?, ?, ?)"
        db.execute(command, tuple(guildData.values()))
        db.commit()




@client.event
async def on_guild_remove(guild):
    data = read_database(guild.id)[0]

    # Deletes server data from the bot when the bot removed from the server
    with sqlite3.connect("db.sqlite3") as db:
        command = f"DELETE FROM Settings WHERE GuildId = {guild.id}"
        db.execute(command)
        db.commit()


@client.event
async def on_member_join(member):
    settings = read_database(member.guild.id)

    # Checks if welcome msg is enabled
    enabled = bool(settings[3])


    if enabled:
        colour = discord.Color
        colours = [colour.teal(), colour.green(),
                   colour.orange(), colour.blue()]

        embed = discord.Embed(colour=random.choice(colours))
        embed.set_image(url=member.avatar_url)

        # Gets welcome msg channel
        channel_id = settings[1]

        # Sends welcome msg
        await client.get_channel(channel_id).send(f'Hey {member.mention}, Welcome to {member.guild.name}', embed=embed)


@client.event
async def on_member_remove(member):
    settings = read_database(member.guild.id)
    enabled = bool(settings[4])
    if enabled:
        # Gets user leave msg channel
        channel_id = settings[2]

        # Sends user leave msg
        await client.get_channel(channel_id).send(f'{member.name} just left the server.')



client.load_extension('commands')
client.run(config('TOKEN'))
