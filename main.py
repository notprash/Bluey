import discord
from discord.ext import commands
from decouple import config
import json
import random


intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix='*', intents=intents)


def load_json(file):
    with open(file, 'r') as f:
        guildInfo = json.load(f)

    return guildInfo


@client.event
async def on_ready():
    print("Bot is ready")
    await client.change_presence(activity=discord.Game(name=" *help"))


@client.event
async def on_guild_join(guild):
    with open('data.json', 'w') as f:
        f.write('{}')

    guild_info = load_json('data.json')

    guild_info[str(guild.id)] = {
        'welcome': guild.text_channels[0].id, 'bye': guild.text_channels[0].id}
    with open("data.json", "w") as f:
        json.dump(guild_info, f)

    guildSettings = load_json('settings.json')
    guildSettings[str(guild.id)] = {'welcome': 'False', 'bye': 'False'}

    with open('settings.json', 'w') as file:
        json.dump(guildSettings, file)


@client.event
async def on_guild_remove(guild):
    guild = str(guild.id)

    data = load_json('data.json')

    del data[guild]

    with open('data.json', 'w') as f:
        json.dump(data, f)

    settings = load_json('settings.json')

    del settings[guild]
    with open('settings.json', 'w') as f:
        json.dump(data, f)


def admin(ctx):
    return ctx.message.author.guild_permissions.administrator


@client.command()
async def welcomeChannel(ctx, arg):

    guildInfo = load_json('data.json')

    if admin(ctx):

        guildInfo[str(ctx.message.guild.id)]['welcome'] = discord.utils.get(
            ctx.guild.channels, name=arg).id

        with open("data.json", "w") as f:
            json.dump(guildInfo, f)

        await ctx.message.channel.send(
            f"Welcome Channel has been changed to `{arg}`")


def str_to_bool(string):
    result = ''
    if string == 'True':
        result = True
    elif string == 'False':
        result = False

    return result


@client.command()
async def welcomeMsg(ctx, arg):
    settings = load_json('settings.json')
    if arg.lower() == 'enable':
        settings[str(ctx.message.guild.id)]['welcome'] = 'True'
        await ctx.message.channel.send('Welcome Message is enabled')
    elif arg.lower() == 'disable':
        settings[str(ctx.message.guild.id)]['welcome'] = 'False'
        await ctx.message.channel.send('Welcome Message is disabled')
    else:
        await ctx.message.channel.send("Could not understand that")

    with open('settings.json', 'w') as file:
        json.dump(settings, file)


@client.event
async def on_member_join(member):
    settings = load_json('settings.json')
    enabled = str_to_bool(settings[str(member.guild.id)]['welcome'])
    if enabled:
        colour = discord.Color
        colours = [colour.teal(), colour.green(),
                   colour.orange(), colour.blue()]

        embed = discord.Embed(colour=random.choice(colours))
        embed.set_image(url=member.avatar_url)

        guildInfo = load_json('data.json')

        channel_id = guildInfo[str(member.guild.id)]['welcome']
        await client.get_channel(channel_id).send(f'Hey {member.mention}, Welcome to {member.guild.name}', embed=embed)


@client.command()
async def userLeaveChannel(ctx, arg):
    guildInfo = load_json('data.json')

    if admin(ctx):

        guildInfo[str(ctx.message.guild.id)]['bye'] = discord.utils.get(
            ctx.guild.channels, name=arg).id

        with open("data.json", "w") as f:
            json.dump(guildInfo, f)

        await ctx.message.channel.send(
            f"UserLeave Channel has been changed to `{arg}`")


@client.command()
async def userLeave(ctx, arg):
    settings = load_json('settings.json')
    if arg.lower() == 'enable':
        settings[str(ctx.message.guild.id)]['bye'] = 'True'
        await ctx.message.channel.send('UserLeave Message is enabled')
    elif arg.lower() == 'disable':
        settings[str(ctx.message.guild.id)]['bye'] = 'False'
        await ctx.message.channel.send('UserLeave Message is disabled')
    else:
        await ctx.message.channel.send("Could not understand that")
    with open('settings.json', 'w') as file:
        json.dump(settings, file)


@client.event
async def on_member_remove(member):
    settings = load_json('settings.json')
    enabled = str_to_bool(settings[str(member.guild.id)]['bye'])
    if enabled:
        if member.id != client.user.id:
            guildInfo = load_json('data.json')

            channel_id = guildInfo[str(member.guild.id)]['bye']
            await client.get_channel(channel_id).send(f'{member.name} just left the server.')

client.run(config('TOKEN'))
