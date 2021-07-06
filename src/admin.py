from os import read
import sqlite3
from discord.ext import commands
import discord
from utilities import has_admin_permissions, read_database, update_database
from discord.ext.tasks import loop


class Admin(commands.Cog):
    def __init__(self, bot):
        self.client = bot



    @commands.Cog.listener()
    async def on_ready(self):
        self.reached_milestone.start()

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

    @loop(minutes=10)
    async def reached_milestone(self):
        with sqlite3.connect('db.sqlite3') as db:
            cursor = db.execute("SELECT * FROM Milestones")
            values = cursor.fetchall()
            for value in values:
                guildid, members = value
                guild = self.client.get_guild(guildid)
                server_members = [member for member in guild.members if not member.bot]
                member_count = len(server_members)
                if member_count >= members:
                    channel = self.client.get_channel(read_database(guild.id)[7])
                    description = f"**{members} members** 🥳 "
                    embed = discord.Embed(description=description, color=discord.Color.blue()).set_author(name="Milestone reached", icon_url=guild.icon_url)
                    embed.set_thumbnail(url=guild.icon_url)
                    db.execute(f"DELETE FROM Milestones WHERE guildId = {guild.id} AND members = {members}")
                    try:
                        cursor = db.execute(f"SELECT members FROM Milestones WHERE guildId = {guild.id} AND members > {members}").fetchone()[0]
                        embed.set_footer(text=f"Next Milestone {cursor}", icon_url=self.client.user.icon_url)
                    except:
                        pass
                    await channel.send(embed=embed)


    @commands.command()
    @has_admin_permissions()
    async def milestone(self, ctx, keyword, value=None, *value2):
        with sqlite3.connect("db.sqlite3") as db:
            try:
                db.execute("CREATE TABLE Milestones (guildId int, members int)")
            except:
                pass
            if keyword == 'add' and value != None:
                db.execute("INSERT INTO Milestones VALUES(?, ?)", (ctx.guild.id, int(value)))
                db.commit()
                await ctx.send(f"<a:bluecrystal:860705116893347841> Added new milestone, You will be notified once the server reaches {value} members")
                cursor = db.execute(f"SELECT milestone FROM Settings WHERE guildId = {ctx.guild.id}")
                value = cursor.fetchone()[0]
                if value == 0:
                    await ctx.send("Please change the milestone channel using `milestone channel [channel mention]`")

            elif keyword == 'remove' and value != None:
                db.execute(f"DELETE FROM Milestones WHERE guildId = {ctx.guild.id} and members = {value}")
                db.commit()
                await ctx.send("Successfully removed the milestone")

            elif keyword == 'list':
                cursor = db.execute(f"SELECT members FROM Milestones WHERE guildId = {ctx.guild.id} ORDER BY members ASC")
                values = cursor.fetchall()
                description = ""
                for value in values:
                    description += f"<a:bluecrystal:860705116893347841> <a:arrow:855079459656564767> {value[0]} members\n"


                embed = discord.Embed(color=ctx.author.color, description=description)
                embed.set_author(icon_url=self.client.user.avatar_url, name="Milestones")
                embed.set_thumbnail(url=ctx.guild.icon_url)
                embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

                await ctx.send(embed=embed)

            elif keyword == 'channel' and value != None:
                value = int(value[2:-1])
                channel = await self.client.fetch_channel(value)
                update_database('Settings', 'milestone', channel.id, 'guildId', ctx.guild.id)
                await ctx.send(f"Selected {channel.mention} for Milestone events")


    @commands.command()
    @has_admin_permissions()
    async def prefix(self, ctx, prefix):
        with sqlite3.connect("db.sqlite3") as db:
            sql = f"UPDATE Settings SET prefix = '{prefix}' WHERE guildId = {ctx.guild.id}" 
            db.execute(sql)
            db.commit()

        await ctx.send(f"Prefix set to {prefix}")

# Add bot as an extension
def setup(bot):
    bot.add_cog(Admin(bot))
