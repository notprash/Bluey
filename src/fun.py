# Imports
import discord
from discord.ext import commands
import random
from requests import get
from bs4 import BeautifulSoup
from decouple import config
from googleapiclient.discovery import build
from decouple import config
from num2words import num2words
from utilities import help_embed
from discord_slash.cog_ext import cog_slash

key = 'https://meme-api.herokuapp.com/gimme/'

class Fun(commands.Cog):
    def __init__(self, bot):
        self.client = bot

    @commands.command(name="poll", description='Creates a poll')
    async def poll(self, ctx, question=None, choice_a=None, choice_b=None, choice_c="", choice_d="", choice_e="", choice_f="", choice_g=""):
        arg = 0
        # Emoji List
        if question == None or choice_a == None or choice_b == None:
            arg = None

        if await help_embed(ctx.channel, "poll \"<question>\" \"<choice_a>\" \"<choice_b>\" .......", arg):
            return
        emojis = ["\N{REGIONAL INDICATOR SYMBOL LETTER A}",
                "\N{REGIONAL INDICATOR SYMBOL LETTER B}",
                "\N{REGIONAL INDICATOR SYMBOL LETTER C}",
                "\N{REGIONAL INDICATOR SYMBOL LETTER D}",
                "\N{REGIONAL INDICATOR SYMBOL LETTER E}", 
                "\N{REGIONAL INDICATOR SYMBOL LETTER F}",
                "\N{REGIONAL INDICATOR SYMBOL LETTER G}"]

        choices_list = [choice_a, choice_b, choice_c , choice_d, choice_e, choice_f, choice_g]
        emoji_count = 0 
        final_str = ""
        for i in range(len(choices_list)):
            if choices_list[i] != "":
                final_str += f"{emojis[i]} {choices_list[i]}\n"
                emoji_count += 1
        # Create Embed
        embed = discord.Embed(description=final_str, color=ctx.author.color).set_author(name=ctx.author, icon_url=ctx.author.avatar_url)


        msg = await ctx.send(f"**{question}**", embed=embed)

        # Add Reactions
        for emoji in emojis[:emoji_count]:
            await msg.add_reaction(emoji)

#### Command for Memes

    @commands.command()
    async def meme(self, ctx, sub = 'memes'):
        data = get(key).json()
        title = data['title']
        embed = discord.Embed(title=title)
        embed.set_image(url=data['url'])
        await ctx.send(embed=embed)

#### Command for Wallpapers

    @commands.command(aliases=["w"])
    async def wallpaper(self, ctx, *query):
        if await help_embed(ctx.channel, "wallpaper <character_name>", query):
            return
        query = ' '.join(query)
        site = get(f'https://www.wallpaperflare.com/search?wallpaper={query}').text
        soup = BeautifulSoup(site, 'lxml')
        link = soup.find_all('a')

        wallpaper = []
        for i in link:
            if i.get('itemprop') == 'url':
                wallpaper.append(i)

        if len(wallpaper) == 0:
            await ctx.send('Sorry! Wallpaper not found :( ')
        else:
            wallpaper.pop(0)
            random_wall = random.choice(wallpaper)
            image = random_wall.contents[1].get('data-src') 
            webpage = random_wall.get('href')

            description = f"[Wallpaper Link]({webpage})"
            emb = discord.Embed(title = query, description = description)
            emb.set_image(url = image)
            await ctx.send(embed = emb)

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
    async def stats(self, ctx):
        # Settings Embed Color
        color = discord.Color.blue()
        embed = discord.Embed(color=color)
        embed.set_author(name=f"{ctx.guild.name}'s stats",
                         icon_url=ctx.guild.icon_url)

        time = ctx.guild.created_at
        time = time.strftime("%d/%m/%Y")
        embed.add_field(name="🆔 ID", value=f"`{ctx.guild.id}`")
        embed.add_field(name="👑 Owner", value=ctx.guild.owner.mention)
        embed.add_field(name="📆 Created on", value=time)
        embed.add_field(name="<a:nitroboost:859792594032918558>  Boosts", value=ctx.guild.premium_subscription_count)


        member_count = len(
            [member for member in ctx.guild.members if not member.bot])
        embed.add_field(name="👤 Members", value=f"`{member_count}`")

        embed.add_field(name="Roles", value=f"`{len(ctx.guild.roles)}`")
        embed.add_field(name=f"💬 Channels ({len(ctx.guild.text_channels) + len(ctx.guild.voice_channels)})", value=f"{len(ctx.guild.text_channels)} Text | {len(ctx.guild.voice_channels)} Voice")
        embed.set_thumbnail(url=ctx.guild.icon_url)


        await ctx.send(embed=embed)
    @commands.command()
    async def youtubestats(self, ctx, channelId=None):
        if await help_embed(ctx.channel, "youtubestats <channelId>", channelId):
            return

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

def setup(bot):
    bot.add_cog(Fun(bot))
