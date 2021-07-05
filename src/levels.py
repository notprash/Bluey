from operator import truediv
import discord
from discord.ext import commands
import sqlite3 as sql
import math
import random
from PIL import Image, ImageDraw, ImageOps, ImageFont
import os
from utilities import read_database, update_database, has_admin_permissions

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
            self.make_image(xp, final_xp, rank, level, name, self.calculate_xp(level))

        file = discord.File("rank.png")
        await ctx.send(file=file)
        
        # remove files
        os.remove('output.png')
        os.remove('1.jpg')
        os.remove('avatar.jpg')
        os.remove('rank.png')
       

    @commands.command()
    async def top(self, ctx ):
        with sql.connect("db.sqlite3") as db:
            cursor = db.execute(f'SELECT user, xp, level FROM Levels WHERE Guild = {ctx.guild.id} ORDER BY xp DESC ')
            data = cursor.fetchall()
            i = 0
            embed = discord.Embed().set_author(name="Leaderboard", icon_url=self.client.user.avatar_url)
            embed.set_thumbnail(url=ctx.guild.icon_url)
            for row in data:
                userid, xp, level = row
                user = await self.client.fetch_user(userid)
                value = f"    XP: `{xp}`\n     Level: `{level}`"
                if i == 0:
                    user = f"<:infinity_winner:855083626647650345>  <a:arrow:855079459656564767> {user}"
                    embed.add_field(name=user, value=value, inline=False)
                    i += 1
                    continue

                user = f"#{i + 1} <a:arrow:855079459656564767>  {user}"
                embed.add_field(name=user, value=value, inline=False)
                i += 1

        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setlvl(self, ctx, member: discord.Member, lvl: int):
        guildid, userid, xp, level = self.find_or_insert_user(member)
        
        xp = self.calculate_xp(lvl)
        level = lvl
        with sql.connect("db.sqlite3") as db:
            db.execute(f'Update Levels set xp = {xp}, level = {level} WHERE Guild = {guildid} and user = {userid}')
            db.commit()


        color = discord.Color.green()
        embed = discord.Embed(description=f"Level set {level} for {member.mention}", color=color)
        await ctx.send(embed=embed)

    def check_if_level_up_role(self, level, guildid):
        with sql.connect('db.sqlite3') as db:
            try:
                cursor = db.execute(f"SELECT * FROM Levelups WHERE guildId = {guildid}")
            except:
                return False
            values = cursor.fetchone()
            if values[2] == level:
                return values[1] 

        return False


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return


        result = self.find_or_insert_user(message.author)
        
        guildid, userid, xp, level = result
        
        # Value 0 == No level up channel
        levelup_channel = read_database(message.guild.id)[6]

        xp += random.randint(5, 15)

        if self.calculate_lvl(xp) > level and levelup_channel == 0:
            level += 1
            
            value = self.check_if_level_up_role(level, message.guild.id)

            if value != False:
                role = discord.utils.get(message.guild.roles, id=value)
                await message.author.add_roles(role)
            await message.channel.send(f"Congrats {message.author.mention}, You have reached level {level} <a:wumpuscongrats:857438443441618954>")
        elif self.calculate_lvl(xp) > level:
            channel = await self.client.fetch_channel(levelup_channel)
            level += 1
            value = self.check_if_level_up_role(level, message.guild.id)
            if value != False:
                role = message.guild.get_role(value)
                await message.author.add_roles(role)
            await channel.send(f"Congrats {message.author.mention}, You have reached level {level} <a:wumpuscongrats:857438443441618954>")



        with sql.connect('db.sqlite3') as db:
            db.execute(f'Update Levels set xp = {xp}, level = {level} WHERE Guild = {guildid} and user = {userid}')
            db.commit()


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def levelup(self, ctx, type, channel: discord.TextChannel=None):
        if type == 'channel':
            update_database("Settings", 'levelup', channel.id, 'guildId', ctx.guild.id)
            embed = discord.Embed(description=f"Now {channel.mention} will recieve level up notifications", color=discord.Color.green())
            await ctx.send(embed=embed)

        elif type == "default":
            update_database("Settings", 'levelup', 0, 'guildId', ctx.guild.id)
            await ctx.send("✅ Restored defaults")


    @commands.command()
    @has_admin_permissions()
    async def giverole(self, ctx, level: int, role: discord.Role):
        with sql.connect('db.sqlite3') as db:
            try:
                db.execute("CREATE TABLE Levelups (guildId int, roleId int PRIMARY KEY, level int)")
            except:
                print("Table Exists")


            cursor = db.execute(f"INSERT INTO Levelups VALUES(?, ?, ?)", (ctx.guild.id, role.id, level))
            db.commit()

def setup(bot):
    bot.add_cog(Levels(bot))