from discord.ext import commands
import discord
from utilities import read_database, has_admin_permissions, update_database
from googleapiclient.discovery import build
from decouple import config
from num2words import num2words


class Commands(commands.Cog):
    def __init__(self, bot):
        self.client = bot

    async def toggle_msgs(self, ctx, arg, field_name, msg_type):
        # Enable welcome/userLeave msg
        if arg.lower() == 'enable':
            update_database('Settings', field_name, True, 'GuildId', ctx.guild.id)
            await ctx.message.channel.send(f'{msg_type} Message is enabled')

        # Disables welcome/userLeave msg
        elif arg.lower() == 'disable':
            update_database('Settings', field_name, False, 'GuildId', ctx.guild.id)
            await ctx.message.channel.send(f'{msg_type} Message is disabled')
        else:
            await ctx.message.channel.send("Could not understand that")

    async def change_channel(self, ctx, arg, field_name, msg_type):
        # Gettings ChannelId by name

        update_database('Settings', f"{field_name}", arg.id, 'GuildId', ctx.guild.id)

        await ctx.message.channel.send(
            f"{msg_type} Channel has been changed to `{arg}`")


    @commands.command()
    async def youtubestats(self, ctx, channelId):

        # Get api key
        api_key = config("APIKEY")

        # Fetch the youtube the api
        youtube = build('youtube', 'v3', developerKey=api_key) 

        # Get Part statistics 
        request = youtube.channels().list(part='statistics', id=channelId)
        request = request.execute()

        # Return if channel does not exist
        if request['pageInfo']['totalResults'] == 0:
            await ctx.send("Channel not Found!")
            return

        # Create Embed
        stats = request['items'][0]['statistics']
        fields = '''
        **SubcriberCount** 🎉 >> {:,d}
        **View Count** 🔥 >> {}
        **Video Count** >> {}
        '''.format(int(stats['subscriberCount']), ' '.join(num2words(stats['viewCount']).split()[:2]).capitalize()[:-1], stats['videoCount'])
        
        embed = discord.Embed(description=fields, color=discord.Color.random()).set_author(name=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)



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
    async def avatar(self, ctx, member: discord.User = None):
        if member == None:
            avatar = ctx.message.author.avatar_url
            user_name = ctx.message.author
        else:
            avatar = member.avatar_url
            user_name = member

        embed = discord.Embed(description=f"Requested by {ctx.message.author}")
        embed.set_author(name=f"{user_name}'s Avatar", icon_url=avatar)
        embed.set_image(url=avatar)

        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx, channel: discord.TextChannel = None):
        channel = channel or ctx.channel

        # Overwrites user permissions
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = False
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)

        await ctx.send('Channel locked.')

    @commands.command()
    @has_admin_permissions()
    async def unlock(self, ctx, channel: discord.TextChannel = None):
        channel = channel or ctx.channel

        # Overwrites user permssions
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = True
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)

        await ctx.send('Channel Unlocked.')


    @commands.command()
    async def stats(self, ctx):
        # Settings Embed Color
        color = discord.Color.blue()
        embed = discord.Embed(color=color)
        embed.set_author(name=f"{ctx.guild.name}'s stats",
                         icon_url=ctx.guild.icon_url)

        # Discord Server ID
        embed.add_field(name="ID", value=f"`{ctx.guild.id}`", inline=False)

        # Get Total Member Count
        member_count = len(
            [member for member in ctx.guild.members if not member.bot])
        embed.add_field(name="Total Members", value=f"`{member_count}`")

        embed.add_field(name="Total Roles", value=f"`{len(ctx.guild.roles)}`")

        embed.add_field(
            name="Owner", value=ctx.guild.owner.mention, inline=False)

        await ctx.send(embed=embed)


# Add bot as an extension
def setup(bot):
    bot.add_cog(Commands(bot))
