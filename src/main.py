import discord
from discord.ext import commands
from decouple import config
from utilities import load_json, str_to_bool
import json
import random
import os


intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix='*', intents=intents)




@client.event
async def on_ready():
    print("Bot is ready")
    await client.change_presence(activity=discord.Game(name=" *help"))


@client.event
async def on_guild_join(guild):
    if not os.path.isfile('config/data.json'):
        with open('config/data.json', 'w') as f:
            f.write('{}')

    guild_info = load_json('config/data.json')

    guild_info[str(guild.id)] = {
        'welcome': guild.text_channels[0].id, 'bye': guild.text_channels[0].id}
    with open("config/data.json", "w") as f:
        json.dump(guild_info, f)

    if not os.path.isfile('config/settings.json'):
        with open('config/settings.json', 'w') as f:
            f.write('{}')

    guildSettings = load_json('config/settings.json')
    guildSettings[str(guild.id)] = {'welcome': 'False', 'bye': 'False'}

    with open('config/settings.json', 'w') as file:
        json.dump(guildSettings, file)


@client.event
async def on_guild_remove(guild):
    guild = str(guild.id)

    data = load_json('config/data.json')

    del data[guild]

    with open('config/data.json', 'w') as f:
        json.dump(data, f)

    settings = load_json('config/settings.json')

    del settings[guild]
    with open('config/settings.json', 'w') as f:
        json.dump(data, f)


@client.event
async def on_member_join(member):
    settings = load_json('config/settings.json')
    enabled = str_to_bool(settings[str(member.guild.id)]['welcome'])
    if enabled:
        colour = discord.Color
        colours = [colour.teal(), colour.green(),
                   colour.orange(), colour.blue()]

        embed = discord.Embed(colour=random.choice(colours))
        embed.set_image(url=member.avatar_url)

        guildInfo = load_json('config/data.json')

        channel_id = guildInfo[str(member.guild.id)]['welcome']

        await client.get_channel(channel_id).send(f'Hey {member.mention}, Welcome to {member.guild.name}', embed=embed)


@client.event
async def on_member_remove(member):
    settings = load_json('config/settings.json')
    enabled = str_to_bool(settings[str(member.guild.id)]['bye'])
    if enabled:
        if member.id != client.user.id:
            guildInfo = load_json('config/data.json')

            channel_id = guildInfo[str(member.guild.id)]['bye']
            await client.get_channel(channel_id).send(f'{member.name} just left the server.')



client.load_extension('commands')
client.run(config('TOKEN'))
