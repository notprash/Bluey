from operator import truediv
import discord
from discord.ext import commands
import sqlite3 as sql
import math
import random
from PIL import Image, ImageDraw, ImageOps, ImageFont
import os
from utilities import read_database, update_database, has_admin_permissions, help_embed


class Levels(commands.Cog):
    def __init__(self, bot):
        self.client = bot

    def enabled(self, guild):
        return bool(read_database(guild)[9])

    async def disabled_msg(self, ctx):
        embed = discord.Embed(
            description="Levels is disabled. Please enable it to use this", color=discord.Color.red())
        return await ctx.send(embed=embed)

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
                cursor.execute("INSERT INTO Levels VALUES(?, ?, ?, ?)",
                               (member.guild.id, member.id, 0, 0))
                cursor.commit()

        return result

    def check_if_level_up_role(self, level, guildid):
        if level == None:
            return
        with sql.connect('db.sqlite3') as db:
            try:
                cursor = db.execute(
                    f"SELECT * FROM Levelups WHERE guildId = {guildid}")
            except:
                return False
            values = cursor.fetchone()
            if values == None:
                return False
            if values[2] == level:
                return values[1]

        return False

    def check_if_xp_blocked(self, channel: discord.TextChannel, guild):
        with sql.connect("db.sqlite3") as db:
            try: 
                values = db.execute(
                    f"SELECT channel FROM Noxp WHERE guildId = {guild.id}").fetchall()
            except:
                return False
            for value in values:
                if value[0] == channel.id:
                    return True

        return False

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

    def get_colors(self, image_file, numcolors=10, resize=150):
        # Resize image to speed up processing
        img = Image.open(image_file)
        img = img.copy()
        img.thumbnail((resize, resize))

        # Reduce to palette
        paletted = img.convert('P', palette=Image.ADAPTIVE, colors=numcolors)

        # Find dominant colors
        palette = paletted.getpalette()
        color_counts = sorted(paletted.getcolors(), reverse=True)
        colors = list()
        for i in range(numcolors):
            palette_index = color_counts[i][1]
            dominant_color = palette[palette_index*3:palette_index*3+3]
            colors.append(tuple(dominant_color))

        return colors

    def add_corners(self, im, rad):
        circle = Image.new('L', (rad * 2, rad * 2), 0)
        draw = ImageDraw.Draw(circle)
        draw.ellipse((0, 0, rad * 2, rad * 2), fill=255)
        alpha = Image.new('L', im.size, 255)
        w, h = im.size
        alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
        alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
        alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
        alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)),
                    (w - rad, h - rad))
        im.putalpha(alpha)
        return im

    def make_image(self, xp, final_xp, rank, level, name):

        # load background image
        background = Image.new("RGBA", (593, 316), '#535353')

        # load rectangle(progress bar)
        draw = ImageDraw.Draw(background)

        bar_x1 = 182
        bar_y1 = 240
        bar_x2 = 400
        bar_y2 = 270
        circle_size = bar_y2 - bar_y1
        draw.ellipse((bar_x1 - circle_size//2, bar_y1, bar_x1 +
                     circle_size//2, bar_y1 + circle_size), fill="#9b9e9c")

        draw.ellipse((bar_x2 - circle_size//2, bar_y1, bar_x2 +
                     circle_size//2, bar_y2), fill="#9b9e9c")
        draw.rectangle([bar_x1, bar_y1, bar_x2, bar_y2], fill="#9b9e9c")

        percent = round((xp/final_xp) * 100)
        size_progress_bar = int((bar_x2 - bar_x1) * percent/100)
        bar_x2 = bar_x1 + size_progress_bar
        draw.ellipse((bar_x1 - circle_size//2, bar_y1, bar_x1 +
                     circle_size//2, bar_y1 + circle_size), fill="#00a8f3")

        draw.ellipse((bar_x2 - circle_size//2, bar_y1, bar_x2 +
                     circle_size//2, bar_y2), fill="#00a8f3")
        draw.rectangle([bar_x1, bar_y1, bar_x2, bar_y2], fill='#00a8f3')

        self.create_circular_image('avatar.jpg', (177, 176))
        img = Image.open('output.png').convert('RGBA')
        colors = self.get_colors('output.png')
        background.paste(img, (15, 75), img)

        font2 = ImageFont.truetype('fonts/Font.ttf', 32)
        font3 = ImageFont.truetype('fonts/Font.ttf', 40)
        font4 = ImageFont.truetype("fonts/Font.ttf", 25)

        draw.text((218, 90), f"LEVEL\n\n {level}",
                  font=font2, fill=(255, 255, 255))
        draw.text((347, 91), f"RANK\n\n# {rank}",
                  font=font2, fill=(255, 255, 255))
        draw.text((228, 246), f"{xp}/{final_xp}",
                  font=font4, fill=(255, 255, 255))

        W, H = 593, 316
        w, h = draw.textsize(name, font=font3)
        draw.text(((W-w)/2 + 6, 20), name, font=font3, fill=(255, 255, 255))

        self.create_circular_image('1.jpg', (80, 80))
        img = Image.open('output.png').convert('RGBA')
        draw.rectangle((464, 58, 467, 257), fill='#48ebfa')
        draw.rectangle((468, 118, 489, 121), fill='#48ebfa')
        background.paste(img, (489, 79), img)

        half = Image.new("RGBA", (593, 7), colors[2])
        background.paste(half, (0, H - 7))

        # save image
        round_corners = self.add_corners(background, 30)
        round_corners.save("rank.png")

    @commands.command()
    async def rank(self, ctx, member: discord.Member = None):
        if not self.enabled(ctx.guild.id):
            return await self.disabled_msg(ctx)
        member = member or ctx.author
        await member.avatar_url.save('avatar.jpg')
        await member.guild.icon_url.save('1.jpg')
        with sql.connect('db.sqlite3') as db:
            guild_id, user_id, xp, level = self.find_or_insert_user(member)
            rank = db.execute(
                f"Select Count(*) from Levels where xp > ? and Guild=?", (xp, guild_id))
            rank = rank.fetchone()[0] + 1
            final_xp = self.calculate_xp(level + 1)
            name = f"{member.name}#{member.discriminator}"
            self.make_image(xp, final_xp, rank, level, name)

        file = discord.File("rank.png")
        await ctx.send(file=file)

        # remove files
        os.remove('output.png')
        os.remove('1.jpg')
        os.remove('avatar.jpg')
        os.remove('rank.png')

    @commands.command()
    async def top(self, ctx):
        if not self.enabled(ctx.guild.id):
            return await self.disabled_msg(ctx)
        with sql.connect("db.sqlite3") as db:
            cursor = db.execute(
                f'SELECT user, xp, level FROM Levels WHERE Guild = {ctx.guild.id} ORDER BY xp DESC ')
            data = cursor.fetchall()
            i = 0
            embed = discord.Embed().set_author(name="Leaderboard",
                                               icon_url=self.client.user.avatar_url)
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
    async def setlvl(self, ctx, member: discord.Member = None, lvl: int = None):
        arg = 0;
        if not self.enabled(ctx.guild.id):
            return await self.disabled_msg(ctx)
        if member == None or lvl == None:
            arg = None
        if await help_embed(ctx.channel, "setlvl <@member> <lvl>", arg):
            return
        guildid, userid, xp, level = self.find_or_insert_user(member)

        xp = self.calculate_xp(lvl)
        level = lvl
        with sql.connect("db.sqlite3") as db:
            db.execute(
                f'Update Levels set xp = {xp}, level = {level} WHERE Guild = {guildid} and user = {userid}')
            db.commit()

        color = discord.Color.green()
        embed = discord.Embed(
            description=f"Level set {level} for {member.mention}", color=color)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def levelup(self, ctx, type=None, channel: discord.TextChannel = None):
        prefix = read_database(ctx.guild.id)[8]
        if not self.enabled(ctx.guild.id):
            return await self.disabled_msg(ctx)
        if await help_embed(ctx.channel, f"levelup channel <#channel>\n{prefix}levelup default", type):
            return
        if type == 'channel':
            update_database("Settings", 'levelup', channel.id,
                            'guildId', ctx.guild.id)
            embed = discord.Embed(
                description=f"Now {channel.mention} will recieve level up notifications", color=discord.Color.green())
            await ctx.send(embed=embed)

        elif type == "default":
            update_database("Settings", 'levelup', 0, 'guildId', ctx.guild.id)
            await ctx.send("✅ Restored defaults")

    @commands.command()
    @commands.has_permissions(kick_members=True, ban_members=True)
    async def xpblock(self, ctx, member: discord.Member = None):
        if not self.enabled(ctx.guild.id):
            return await self.disabled_msg(ctx)
        if await help_embed(ctx.channel, "xpblock <@member>", member):
            return
        role = discord.utils.get(ctx.guild.roles, name="[xp blocked]")
        if role == None:
            role = await ctx.guild.create_role(name="[xp blocked]")
            await ctx.send(f"Xp blocked {member.mention}")
            return await member.add_roles(role)

        await ctx.send(f"<:tickmark:867411301277892618> Xp blocked {member.mention}")
        return await member.add_roles(role)
        # member.add_roles(roles=)

    @commands.command()
    @has_admin_permissions()
    async def noxpchannel(self, ctx, type=None, channel: discord.TextChannel = None):
        prefix = read_database(ctx.guild.id)[8]
        if not self.enabled(ctx.guild.id):
            return await self.disabled_msg(ctx)
        arg = 0
        if type == None or channel == None:
            arg = None
        if await help_embed(ctx.channel, f"noxpchannel add <#channel>\n{prefix}noxpchannel remove <#channel>", arg):
            return
        with sql.connect("db.sqlite3") as db:
            try:
                db.execute(
                    "CREATE TABLE Noxp (guildId int, channel int PRIMARY KEY)")
                db.commit()
            except:
                pass

            if type == 'add':
                try:
                    db.execute("INSERT INTO Noxp VALUES(?, ?)",
                               (ctx.guild.id, channel.id))
                    db.commit()
                    await ctx.send(f"✅ {channel.mention} is now xp blocked channel")
                except:
                    await ctx.send(f"🔴 {channel.mention} already added")

            elif type == 'remove':
                try:
                    db.execute(
                        f"DELETE FROM Noxp WHERE guildId = {ctx.guild.id} AND channel = {channel.id}")
                    db.commit()
                    await ctx.send(f"✅ {channel.mention} is not xp blocked anymore")
                except:
                    await ctx.send(f"🔴 {channel.mention} channel is not added")

    @commands.command()
    @has_admin_permissions()
    async def giverole(self, ctx, type=None, *args):
        # get prefix
        prefix = read_database(ctx.guild.id)[8]
        if not self.enabled(ctx.guild.id):
            return await self.disabled_msg(ctx)
        if await help_embed(ctx.channel, f"giverole add <lvl> <@role>\n{prefix}giverole remove <@role>\n{prefix}giverole list", type):
            return
        with sql.connect('db.sqlite3') as db:
            try:
                db.execute(
                    "CREATE TABLE Levelups (guildId int, roleId int PRIMARY KEY, level int)")
            except:
                print("Table Exists")

            if type == 'add' and args != []:
                try:
                    role = ctx.guild.get_role(int(args[1][3:-1]))
                    level = int(args[0])
                    cursor = db.execute(
                        f"INSERT INTO Levelups VALUES(?, ?, ?)", (ctx.guild.id, role.id, level))
                    db.commit()
                    await ctx.send(f"<:tickmark:867411301277892618> User will recieve {role.mention} at level {level}")
                except:
                    await ctx.send("Role already added")

            elif type == 'remove' and args != []:
                role = ctx.guild.get_role(int(args[0][3:-1]))
                try:
                    db.execute(
                        "DELETE FROM Levelups WHERE guildId = ? AND roleId = ?", (ctx.guild.id, role.id))
                    db.commit()
                    await ctx.send("✅ Role removed")
                except:
                    await ctx.send('🔴 Role does not exist')

            elif type == 'list':
                values = db.execute(
                    f"SELECT roleId, level FROM Levelups WHERE guildId = {ctx.guild.id}").fetchall()
                description = ""
                for value in values:
                    roleid, level = value
                    role = discord.utils.get(ctx.guild.roles, id=roleid)
                    description += f"**{level}** -- {role.mention} \n\n"

                embed = discord.Embed(description=description)
                embed.set_author(name="Levelup Roles",
                                 icon_url=ctx.guild.icon_url)
                await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if not self.enabled(message.guild.id):
            return
        role = discord.utils.get(message.guild.roles, name='[xp blocked]')
        if message.author.bot or role in message.author.roles:
            return

        if self.check_if_xp_blocked(message.channel, message.guild):
            return

        prefix = read_database(message.guild.id)[8]
        if message.content.startswith(prefix):
            return

        result = self.find_or_insert_user(message.author)

        guildid, userid, xp, level = result

        # Value 0 == No level up channel
        levelup_channel = read_database(message.guild.id)[6]

        xp += random.randint(5, 70)

        if self.calculate_lvl(xp) > level and levelup_channel == 0:
            level += 1
            xp = 0
            value = self.check_if_level_up_role(level, message.guild.id)

            if value != False:
                role = discord.utils.get(message.guild.roles, id=value)
                await message.author.add_roles(role)
            await message.channel.send(f"Congrats {message.author.mention}, You have reached level {level} <a:wumpuscongrats:857438443441618954>")
        elif self.calculate_lvl(xp) > level:
            channel = await self.client.fetch_channel(levelup_channel)
            level += 1
            xp = 0
            value = self.check_if_level_up_role(level, message.guild.id)
            if value != False:
                role = message.guild.get_role(value)
                await message.author.add_roles(role)
            await channel.send(f"Congrats {message.author.mention}, You have reached level {level} <a:wumpuscongrats:857438443441618954>")

        with sql.connect('db.sqlite3') as db:
            db.execute(
                f'Update Levels set xp = {xp}, level = {level} WHERE Guild = {guildid} and user = {userid}')
            db.commit()


def setup(bot):
    bot.add_cog(Levels(bot))
