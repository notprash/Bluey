import discord
from discord.ext import commands
from utilities import read_database

class Help(commands.Cog):
    def __init__(self, bot):
        self.client = bot


    @commands.command(name='help', description="The help command")
    async def help(self, ctx, cog_name=None):
        cogs_names = self.client.cogs.keys()
        cog_dict = {}
        cog_emojis = {"Admin": "🔒", "Levels": '🥳', "Moderation": '🕵️', 'Music': '💿', 'Animal': '💿', 'Fun': '👀'}
        prefix = read_database(ctx.guild.id)[8]
        for cogs in cogs_names:
            commands = []
            for command in self.client.cogs[cogs].walk_commands():
                commands.append(command)
            
            cog_dict[cogs] = commands

        if cog_name == None:
        
            embed = discord.Embed(title="Bluey's Command list", description="Thanks for using bluey. We will be adding new features bluey every now and then")
            embed.set_thumbnail(url=self.client.user.avatar_url)
            embed.add_field(name="🔒Admin", value=f"`{prefix}help Admin`")
            embed.add_field(name="🥳 Levels", value=f"`{prefix}help Levels`")
            embed.add_field(name="🕵️ Moderation", value=f"`{prefix}help Moderation`")
            embed.add_field(name="💿 Music", value=f"`{prefix}help Music`")
            embed.add_field(name="🐶 Animal", value=f"`{prefix}help Animal`")
            embed.add_field(name="👀 Fun", value=f"`{prefix}help Fun`")
            embed.add_field(name="Anime", value=f"`{prefix}help Anime`")
            embed.add_field(name="Notifier", value=f"`{prefix}help Notifier`", inline=False)

            await ctx.send(embed=embed)

        try:
            commands = cog_dict[cog_name]
            commands = ' '.join([f"`{command}`" for command in commands])
            embed = discord.Embed(title=f"{cog_emojis[cog_name]} {cog_name}", description=commands)
        except:
            commands = cog_dict[cog_name]
            commands = [f"`{command}`" for command in commands]
            commands = ' '.join([f"`{command}`" for command in commands])
            embed = discord.Embed(title=f"{cog_name}", description=commands)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Help(bot))
