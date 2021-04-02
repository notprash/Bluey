from discord.ext import commands
import discord
import json
from utilities import load_json, has_admin_permissions 

class Commands(commands.Cog):
    def __init__(self, bot):
        self.client = bot
    @commands.command()
    @has_admin_permissions()
    async def welcomeChannel(self, ctx, arg):

        guildInfo = load_json('config/data.json')

        guildInfo[str(ctx.message.guild.id)]['welcome'] = discord.utils.get(
            ctx.guild.channels, name=arg).id


        with open("config/data.json", "w") as f:
            json.dump(guildInfo, f)

        await ctx.message.channel.send(
            f"Welcome Channel has been changed to `{arg}`")


    @commands.command()
    @has_admin_permissions()
    async def welcomeMsg(self, ctx, arg):
        settings = load_json('config/settings.json')
        if arg.lower() == 'enable':
            settings[str(ctx.message.guild.id)]['welcome'] = 'True'
            await ctx.message.channel.send('Welcome Message is enabled')
        elif arg.lower() == 'disable':
            settings[str(ctx.message.guild.id)]['welcome'] = 'False'
            await ctx.message.channel.send('Welcome Message is disabled')
        else:
            await ctx.message.channel.send("Could not understand that")

        with open('config/settings.json', 'w') as file:
            json.dump(settings, file)


    @commands.command()
    @has_admin_permissions()
    async def userLeaveChannel(self, ctx, arg):
        guildInfo = load_json('config/data.json')

        guildInfo[str(ctx.message.guild.id)]['bye'] = discord.utils.get(
            ctx.guild.channels, name=arg).id

        with open("config/data.json", "w") as f:
            json.dump(guildInfo, f)

        await ctx.message.channel.send(
            f"UserLeave Channel has been changed to `{arg}`")

    @commands.command()
    @has_admin_permissions()
    async def userLeaveMsg(self, ctx, arg):
        settings = load_json('config/settings.json')
        if arg.lower() == 'enable':
            settings[str(ctx.message.guild.id)]['bye'] = 'True'
            await ctx.message.channel.send('User Leave Message is enabled')
        elif arg.lower() == 'disable':
            settings[str(ctx.message.guild.id)]['bye'] = 'False'
            await ctx.message.channel.send('User Leave Message is disabled')
        else:
            await ctx.message.channel.send("Could not understand that")

        with open('config/settings.json', 'w') as file:
            json.dump(settings, file)


    @commands.command()
    async def avatar(self, ctx, member: discord.User = None):
        avatar = member.avatar_url
        await ctx.send(avatar)


    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx, channel: discord.TextChannel = None):
        channel = channel or ctx.channel
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = False
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.send('Channel locked.')


    @commands.command()
    @has_admin_permissions()
    async def unlock(self, ctx, channel: discord.TextChannel = None):
        channel = channel or ctx.channel
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = True
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.send('Channel Unlocked.')


    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, reason="No Reason was provided"):
        await ctx.send(f'{member.name} has been banned from the server')
        await member.ban(reason=reason)

def setup(bot):
    bot.add_cog(Commands(bot))