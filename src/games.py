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
            try:
                number = int(msg.content)
            except:
                return
            return msg.author == ctx.author and msg.channel == ctx.channel and int(number) in list(range(1, 11))

        msg = await self.client.wait_for("message", check=check)
        i = 0
        while i < 3:
            try:
                number = int(msg.content)
            except:
                await ctx.send("<:error:870673057495261184> Choose a number between 1 to 10!")
                continue
            if number == num:
                return await ctx.send("<a:wumpuscongrats:857438443441618954> Kudos! You guessed the number right.")
            else:
                if i + 1 == 3:
                    return await ctx.send(f"😕 Sorry! It was {num}")
                i += 1
                await ctx.send(f'Try Again, only {3 - i} attempts left')
                msg = await self.client.wait_for("message", check=check)

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
