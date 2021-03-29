import discord
from discord.ext import commands
from decouple import config
import json
import random


intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix='*', intents=intents)


def load_data_json():
    with open('data.json', 'r') as f:
        guildInfo = json.load(f)

    return guildInfo


@client.event
async def on_ready():
    print("Bot is ready")


@client.event
async def on_guild_join(guild):
    with open('data.json', 'w') as f:
        f.write('{}')

    guild_info = load_data_json()

    guild_info[str(guild.id)] = {
        'welcome': guild.text_channels[0].id, 'bye': guild.text_channels[0].id}
    with open("data.json", "w") as f:
        json.dump(guild_info, f)


@client.event
async def on_guild_remove(guild):
    guild = str(guild.id)

    with open('data.json', 'r') as f:
        data = json.load(f)

    del data[guild]

    with open('data.json', 'w') as f:
        json.dump(data, f)


@client.command()
async def welcomeChannel(ctx, arg):

    guildInfo = load_data_json()

    if ctx.message.author.guild_permissions.administrator:

        guildInfo[str(ctx.message.guild.id)]['welcome'] = discord.utils.get(
            ctx.guild.channels, name=arg).id

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

    guildInfo = load_data_json()

    channel_id = guildInfo[str(member.guild.id)]['welcome']
    await client.get_channel(channel_id).send(f'Hey {member.mention}, Welcome to {member.guild.name}', embed=embed)


@client.command()
async def byeChannel(ctx, arg):
    guildInfo = load_data_json()

    if ctx.message.author.guild_permissions.administrator:

        guildInfo[str(ctx.message.guild.id)]['bye'] = discord.utils.get(
            ctx.guild.channels, name=arg).id

        with open("data.json", "w") as f:
            json.dump(guildInfo, f)

        await ctx.message.channel.send(
            f"Welcome Channel has been changed to `{arg}`")


@client.event
async def on_member_remove(member):
    if member.id != client.user.id:
        guildInfo = load_data_json()

        channel_id = guildInfo[str(member.guild.id)]['bye']
        await client.get_channel(channel_id).send(f'{member.name} just left the server.')

client.run(config('TOKEN'))
