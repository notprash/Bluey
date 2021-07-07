import discord
from discord.ext import commands
from decouple import config
from utilities import read_database
from PIL import Image, ImageDraw, ImageOps, ImageFont
from discord_slash import SlashCommand
import sqlite3
import os

def get_prefix(client, msg):
    # get prefix
    prefix = read_database(msg.guild.id)[8]

    return prefix

intents = discord.Intents.all()

client = commands.Bot(command_prefix=get_prefix, intents=intents)
slash = SlashCommand(client, sync_commands=True)


@slash.slash(name="poll", description='Creates a poll')
async def poll(ctx, question, choice_a, choice_b, choice_c="", choice_d="", choice_e="", choice_f="", choice_g=""):
    # Emoji List
    emojis = ["\N{REGIONAL INDICATOR SYMBOL LETTER A}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER B}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER C}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER D}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER E}", 
            "\N{REGIONAL INDICATOR SYMBOL LETTER F}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER G}"]

    choices_list = [choice_a, choice_b, choice_c , choice_d, choice_e, choice_f, choice_g]
    emoji_count = 0 
    final_str = ""
    for i in range(len(choices_list)):
        if choices_list[i] != "":
            final_str += f"{emojis[i]} {choices_list[i]}\n"
            emoji_count += 1
    # Create Embed
    embed = discord.Embed(description=final_str, color=ctx.author.color).set_author(name=ctx.author, icon_url=ctx.author.avatar_url)


    msg = await ctx.send(f"**{question}**", embed=embed)

    # Add Reactions
    for emoji in emojis[:emoji_count]:
        await msg.add_reaction(emoji)




@client.event
async def on_ready():
    print("Bot is ready")

    # Changes Bot Status
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=" !help"))


@client.event
async def on_guild_join(guild):

    # Create table and field
    with sqlite3.connect('db.sqlite3') as db:
        command = "CREATE TABLE Settings (GuildId int, welcomeChannel int, userLeaveChannel int, welcomeMsg int, userLeavemsg int, warncount int, levelup int, milestone int, prefix TEXT)"
        try:
            db.execute(command)
            db.commit()
        except Exception:
            print("Table Exists")
        

    # Creates Basic Data Structure
    guildData = {"GuildId": guild.id, "welcomeChannel": guild.text_channels[0].id,
            "userLeaveChannel": guild.text_channels[0].id, "welcomeMsg": False, "userLeaveMsg": False, "warncount": 6, "levelup": 0, 'milestone': 0, 'prefix': "!"}

    # Create DataBase
    with sqlite3.connect('db.sqlite3') as db:
        command = "INSERT INTO Settings VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)"
        db.execute(command, tuple(guildData.values()))
        db.commit()


@client.event
async def on_guild_remove(guild):

    # Deletes server data from the bot when the bot removed from the server 
    with sqlite3.connect("db.sqlite3") as db: 
        command = f"DELETE FROM Settings WHERE GuildId = {guild.id}" 
        db.execute(command)
        db.commit()

def get_colors(image_file, numcolors=10, resize=150):
    # Resize image to speed up processing
    img = Image.open(image_file)
    img = img.copy()
    img.thumbnail((resize, resize))

    # Reduce to palette
    paletted = img.convert('P', palette=Image.ADAPTIVE, colors=numcolors)

    # Find dominant colors
    palette = paletted.getpalette()
    color_counts = sorted(paletted.getcolors(), reverse=True)
    colors = list()
    for i in range(numcolors):
        palette_index = color_counts[i][1]
        dominant_color = palette[palette_index*3:palette_index*3+3]
        colors.append(tuple(dominant_color))

    return colors


@client.event
async def on_member_join(member):
    settings = read_database(member.guild.id)
    username = f"{member.name}# {member.discriminator}"

    # Checks if welcome msg is enabled
    enabled = bool(settings[3])

    if enabled:

        await member.avatar_url.save("avatar.png")


        W, H = (593, 316)
        size = (216, 192)
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask) 
        draw.ellipse((0, 0) + size, fill=255)

        im = Image.open('avatar.png').convert("RGBA")

        output = ImageOps.fit(im, mask.size, centering=(0.5, 0.5))
        output.putalpha(mask)

        output.save('output.png')
        im = Image.open("output.png").convert("RGBA")
        colors = get_colors("output.png")


        background = Image.new("RGBA", (W, H), '#535353')
        background.paste(im, (200, 30), im)

        font = ImageFont.truetype('Roboto.ttf', 24)
        draw = ImageDraw.Draw(background)
        half = Image.new("RGBA", (593, 10), colors[0])
        background.paste(half, (0, 306))
        msg = f"{username} just landed"
        w, h = draw.textsize(msg, font=font)
        draw.text(((W-w)/2, 250), msg, fill=(255, 255, 255), font=font)
        background.save('foo.png')

        # Gets welcome msg channel
        channel_id = settings[1]

        # Get Welcome Card
        welcome_card = discord.File('foo.png')

        # Sends welcome msg
        await client.get_channel(channel_id).send(f"Hey {member.mention}, Welcome to the {member.guild.name}", file=welcome_card)

        # Remove the files
        os.remove('foo.png')
        os.remove('output.png')
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


client.load_extension('admin')
client.load_extension('music')
client.load_extension('moderation')
client.load_extension('fun')
client.load_extension("levels")
client.load_extension("animal")
client.load_extension("notifier")
client.load_extension('kitsu')
client.run(config('TOKEN'))
