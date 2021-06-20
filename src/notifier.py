from discord.ext import commands
import discord
import praw
from decouple import config
from praw.reddit import Submission
import asyncio

r = praw.Reddit(client_id = config("client_id"), 
	client_secret = config('client_secret'), 
	user_agent = config("user_agent"), 
	password = config("password"), check_for_async=False)

class Notifier(commands.Cog):
	def __init__(self, bot):
		self.client = bot

	def sub_exists(self, sub): # Check if a subreddit exists
		exists = True
		try:
			r.subreddits.search_by_name(sub, exact=True)
		except Exception:
			exists = False
		return exists


	async def get_posts(self, subname, channel: discord.TextChannel):
		submissions = r.subreddit(subname)
		sent = []
		while True:
			for submission in submissions.new(limit=5):
				title = submission.title
				if title in sent:
					break
				sent.append(title)
				embed = discord.Embed(title=title)
				embed.set_image(url=submission.url)
				await channel.send(embed=embed)
			await asyncio.sleep(60)

	@commands.command()
	async def rnotify(self, ctx, subname, channel: discord.TextChannel):
		if self.sub_exists(subname):
			self.client.loop.create_task(self.get_posts(subname, channel))
			await ctx.send(f"r/{subname} added to {channel.mention} 🥳")
		else:
			await ctx.send(f"Couldn't find the subreddit :(")

def setup(bot):
	bot.add_cog(Notifier(bot))