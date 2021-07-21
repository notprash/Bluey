from os import read
import sqlite3
from discord.ext import commands
import discord

def read_database(guildId):
    with sqlite3.connect('db.sqlite3') as db:
        # Fetching Data
        command = f"SELECT * FROM Settings WHERE GuildId = '{guildId}'"

        data = db.execute(command)
        data = data.fetchone()

    return data

def update_database(database, setting, value, condition_parameter, condition_value):
    with sqlite3.connect("db.sqlite3") as db:
        command = f"UPDATE {database} SET {setting} = {value} WHERE {condition_parameter} = {condition_value}" 
        db.execute(command)
        db.commit()      


def has_admin_permissions():
    return commands.has_permissions(administrator=True)

def not_none(value):
    return value != None


async def help_embed(channel, syntax, none_value):
    if none_value == None or none_value == ():
        prefix = read_database(channel.guild.id)[8]
        description = f'The command input is incomplete. \n```{prefix}{syntax}```'
        embed = discord.Embed(title="Error", description=description, color=discord.Color.red())
        await channel.send(embed=embed)
        return True

    return False
