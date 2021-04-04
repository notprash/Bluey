from discord.ext import commands
import discord
import sqlite3
from utilities import read_database, has_admin_permissions, update_settings

class Commands(commands.Cog):
    def __init__(self, bot):
        self.client = bot

    async def toggle_msgs(self, ctx, arg, field_name, msg_type):
        settings = read_database(ctx.guild.id)
        if arg.lower() == 'enable':
            update_settings(field_name, True, ctx.guild.id)
            await ctx.message.channel.send(f'{msg_type} Message is enabled')
        elif arg.lower() == 'disable':
            update_settings(field_name, False, ctx.guild.id)
            await ctx.message.channel.send(f'{msg_type} Message is disabled')
        else:
            await ctx.message.channel.send("Could not understand that")

    async def change_channel(self, ctx, arg, field_name, msg_type):
        settings = read_database(ctx.guild.id)
        channelId = discord.utils.get(
                ctx.guild.channels, name=arg).id

        update_settings(f"{field_name}", channelId, ctx.guild.id)

        await ctx.message.channel.send(
            f"{msg_type} Channel has been changed to `{arg}`")



    @commands.command()
    @has_admin_permissions()
    async def welcomeChannel(self, ctx, arg):
        await self.change_channel(ctx, arg, "welcomeChannel", "Welcome")



    @commands.command()
    @has_admin_permissions()
    async def welcomeMsg(self, ctx, arg):
        await self.toggle_msgs(ctx, arg, "welcomeMsg", "Welcome")   

    @commands.command()
    @has_admin_permissions()
    async def userLeaveChannel(self, ctx, arg):
        await self.change_channel(ctx, arg, "userLeaveChannel", "User Leave")

    @commands.command()
    @has_admin_permissions()
    async def userLeaveMsg(self, ctx, arg):
        await self.toggle_msgs(ctx, arg, "userLeaveMsg", "UserLeave")


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


    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, member, reason="No Reason was provided"):
        banned_users = await ctx.guild.bans()
        member_name, member_disc = member.split("#")

        for banned_entry in banned_users:
            user = banned_entry.user


            if (user.name, user.discriminator) == (member_name, member_disc):
                await ctx.guild.unban(user)
                await ctx.send(f"Unbanned {user.name}#{user.discriminator} from the server")
                return
            

        
        

def setup(bot):
    bot.add_cog(Commands(bot))
