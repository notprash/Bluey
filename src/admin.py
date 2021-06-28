from discord.ext import commands
import discord
from utilities import has_admin_permissions, update_database


class Admin(commands.Cog):
    def __init__(self, bot):
        self.client = bot

    async def toggle_msgs(self, ctx, arg, field_name, msg_type):
        # Enable welcome/userLeave msg
        if arg.lower() == 'enable':
            update_database('Settings', field_name, True, 'GuildId', ctx.guild.id)
            await ctx.message.channel.send(f'<a:tick:857439616877199360> {msg_type} Message is enabled')

        # Disables welcome/userLeave msg
        elif arg.lower() == 'disable':
            update_database('Settings', field_name, False, 'GuildId', ctx.guild.id)
            await ctx.message.channel.send(f'<a:tick:857439616877199360> {msg_type} Message is disabled')
        else:
            await ctx.message.channel.send("Could not understand that")

    async def change_channel(self, ctx, arg, field_name, msg_type):
        # Gettings ChannelId by name

        update_database('Settings', f"{field_name}", arg.id, 'GuildId', ctx.guild.id)

        await ctx.message.channel.send(
            f"<a:tick:857439616877199360> {msg_type} Channel has been changed to `{arg}`")




    @commands.command()
    @has_admin_permissions()
    async def welcomeChannel(self, ctx, arg: discord.TextChannel):
        await self.change_channel(ctx, arg, "welcomeChannel", "Welcome")

    @commands.command()
    @has_admin_permissions()
    async def welcomeMsg(self, ctx, arg):
        await self.toggle_msgs(ctx, arg, "welcomeMsg", "Welcome")

    @commands.command()
    @has_admin_permissions()
    async def userLeaveChannel(self, ctx, arg: discord.TextChannel):
        await self.change_channel(ctx, arg, "userLeaveChannel", "User Leave")

    @commands.command()
    @has_admin_permissions()
    async def userLeaveMsg(self, ctx, arg):
        await self.toggle_msgs(ctx, arg, "userLeaveMsg", "UserLeave")

   

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx, channel: discord.TextChannel = None):
        channel = channel or ctx.channel

        # Overwrites user permissions
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = False
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)

        await ctx.send('<a:tick:857439616877199360> Channel locked.')

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx, channel: discord.TextChannel = None):
        channel = channel or ctx.channel

        # Overwrites user permssions
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = True
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)

        await ctx.send('<a:tick:857439616877199360> Channel Unlocked.')

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def warncount(self, ctx, count):
        
        update_database("Settings", 'warncount', int(count), 'GuildId', ctx.guild.id)

        await ctx.send(f"⚠️ Warn Count changed to {count}")


# Add bot as an extension
def setup(bot):
    bot.add_cog(Admin(bot))
