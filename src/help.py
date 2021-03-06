import discord
from discord.ext import commands
from utilities import read_database
from discord_components import DiscordComponents, Button, ButtonStyle

class Help(commands.Cog):
    def __init__(self, bot):
        self.client = bot


    @commands.command(name='help', description="The help command")
    async def help(self, ctx, cog_name: str=None):
        if cog_name != None:
            cog_name = cog_name.capitalize()
        cogs_names = self.client.cogs.keys()
        cog_dict = {}
        cog_emojis = {"Admin": "π", "Levels": 'π₯³', "Moderation": 'π΅οΈ', 'Animal': 'πΏ', 'Fun': 'π', "Games": 'π²'}
        prefix = read_database(ctx.guild.id)[8]
        for cogs in cogs_names:
            commands = []
            for command in self.client.cogs[cogs].walk_commands():
                commands.append(command)
            
            cog_dict[cogs] = commands

        if cog_name == None:
        
            embed = discord.Embed(title="Bluey's Command list", description="Thanks for using bluey. We will be adding new features to bluey every now and then")
            embed.set_thumbnail(url=self.client.user.avatar_url)
            embed.add_field(name="πAdmin", value=f"`{prefix}help Admin`")
            embed.add_field(name="π₯³ Levels", value=f"`{prefix}help Levels`")
            embed.add_field(name="π΅οΈ Moderation", value=f"`{prefix}help Moderation`")
            embed.add_field(name="πΆ Animal", value=f"`{prefix}help Animal`")
            embed.add_field(name="π Fun", value=f"`{prefix}help Fun`")
            embed.add_field(name="π² Games", value=f"`{prefix}help Games`")
            embed.add_field(name="Milestones", value=f"`{prefix}help Milestones`")
            embed.add_field(name="Anime", value=f"`{prefix}help Anime`")
            

            components = [Button(style=ButtonStyle.URL, label="Invite", url='https://discord.com/api/oauth2/authorize?client_id=823908962428387338&permissions=8&scope=bot%20applications.commands')]
            await ctx.send(embed=embed, components=components)
            return

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
