import discord
from discord.ext import commands
from decouple import config
from utilities import read_database
from PIL import Image, ImageDraw, ImageOps, ImageFont
import sqlite3
import os


intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix='*', intents=intents)


track_msg = {}


@client.event
async def on_ready():
    print("Bot is ready")

    # Changes Bot Status
    await client.change_presence(activity=discord.Game(name=" *help"))


@client.event
async def on_guild_join(guild):
    # Creates Basic Data Structure
    guildData = {"GuildId": guild.id, "welcomeChannel": guild.text_channels[0].id,
                 "userLeaveChannel": guild.text_channels[0].id, "welcomeMsg": False, "userLeaveMsg": False}

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

        await member.avatar_url.save("avatar.png")

        # Create the circular image
        img = Image.open('avatar.png')

        size = (256, 256)
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + size, fill=255)

        circle = ImageOps.fit(img, mask.size, centering=(0.5, 0.5))
        circle.putalpha(mask)

        # Create Background
        background = Image.new("RGB", (700, 400), (0, 0, 0))

        # Paste the circular image on the background
        background.paste(circle, (220, 0), circle)

        # Add Text to Image
        font = ImageFont.truetype('Roboto-Regular.ttf', 30)
        draw = ImageDraw.Draw(background)
        draw.text((120, 300), f"{member.name}#{member.discriminator} just joined the server",
                  (128, 128, 128), font=font)
        background.save('foo.png')

        # Gets welcome msg channel
        channel_id = settings[1]

        # Get Welcome Card
        welcome_card = discord.File('foo.png')

        # Sends welcome msg
        await client.get_channel(channel_id).send(file=welcome_card)

        # Remvoe the files
        os.remove('foo.png')
        os.remove('avatar.png')


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
