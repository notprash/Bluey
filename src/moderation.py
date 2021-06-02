from discord.ext import commands
import discord


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

    


def setup(bot):
    bot.add_cog(Moderation(bot))
