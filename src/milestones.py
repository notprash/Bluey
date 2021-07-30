from discord.ext import commands
from discord.ext.tasks import loop
import discord
from utilities import help_embed, read_database, update_database, has_admin_permissions
import sqlite3

class Milestones(commands.Cog):
    def __init__(self, bot):
        self.client = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.reached_milestone.start()
    
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

            
            
            db.commit()


    @commands.command()
    @has_admin_permissions()
    async def milestone(self, ctx, keyword=None, value=None, *value2):
        if await help_embed(ctx.channel, "milestone add <member_count> \n milestone remove <member_count>\n milestone list", keyword):
            return
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


    
def setup(bot):
    bot.add_cog(Milestones(bot))