import discord
from discord.ext import commands
import kitsupy

def getlist(dict):
    list = []
    for key in dict.keys():
        list.append(key)
    return list

class Anime(commands.Cog):
    def __init__(self, bot):
        self.client = bot

    @commands.command()
    async def anime(self, ctx, *query):
        query = ' '.join(query)
        data = kitsupy.search('anime', query)
        id = getlist(data)
        result = kitsupy.get_info('anime', id[1])
        en_title, jp_title = result['titles']['en'], result['titles']['ja_jp']
        en_jp_title = ''
        if result['titles']['en_jp'] == '':
            en_jp_title = en_title
        else:
            en_jp_title = result['titles']['en_jp']
        average_rating, popularity_rank, rating_rank = result['averageRating'], ['popularityRank'], result['ratingRank']
        image = result['posterImage']['medium']
        episode_count = result['episodeCount']
        start_date = result['startDate']
        end_date = result['endDate']
        synopsis = result['synopsis']

        emb = discord.Embed(title = en_jp_title, description=synopsis, color = discord.Color.blue())
        emb.add_field(name='English', value=en_title, inline=True)
        emb.add_field(name='Japanese', value = jp_title, inline=True)
        emb.add_field(name = chr(173), value = chr(173))
        emb.add_field(name='Average Rating', value=average_rating, inline=True)
        emb.add_field(name='Popularity Rank', value=popularity_rank, inline=True)
        emb.add_field(name='Rating Rank', value=rating_rank, inline=True)
        emb.add_field(name='Start Date', value=start_date, inline=True)
        emb.add_field(name='End Date', value=end_date, inline=True)
        emb.add_field(name='Episode Count', value=episode_count, inline=True)
        emb.set_image(url = image)
        await ctx.send(embed = emb)

    @commands.command()
    async def manga(self, ctx, *query):
        query = ' '.join(query)
        data = kitsupy.search('anime', query)
        id = getlist(data)
        result = kitsupy.get_info('anime', id[1])
        en_title, jp_title = result['titles']['en'], result['titles']['ja_jp']
        en_jp_title = ''
        if result['titles']['en_jp'] == '':
            en_jp_title = en_title
        else:
            en_jp_title = result['titles']['en_jp']
        average_rating, popularity_rank, rating_rank = result['averageRating'], ['popularityRank'], result['ratingRank']
        image = result['posterImage']['medium']
        episode_count = result['episodeCount']
        start_date = result['startDate']
        end_date = result['endDate']
        synopsis = result['synopsis']

        emb = discord.Embed(title = en_jp_title, description=synopsis, color = discord.Color.blue())
        emb.add_field(name='English', value=en_title, inline=True)
        emb.add_field(name='Japanese', value = jp_title, inline=True)
        emb.add_field(name = chr(173), value = chr(173))
        emb.add_field(name='Average Rating', value=average_rating, inline=True)
        emb.add_field(name='Popularity Rank', value=popularity_rank, inline=True)
        emb.add_field(name='Rating Rank', value=rating_rank, inline=True)
        emb.add_field(name='Start Date', value=start_date, inline=True)
        emb.add_field(name='End Date', value=end_date, inline=True)
        emb.add_field(name='Episode Count', value=episode_count, inline=True)
        emb.set_image(url = image)
        await ctx.send(embed = emb)

    @commands.command()
    async def char(self, ctx, *query):
        query = ' '.join(query)
        data = kitsupy.search('characters', query)
        id = id = getlist(data)
        result = kitsupy.get_info('characters', id[1])
        name = result['name']
        eng_name = result['names']['en']
        jap_name = result['names']['ja_jp']
        desc = result['description']
        u_desc = '%.4090s' % desc + '...'
        image = result['image']['original']
        other_name = ''
        if len(result['otherNames']) != 0:
            other_name = result['otherNames'][0]
        else:
            other_name = 'No other names'

        emb = discord.Embed(title = name, description=u_desc, color = discord.Color.blue())
        emb.add_field(name="English", value=eng_name, inline=True)
        emb.add_field(name="Japanese", value=jap_name, inline=True)
        emb.add_field(name='Other Names', value=other_name, inline=True)
        emb.set_image(url = image)
        await ctx.send(embed = emb)

def setup(bot):
    bot.add_cog(Anime(bot))
