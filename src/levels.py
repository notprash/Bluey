import discord
from discord.ext import commands
import sqlite3 as sql
import math
import random
from PIL import Image, ImageDraw, ImageOps, ImageFont
import os

class Levels(commands.Cog):
    def __init__(self, bot):
        self.client = bot

    def find_or_insert_user(self, member: discord.Member):
        with sql.connect('db.sqlite3') as cursor:
            try: 
                command = "CREATE TABLE Levels (Guild int, user int, xp int, level int)"
                cursor.execute(command)
                cursor.commit()
            except:
                pass

            command = f"SELECT * FROM Levels WHERE user = {member.id} AND Guild = {member.guild.id}"
            result = cursor.execute(command)
            result = result.fetchone()

            if result == None:
                result = (member.guild.id, member.id, 0, 0)
                cursor.execute("INSERT INTO Levels VALUES(?, ?, ?, ?)", (member.guild.id, member.id, 0, 0))
                cursor.commit()

        return result



    def calculate_lvl(self, xp):
        lvl = round(0.1 * math.sqrt(xp))
        return lvl

    def calculate_xp(self, lvl):
        xp = (100 * (lvl ** 2))
        return xp

    # Create Circular Image
    def create_circular_image(self, image_file, size: tuple):
        mask = Image.new('L', size, 0)
        drawmask = ImageDraw.Draw(mask) 
        drawmask.ellipse((0, 0) + size, fill=255)

        im = Image.open(image_file).convert("RGBA")

        output = ImageOps.fit(im, mask.size, centering=(0.5, 0.5))
        output.putalpha(mask)
        output.save('output.png')

    def add_corners(self, im, rad):
        circle = Image.new('L', (rad * 2, rad * 2), 0)
        draw = ImageDraw.Draw(circle)
        draw.ellipse((0, 0, rad * 2, rad * 2), fill=255)
        alpha = Image.new('L', im.size, 255)
        w, h = im.size
        alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
        alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
        alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
        alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
        im.putalpha(alpha)
        return im

    def make_image(self, xp, final_xp, rank, level, name, start_xp):
        # load background image
        background = Image.new("RGBA", (700, 300), '#1a1a1a')

        # load rectangle(progress bar)
        draw = ImageDraw.Draw(background)

        bar_x1 = 0
        bar_y1 = 295
        bar_x2 = 700
        bar_y2 = 300
        draw.rectangle([bar_x1, bar_y1, bar_x2, bar_y2], fill="#000000")


        percent = round((xp/final_xp) * 100)
        size_progress_bar = int((bar_x2 - bar_x1)  * percent/100)  
        bar_x2 = bar_x1 + size_progress_bar

        draw.rectangle([bar_x1, bar_y1, bar_x2, bar_y2], fill="#11ebf2")


        self.create_circular_image('avatar.jpg', (170, 170))
        img = Image.open('output.png').convert('RGBA')
        background.paste(img, (10, 50), img)

        font = ImageFont.truetype('Font.ttf', 28)
        font2 = ImageFont.truetype('Font.ttf', 23)
        font3 = ImageFont.truetype('Font.ttf', 30)

        draw.text((360, 100), "LVL", font=font, fill='#58e1e8')
        draw.text((360, 160), "#" + str(level), font=font2, fill=(255, 255, 255))
        draw.text((250, 100), "RANK", font=font, fill='#58e1e8')
        draw.text((250, 160), "#" + str(rank), font=font2, fill=(255, 255, 255))
        draw.text((300, 30), name, font=font3, fill='#7373d1')



        self.create_circular_image('1.jpg', (100, 100))
        img = Image.open('output.png').convert('RGBA')
        draw.line((470, 75, 470, 250), fill=(255, 255, 255))
        draw.text((500, 200), f"{xp}/{final_xp}", font=font2, fill='#7373d1')
        background.paste(img, (500, 80), img)


        # save image
        round_corners = self.add_corners(background, 50)
        round_corners.save("rank.png")


    @commands.command()
    async def rank(self, ctx, member : discord.Member=None):
        member = member or ctx.author
        await member.avatar_url.save('avatar.jpg')
        await member.guild.icon_url.save('1.jpg')
        with sql.connect('db.sqlite3') as db:
            guild_id, user_id, xp, level = self.find_or_insert_user(member)
            rank = db.execute(f"Select Count(*) from Levels where xp > ? and Guild=?", (xp, guild_id))
            rank = rank.fetchone()[0] + 1
            final_xp = self.calculate_xp(level + 1)
            name = f"{member.name}#{member.discriminator}"
            self.make_image(xp, final_xp, rank, level, name, self.calculate_lvl(level))

        file = discord.File("rank.png")
        await ctx.send(file=file)
        
        # remove files
        os.remove('output.png')
        os.remove('1.jpg')
        os.remove('avatar.jpg')
        os.remove('rank.png')
       




    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return


        result = self.find_or_insert_user(message.author)
        
        guildid, userid, xp, level = result

        xp += random.randint(5, 40)

        if self.calculate_lvl(xp) > level:
            level += 1
            await message.channel.send(f"Congrats {message.author.mention}, You have reached level {level} 🥳")

        with sql.connect('db.sqlite3') as db:
            db.execute(f'Update Levels set xp = {xp}, level = {level} WHERE Guild = {guildid} and user = {userid}')
            db.commit()

def setup(bot):
    bot.add_cog(Levels(bot))