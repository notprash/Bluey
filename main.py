import discord
from discord.ext import commands
from decouple import config
import json
import random


intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix='*', intents=intents)


@client.event
async def on_ready():
    print("Bot is ready")


@client.event
async def on_guild_join(guild):
    with open('data.json', 'w') as f:
        f.write('{}')
    with open('data.json', 'r') as f:
        guild_info = json.load(f)

    guild_info[str(guild.id)] = (guild.text_channels[0].id)
    with open("data.json", "w") as f:
        json.dump(guild_info, f)


@client.command()
async def changewelcomechannel(ctx, arg):
    with open("data.json", "r") as f:
        guildInfo = json.load(f)

    guildInfo[str(ctx.message.guild.id)] = ctx.message.channel.id

    with open("data.json", "w") as f:
        json.dump(guildInfo, f)

    await ctx.message.channel.send(
        f"Welcome Channel has been changed to `{arg}`")


@client.event
async def on_member_join(member):
    colour = discord.Color
    colours = [colour.teal(), colour.green(),
               colour.orange(), colour.blue()]

    embed = discord.Embed(
        title=f"Info", colour=random.choice(colours))
    embed.add_field(name="Name", value=member.name, inline=True)
    embed.add_field(name="Status", value=member.status, inline=True)
    embed.add_field(name="Roles", value=member.top_role, inline=False)
    embed.set_thumbnail(url=member.avatar_url)

    with open('data.json', 'r') as f:
        guildInfo = json.load(f)

    channel_id = guildInfo[str(member.guild.id)]
    await client.get_channel(channel_id).send(f'Hey {member.mention}, Welcome to {member.guild.name}', embed=embed)
client.run(config('TOKEN'))
