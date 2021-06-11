from discord.ext import commands
import discord
import praw
import random
from decouple import config

id = config('ID')
secret = config('SECRET')
username = config('USERNAME')
password = config('PASSWORD')
reddit = praw.Reddit(client_id = id,
                     client_secret = secret,
                     username = username,
                     password = password,
                     user_agent = 'Zoey', check_for_async=False)

class Fun(commands.Cog):
    def __init__(self, bot):
        self.client = bot

    @commands.command()
    async def meme(self, ctx, sub = 'memes'):
        subreddit = reddit.subreddit(sub)

        all_posts = [] # A list of all posts

        top = subreddit.top(limit = 20) # The top 20 posts in the the subreddit
        for post in top:
            all_posts.append(post) # Adding individual posts to the list

        random_post = random.choice(all_posts) # A random post from the list of all the posts

        name = random_post.title # Name of the Post
        url = random_post.url # Url of the image

        emb = discord.Embed(title = name) # The embed
        emb.set_image(url = url)

        await ctx.send(embed = emb)

def setup(bot):
    bot.add_cog(Fun(bot))