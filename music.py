import asyncio
import discord
import youtube_dl
from discord.ext import commands
from discord import ClientException
from discord import app_commands



class Music(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.song_queue = {}
        self.yt_dl_opts = {
            'format':'140',
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

    # This event happens when a message gets sent
    @commands.command()
    async def play(self, msg):

        try:
            voice_client = await msg.author.voice.channel.connect()
            self.voice_clients[voice_client.guild.id] = voice_client
        except:
            print("error")

        try:
            url = msg.message.content.split()[1]
            loop = asyncio.get_event_loop()

            
            data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(url, download=False))
            
            song = data['url']
            player = discord.FFmpegPCMAudio(song, **self.ffmpeg_options)

            self.voice_clients[msg.guild.id].play(player)

        except Exception as err:
            print(err)


    
            

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