import asyncio
import discord
import youtube_dl
from discord.ext import commands
from discord import ClientException
from discord import app_commands
import pafy


class Music(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.song_queue = {}
        self.yt_dl_opts = {
            'format': '140',
            'noplaylist': True,
            'outtmpl': 'music',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '64',
            }],
        }
        self.ytdl = youtube_dl.YoutubeDL(self.yt_dl_opts)
        self.ffmpeg_options = {'options': "-vn"}
        self.voice_clients = {}

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.client.guilds:
            self.song_queue[guild.id] = []

    @commands.command()
    async def stop(self, ctx):
        if ctx.voice_client is not None:
            return await ctx.voice_client.disconnect()
        else:
            return await ctx.send("I am not connected to a voice channel")

    async def check_queue(self, ctx):
        if len(self.song_queue[str(ctx.guild.id)]) > 0:
            ctx.voice_client.stop()
            await self.play_song(ctx, self.song_queue[str(ctx.guild.id)][0])
            self.song_queue[str(ctx.guild.id)].pop(0)

    async def search_song(self, amount, song, get_url=False):
        info = await self.client.loop.run_in_executor(None, lambda: youtube_dl.YoutubeDL({"format": "bestaudio", "quiet": True}).extract_info(f"ytsearch{amount}:{song}", download=False, ie_key="YoutubeSearch"))
        if len(info["entries"]) == 0:
            return None

        return [entry["webpage_url"] for entry in info["entries"]] if get_url else info

    async def play_song(self, ctx, song):
        url = pafy.new(song).getbestaudio().url
        ctx.voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(
            url)), after=lambda error: self.client.loop.create_task(self.check_queue(ctx)))
        ctx.voice_client.source.volume = 0.5

    @commands.command()
    async def search(self, ctx, *, song=None):
        if song is None:
            return await ctx.send("Please include a song to search for")
        await ctx.send("Searching for song, this may take a few seconds...")

        info = await self.search_song(5, song)

        embed = discord.Embed(
            title=f"Results for '{song}':", description="You can use these URL's to play the song\n", colour=discord.Colour.blue())

        amount = 0
        for entry in info["entries"]:
            embed.description += f"[{entry['title']}]({entry['webpage_url']})\n"
            amount += 1

        embed.set_footer(text=f"Displaying the first {amount} results.")
        await ctx.send(embed=embed)

    @commands.command()
    async def play(self, ctx, *, song=None):

        print(song)
        if song is None:
            return await ctx.send("You must include a song to play.")

        if ctx.voice_client is None:
            return await ctx.send("I must be in a voice channel to play a song.")

        if not ("youtube.com/watch?" in song or "https://youtu.be/" in song):

            await ctx.send("Searching for a song, this may take a few seconds...")

            result = await self.search_song(1, song, get_url=True)

            if result is None:
                return await ctx.send("Sorry, I couldn't find the song you asked for. Try using my search command to find the song you want.")

            song = result[0]

        if ctx.voice_client.source is not None:
            # create queue
            try:
                queue_len = len(self.song_queue[str(ctx.guild.id)])
            except KeyError:
                self.song_queue[str(ctx.guild.id)] = []
                queue_len = 0

            if queue_len < 10:
                self.song_queue[str(ctx.guild.id)].append(song)
                return await ctx.send(f"Song added to the queue at position {queue_len+1}")
            else:
                return await ctx.send("Maximum queue limit has been reached, please wait for the current song to end to add more songs to the queue")

        await self.play_song(ctx, song)
        await ctx.send(f"Now playing: {song}")

    @commands.command()
    async def queue(self, ctx, *, song=None):
        if song is None:
            return await ctx.send("You must include a song to queue.")

        if not ("youtube.com/watch?" in song or "https://youtu.be/" in song):
            await ctx.send("Searching for a song, this may take a few seconds...")

            result = await self.search_song(1, song, get_url=True)

            if result is None:
                return await ctx.send("Sorry, I couldn't find the song you asked for. Try using my search command to find the song you want.")

            song = result[0]

        if ctx.voice_client.source is not None:
            try:
                queue_len = len(self.song_queue[str(ctx.guild.id)])
            except KeyError:
                self.song_queue[str(ctx.guild.id)] = []
                queue_len = 0

            if queue_len < 10:
                self.song_queue[str(ctx.guild.id)].append(song)
                return await ctx.send(f"Song added to the queue at position {queue_len+1}")
            else:
                return await ctx.send("Maximum queue limit has been reached, please wait for the current song to end to add more songs to the queue")

    @commands.command()
    async def pause(self, msg):
        try:
            self.voice_clients[msg.guild.id].pause()
        except Exception as err:
            print(err)

    @commands.command()
    async def resume(self, msg):
        try:
            self.voice_clients[msg.guild.id].resume()
        except Exception as err:
            print(err)

    @commands.command()
    async def stop(self, msg):
        try:
            self.voice_clients[msg.guild.id].stop()
            await self.voice_clients[msg.guild.id].disconnect()
        except Exception as err:
            print(err)
