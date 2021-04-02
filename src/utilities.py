import json
from discord.ext import commands
def load_json(file):
    with open(file, 'r') as f:
        guildInfo = json.load(f)

    return guildInfo


def str_to_bool(string):
    result = ''
    if string == 'True':
        result = True
    elif string == 'False':
        result = False

    return result


def has_admin_permissions():
    return commands.has_permissions(administrator=True)