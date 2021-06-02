from discord.ext import commands
from youtube_dl import YoutubeDL
import discord


class Music(commands.Cog):
    def __init__(self, bot):
        self.client = bot
        self.music_queue = []
        self.is_playing = False
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        self.vc = ""
        self.current_song = None


    def search_song(self, song_name):
        with YoutubeDL() as ydl:
            try: 
                info = ydl.extract_info("ytsearch:%s" % song_name, download=False)['entries'][0]
            except Exception: 
                return False

        print(info)

        return {'source': info['formats'][0]['url'], 'title': info['title']}
        
    
    async def play_music(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            m_url = self.music_queue[0][0]['source']
            
            #try to connect to voice channel if you are not already connected

            if self.vc == "" or not self.vc.is_connected() or self.vc == None:
                self.vc = await self.music_queue[0][1].connect()
            else:
                await self.vc.move_to(self.music_queue[0][1])
            
            print(self.music_queue)
            #remove the first element as you are currently playing it
            self.current_song = self.music_queue.pop(0)
            self.current_song = self.current_song[0]['title']

            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            self.is_playing = False


    def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            #get the first url
            m_url = self.music_queue[0][0]['source']

            #remove the first element as you are currently playing it
            self.music_queue.pop(0)

            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            self.is_playing = False
        



    @commands.command()
    async def play(self, ctx, *song_name):
        query = " ".join(song_name)
        
        try: 
            voice_channel = ctx.author.voice.channel
        except Exception:
            voice_channel = None
        if voice_channel is None:
            #you need to be connected so that the bot knows where to go
            await ctx.send("🚫 Connect to a voice channel!")
        else:
            song = self.search_song(query)
            await ctx.send(f"🎵 **{song['title']}** added to **PandaQueue**")
            self.music_queue.append([song, voice_channel, ctx.author])
                
            if self.is_playing == False:
                await self.play_music()


    @commands.command()
    async def skip(self, ctx):
        if self.vc != "" and self.vc:
            self.vc.stop()
            await self.play_music()

    @commands.command()
    async def disconnect(self, ctx):
        for x in self.client.voice_clients:
            if(x.guild == ctx.message.guild):
                return await x.disconnect()

        return await ctx.send("I am not connected to any voice channel on this server!")


    @commands.command()
    async def queue(self, ctx):
        str = ""
        for song in self.music_queue:
            print(self.music_queue)
            song_name = f"🎵 **{song[0]['title']} - {song[2].mention}**\n"
            str += song_name
        embed = discord.Embed(title=f"Panda Queue | {len(self.music_queue)} songs left", description=str, color=ctx.author.color)
        await ctx.send(f"**{self.current_song}**", embed=embed)







def setup(bot):
    bot.add_cog(Music(bot))
