from discord.ext import commands
import discord
import sqlite3
from utilities import help_embed


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.client = bot


    @commands.command()
    @commands.has_permissions(kick_members=True, ban_members=True)
    async def mute(self, ctx, member: discord.Member=None):
        if await help_embed(ctx.channel, "mute <@member>", member):
            return
        server = ctx.guild
        role = discord.utils.get(server.roles, name="Muted")
        if role != None:
            await member.add_roles(role)
            await ctx.send(f"{member} has been muted from the text 🤐")
            return

        role = await server.create_role(name="Muted")

        for channel in server.channels:
            await channel.set_permissions(role, send_messages=False, add_reactions=False, speak=False)

        await member.add_roles(role)
        await ctx.send(f"{member} has been muted from the text 🤐")


    @commands.command()
    @commands.has_permissions(kick_members=True, ban_members=True)
    async def unmute(self, ctx, member: discord.Member=None):
        if await help_embed(ctx.channel, "unmute <@member>", member):
            return
        role = discord.utils.get(ctx.guild.roles, name="Muted")
        await member.remove_roles(role)
        await ctx.send(f"{member} has been unmuted")


    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member=None, reason="No Reason was provided"):
        if await help_embed(ctx.channel, "ban <@member> <reason>", member):
            return
        await ctx.send(f'{member.name} has been banned from the server')
        await member.ban(reason=reason)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, member=None):
        if await help_embed(ctx.channel, "unban <@member>", member):
            return
        banned_users = await ctx.guild.bans()

        # Splits member_name, member_disc ie Prash#4945 = (Prash, 4945)
        member_name, member_disc = member.split("#")

        for banned_entry in banned_users:
            user = banned_entry.user

            # Find user to unban
            if (user.name, user.discriminator) == (member_name, member_disc):
                await ctx.guild.unban(user)
                await ctx.send(f"Unbanned {user.name}#{user.discriminator} from the server")
                return

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, userName: discord.Member=None, reason="No reason was provided"):
        if await help_embed(ctx.channel, "kick <@member> <reason>", userName):
            return
        await userName.kick(reason=reason)
        await ctx.send(f"{userName} has been kicked from the server")

    @commands.command()
    @commands.has_permissions(kick_members=True, ban_members=True)
    async def warn(self, ctx, member: discord.Member=None, reason="No reason"):
        if await help_embed(ctx.channel, "warn <@member>", member):
            return
        with sqlite3.connect("db.sqlite3") as db:
            try: 
                command = "CREATE TABLE Warnings (userid int, count int, guildId int)"
                db.execute(command)
                db.commit()
            except Exception:
                print("Table Exists")

            userid = member.id
            username = f"{member.name}#{member.discriminator}"
            command = f"SELECT count FROM Warnings WHERE userid = {userid} AND guildId = {ctx.guild.id}"
            result = db.execute(command)
            count = result.fetchall()
            command = f"SELECT warncount FROM Settings WHERE GuildId = {ctx.guild.id}"
            execute = db.execute(command)
            warncount = execute.fetchall()[0][0]
            if len(count) == 0:
                command = "INSERT INTO Warnings (userid, count, guildId) VALUES(?, ?, ?)"
                values = {"userid": userid, "count": 1, "guildId": ctx.guild.id}
                db.execute(command, tuple(values.values()))
                db.commit()
                if warncount == 1:
                    command = f"DELETE FROM Warnings WHERE userid = {userid}"
                    db.execute(command)
                    await member.ban(reason=reason)
                    embed = discord.Embed(title=f"{username} has banned from the server")
                    embed.set_footer(text="Crossed the warn limit", icon_url=member.avatar_url)
                    embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
                    await ctx.send(embed=embed)
                    return
            else:
                count = count[0][0]

                if warncount == count + 1:
                    command = f"DELETE FROM Warnings WHERE userid = {userid}"
                    db.execute(command)
                    await member.ban(reason=reason)
                    embed = discord.Embed(title=f"{username} has banned from the server")
                    embed.set_footer(text="Crossed the warn limit", icon_url=member.avatar_url)
                    embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
                    await ctx.send(embed=embed)
                    return
                else:

                    command = f"UPDATE Warnings set count = {count + 1} WHERE userid = {userid}"
                    db.execute(command)
                    db.commit()


        await ctx.send(f"{member} has been warned")

    @commands.command(aliases=['rwarn'])
    @commands.has_permissions(ban_members=True, kick_members=True)
    async def removewarn(self, ctx, member: discord.Member=None, warncount=1):
        if await help_embed(ctx.channel, "removewarn <@member> <warncount>", member):
            return
        with sqlite3.connect("db.sqlite3") as db:
            try: 
                command = "CREATE TABLE Warnings (userid int, count int, guildId int)"
                db.execute(command)
                db.commit()
            except Exception:
                print("Table Exists")

            userid = member.id
            command = f"SELECT count FROM Warnings WHERE userid = {userid} AND guildId = {ctx.guild.id}"
            result = db.execute(command)
            count = result.fetchone()[0]
            if count <= 0:
                return await ctx.send(f"{member.mention} does not have any warnings yet 😕")
            count = count - warncount
            if count < 0:
                count = 0

            db.execute(f"Update Warnings set count = {count} WHERE guildId = {ctx.guild.id}")
            db.commit()
            
        if warncount == 1:
            await ctx.send(f"✅ **{warncount} warn** has been removed from {member.mention}")
        else:
            await ctx.send(f"✅ **{warncount} warns** has been removed from {member.mention}")

    

def setup(bot):
    bot.add_cog(Moderation(bot))
