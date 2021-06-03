from discord.ext import commands
import discord
import sqlite3


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.client = bot


    @commands.command()
    @commands.has_permissions(kick_members=True, ban_members=True)
    async def mute(self, ctx, member: discord.Member):
        server = ctx.guild
        role = discord.utils.get(server.roles, name="Muted")
        if role != None:
            await member.add_roles(role)
            await ctx.send(f"{member} has been muted from the text 🤐")
            return

        role = await server.create_role(name="Muted")

        for channel in server.channels:
            await channel.set_permissions(role, send_messages=False)

        await member.add_roles(role)
        await ctx.send(f"{member} has been muted from the text 🤐")


    @commands.command()
    @commands.has_permissions(kick_members=True, ban_members=True)
    async def unmute(self, ctx, member: discord.Member):
        role = discord.utils.get(ctx.guild.roles, name="Muted")
        await member.remove_roles(role)
        await ctx.send(f"{member} has been unmuted")


    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, reason="No Reason was provided"):
        await ctx.send(f'{member.name} has been banned from the server')
        await member.ban(reason=reason)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, member, reason="No Reason was provided"):
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
    async def kick(self, ctx, userName: discord.Member, reason="No reason was provided"):
        await userName.kick(reason=reason)
        await ctx.send(f"{userName} has been kicked from the server")

    @commands.command()
    @commands.has_permissions(kick_members=True, ban_members=True)
    async def warn(self, ctx, member: discord.Member, reason="No reason"):
        with sqlite3.connect("db.sqlite3") as db:
            try: 
                command = "CREATE TABLE Warnings (Name TEXT, count int, guildId int)"
                db.execute(command)
                db.commit()
            except Exception:
                print("Table Exists")

            username = f"{member.name}#{member.discriminator}"
            command = f"SELECT count FROM Warnings WHERE Name = '{username}' AND guildId = {ctx.guild.id}"
            result = db.execute(command)
            count = result.fetchall()
            if len(count) == 0:
                command = "INSERT INTO Warnings (Name, count, guildId) VALUES(?, ?, ?)"
                values = {"Name": f"{username}", "count": 1, "guildId": ctx.guild.id}
                db.execute(command, tuple(values.values()))
                db.commit()
            else:
                count = count[0][0]
                # Get WarnCount
                command = f"SELECT warncount FROM Settings WHERE GuildId = {ctx.guild.id}"
                execute = db.execute(command)
                warncount = execute.fetchall()[0][0]

                if warncount == count + 1:
                    command = "DELETE FROM Warnings WHERE Name = '{username}'"
                    db.execute(command)
                    await member.ban(reason=reason)
                    embed = discord.Embed(title=f"{username} has banned from the server")
                    embed.set_footer(text="Crossed the warn limit", icon_url=member.avatar_url)
                    embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
                    await ctx.send(embed=embed)
                else:

                    command = f"UPDATE Warnings set count = {count + 1} WHERE Name = '{username}'"
                    values = {"Name": f"{username}", "count": int(count) + 1}
                    db.execute(command)
                    db.commit()


        await ctx.send(f"{member} has been warned")
def setup(bot):
    bot.add_cog(Moderation(bot))
