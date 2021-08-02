from os import read
import sqlite3
from discord.ext import commands
from youtube_dl import YoutubeDL
import discord
from utilities import help_embed, read_database
import wavelink

class QueueIsEmpty(commands.CommandError):
    pass

class Queue:
    def __init__(self):
        self.__queue = []
        self.position = 0

    def empty(self):
        return not self.__queue
    def first_track(self):
        return self.__queue[0]

    def add(self, track):
        self.__queue.append(track)


    @property
    def current_track(self):
        if self.empty():
            raise QueueIsEmpty

        if self.position < len(self.__queue):
            return self.__queue[self.position]
            
            

    def get_next_track(self):
        if self.empty():
            raise QueueIsEmpty

        if self.position + 1 < len(self.__queue):
            self.position += 1
            return self.__queue[self.position]


    @property
    def clear(self):
        self.__queue = []
        self.position = 0

    @property
    def upcoming(self):
        return self.__queue[self.position + 1:]

    
    def previous(self, set=False):
        if set:
            self.position -= 2
            return self.__queue[self.position]
        return self.__queue[self.position - 1]

    @property
    def whole_queue(self):
        return self.__queue





class Player(wavelink.Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = Queue()


    async def add_tracks(self, ctx, tracks):
        self.queue.add(tracks)

        await ctx.send(f"Added **{tracks.title}** to the Queue")

        if not self.is_playing and not self.queue.empty():
            await self.start_playback()

    async def start_playback(self):
        await self.play(self.queue.current_track)

    async def advance(self):
        next_track = self.queue.get_next_track()
        if not next_track:
            return
        await self.play(next_track)


    async def player_disconnect(self):
        try:
            await self.destroy()
        except:
            pass



class Music(commands.Cog, wavelink.WavelinkMixin):
    def __init__(self, bot):
        self.client = bot
        self.wavelink = wavelink.Client(bot=bot)
        self.client.loop.create_task(self.start_nodes())

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not member.bot and after.channel is None:
            if not [m for m in before.channel.members if not m.bot]:
                await self.get_player(member.guild).player_disconnect()

    @wavelink.WavelinkMixin.listener()
    async def on_node_ready(self, node: wavelink.Node):
        print(f"{node.identifier} is ready")

    @wavelink.WavelinkMixin.listener('on_track_end')
    async def on_player_stop(self, node, payload):
        try:
            await payload.player.advance()
        except:
            pass 

    
    async def start_nodes(self):
        await self.client.wait_until_ready()

        await self.wavelink.initiate_node(host='127.0.0.1',
                                              port=2333,
                                              rest_uri='http://127.0.0.1:2333',
                                              password='youshallnotpass',
                                              identifier='MAIN',
                                              region='us_central')
    
    def get_player(self, ctx):
        if isinstance(ctx, commands.Context):
            return self.wavelink.get_player(ctx.guild.id, cls=Player, context=ctx)

        elif isinstance(ctx, discord.Guild):
            return self.wavelink.get_player(ctx.id, cls=Player, context=ctx)


    @commands.command()
    async def skip(self, ctx):
        player = self.get_player(ctx) 
        previous = player.queue.current_track
        await player.advance()
        await ctx.send(f"Skipped {previous}")


    @commands.command(name='play', description="Plays a song", aliases=['p'])
    async def play(self, ctx, *song_name):
        if len(song_name) == 0:
            return
        song_name = ' '.join(song_name)
        tracks = await self.wavelink.get_tracks(f'ytsearch: {song_name}')
        player = self.get_player(ctx)
        try:
            channel = ctx.author.voice.channel
        except Exception:
            await ctx.send("<:error:870673057495261184> Connect to a voice channel!")
            return

        if not player.is_connected:
            await player.connect(channel.id)

        await player.add_tracks(ctx, tracks[0])


    @commands.command(name='queue', description='Return in the songs in queue', aliases=['q'])
    async def queue(self, ctx):
        player = self.get_player(ctx)
        upcoming = player.queue.upcoming
        current_track = player.queue.current_track
        current_track_title = '%.41s' % current_track + '...'
        description = ''
        for track in upcoming:
            track_title = track.title
            if len(track_title) > 41:
                track_title = '%.41s' % track + '..'
            description += f"{track_title} **({track.duration // 60000} min)**\n"
        embed = discord.Embed(color=ctx.author.color, description=description).set_author(name=current_track_title, icon_url=self.client.user.avatar_url)
        embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=current_track.thumb)


        await ctx.send(embed=embed)



    @commands.command(name='stop', description="Disconnects the bot and clears the queue", aliases=['destroy'])
    async def stop(self, ctx):
        player = self.get_player(ctx)
        await player.player_disconnect()
        player.queue.clear

    
    @commands.command(name='volume', description='Changes the volume of the player', aliases=['vol'])
    async def volume(self, ctx, value=None): 
        prefix = read_database(ctx.guild.id)[8]
        try:
            value = int(value)
        except:
            return await ctx.send("😮‍💨 The volume value must be integer")

        player = self.get_player(ctx)
        player_volume = player.volume
        if value == player_volume:
            return await ctx.send(f"🙄 Volume is already set to {value}")

        if not value:
            embed = discord.Embed(title="Volume info", description=f'Current player volume is {player_volume}')
            embed.add_field(name='Help', value=f'`{prefix}volume <volume>`')
            embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            return await ctx.send(embed=embed)

        if value > 100:
            return await ctx.send("The volume is too high")
        elif value < 0:
            return await ctx.send("The volume is too low")


        await player.set_volume(value)
        await ctx.send(f"🔊 volume set to *{value}*")

    @commands.command(name='back', description="Moves back to the previous track", aliases=['prev', 'previous'])
    async def back(self, ctx):
        player = self.get_player(ctx)
        song = player.queue.previous(set=True)
        await player.stop()
        await ctx.send(f"◀️  Moving back to **{song}**")

    @commands.command(name='repeat', description='Replays the current track', aliases=['replay'])
    async def repeat(self, ctx):
        player = self.get_player(ctx)
        song_name = player.queue.previous()
        await player.start_playback()
        await ctx.send(f"🔁 Replaying **{song_name}**")


    
    @commands.command(name='pause', description='Pauses the track')
    async def pause(self, ctx):
        prefix = read_database(ctx.guild.id)[8]
        player = self.get_player(ctx)
        if player.is_paused:
            return await ctx.send(f"The player is already paused. Try using `{prefix}resume` for resuming the track")

        await player.set_pause(True)
        current_track = player.queue.current_track
        await ctx.send(f"Paused **{current_track}** ")

    @commands.command(name='resume', description='Resumes the track', aliases=['unpause'])
    async def resume(self, ctx):
        player = self.get_player(ctx)
        if not player.is_paused:
            return await ctx.send("The player is already playing")

        await player.set_pause(False)
        current_track = player.queue.current_track
        await ctx.send(f"Resumed **{current_track}** ")



    # Likes songs
    @commands.command(name='like', description='Likes the current song', aliases=['fav'])
    async def like(self, ctx):
        with sqlite3.connect('db.sqlite3') as db:
            try:
                db.execute("CREATE TABLE Liked (user int, songname TEXT)")
                db.commit()
            except:
                pass

            player = self.get_player(ctx)
            current_track = player.queue.current_track.title
            song = db.execute("SELECT songname FROM Liked WHERE user = ? AND songname = ?", (ctx.author.id, current_track)).fetchone()
            if song != None:
                embed = discord.Embed(description='Song already added to your liked songs', color=discord.Color.red())
                return await ctx.send(embed=embed)

            db.execute("INSERT INTO Liked VALUES(?, ?)", (ctx.author.id, current_track))
            db.commit()
            embed = discord.Embed(description=f"❤️ Added {current_track} to your liked songs", color=discord.Color.green())
            await ctx.send(embed=embed)


    @commands.command(name='likedsongs', description='Lists the liked songs', aliases=['liked', 'favsongs'])
    async def likedsongs(self, ctx, member: discord.Member=None):
        member = member or ctx.author

        with sqlite3.connect('db.sqlite3') as db:
            songs = db.execute(f'SELECT songname FROM Liked WHERE user = {member.id}').fetchall()
            description = ""
            if songs == []:
                embed = discord.Embed(description=f"{member} does not have any liked songs", color=discord.Color.red())
                return await ctx.send(embed=embed)
                

            i = 0

            for song in songs:
                i += 1
                song = song[0]
                description += f"{i}. {song}\n"

            embed = discord.Embed(description=description, color=ctx.author.color)
            embed.set_author(name=f"{member}'s Liked Songs", icon_url=member.avatar_url)
            embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)


    @commands.command(name='bassboost', description='Increases the bass sound')
    async def bassboost(self, ctx, args=None):
        player = self.get_player(ctx)
        eq = wavelink.Equalizer.boost()
        song = player.queue.current_track
        if args == 'reset':
            eq = wavelink.Equalizer.flat()
            embed = discord.Embed(description="Removed all the effects on the player", color=discord.Color.green())
            await ctx.send(embed=embed)
            return await player.set_eq(eq)
        await player.set_eq(eq)
        await ctx.send(f"Bassboosted **{song}**")

        

def setup(bot):
    bot.add_cog(Music(bot))
