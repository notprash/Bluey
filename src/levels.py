import discord
from discord.ext import commands
import sqlite3 as sql
import math
import random

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