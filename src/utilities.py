import sqlite3
from discord.ext import commands

def read_database(guildId):
    with sqlite3.connect('db.sqlite3') as db:
        command = f"SELECT * FROM Settings WHERE GuildId = '{guildId}'"
        data = db.execute(command)
        data = data.fetchall()

    return data[0]

def update_settings(setting, value, guildId):
    with sqlite3.connect("db.sqlite3") as db:
        command = f"UPDATE Settings SET {setting} = {value} WHERE GuildId = {guildId}" 
        db.execute(command)
        db.commit()      


def has_admin_permissions():
    return commands.has_permissions(administrator=True)
