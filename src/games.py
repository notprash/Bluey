import discord
from discord.ext import commands
# from discord.ext import embed
import random

# words = ['mute', 'ban', 'user', 'discord', 'role', 'nickname', 'testing', 'zoey', 'prash', 'emperor', 'game', 'meme', 'anime']
with open("config/words.txt", "r") as file:
    allText = file.read()
    words = list(map(str, allText.split()))

class Games(commands.Cog):
    def __init__(self, bot):
        self.client = bot

### Number Guessing Game
    @commands.command()
    async def ngg(self, ctx):
        num = random.randint(1, 10)
        await ctx.send('Choose a number between 1 to 10')

        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel and int(msg.content) in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        msg = await self.client.wait_for("message", check=check)
        i = 3
        while i >= 1:
            if int(msg.content) == num:
                await ctx.send("Kudos! You guessed the number right.")
                break
            else:
                i -= 1
                await ctx.send(f'Try Again, only {i} attempts left')
                msg = await self.client.wait_for("message", check=check)
        if i == 1:
            await ctx.send(f"Sorry! It was {num}")

### Memory Game
    @commands.command()
    async def mg(self, ctx):
        word = random.sample(words, 5)
        description = ""
        for i in word:
            description += i + "\n"
        emb = discord.Embed(title="Rewrite the following words", description=description)
        emb.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
        await ctx.send(embed = emb, delete_after = 3.0)

        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel

        msg = await self.client.wait_for("message", check=check)

        answer = msg.content.split()

        if answer == word:
            await ctx.send("Congrats!")
        else:
            await ctx.send("Maybe next time!")

### 8 Ball
    @commands.command()
    async def eb(self, ctx, *ques):
        ques = ' '.join(ques)
        responses = ["It is certain.",
                "It is decidedly so.",
                "Without a doubt.",
                "Yes - definitely.",
                "You may rely on it.",
                "As I see it, yes.",
                "Most likely.",
                "Outlook good.",
                "Yes.",
                "Signs point to yes.",
                "Reply hazy, try again.",
                "Ask again later.",
                "Better not tell you now.",
                "Cannot predict now.",
                "Concentrate and ask again.",
                "Don't count on it.",
                "My reply is no.",
                "My sources say no.",
                "Outlook not so good.",
                "Very doubtful."]
        answer = random.choice(responses)
        await ctx.send(f':8ball:{answer}')


def setup(bot):
    bot.add_cog(Games(bot))
