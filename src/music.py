import discord
from discord.ext import commands
import wavelink
from discord import app_commands
from wavelink.ext import spotify
import re
import os
from src.log import log_command


class CustomPlayer(wavelink.Player):
    """Custom player class for wavelink."""

    def __init__(self):
        super().__init__()
        self.queue = wavelink.Queue()


class Music(commands.Cog):
    """Suite of commands allowing BrennerBot to play music from Youtube and Spotify."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.song_queue = {}
        self.cid = os.environ["SPOTIFY_CLIENT_ID"]
        self.csecret = os.environ["SPOTIFY_CLIENT_SECRET"]
        bot.loop.create_task(self.connect_nodes())

    async def connect_nodes(self):
        """Connect to our Lavalink nodes."""
        await self.bot.wait_until_ready()
        sc = spotify.SpotifyClient(
            client_id=self.cid, client_secret=self.csecret
        )
        node: wavelink.Node = wavelink.Node(
            uri='http://localhost:2333', password='1234')
        await wavelink.NodePool.connect(client=self.bot, nodes=[node], spotify=sc)

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEventPayload):
        player = payload.player
        if not player.queue.is_empty:
            next_track = player.queue.get()
            await player.play(next_track)

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        """Event fired when a node has finished connecting."""
        print(f'Node: <{node}> is ready!')

    @commands.command()
    @log_command
    async def join(self, ctx):
        vc = ctx.voice_client
        try:
            channel = ctx.author.voice.channel
        except AttributeError:
            return await ctx.send("How can I join if you are nowhere to be found?")
        if vc:
            await vc.disconnect()
        await channel.connect(cls=CustomPlayer())

    @commands.command()
    @log_command
    async def leave(self, ctx):
        vc = ctx.voice_client
        if vc:
            await vc.disconnect()
        else:
            await ctx.send("how can i disconnect when i am not connect?")

    @commands.command()
    @log_command
    async def play(self, ctx: commands.Context, *, search: str = commands.parameter(
            description="Plays a song from url or query. Accepted urls are: spotify [track,album,playlist], youtube.")):
        """
        Play requested song (url or query). Queues if a song is already playing.

        Usage:
        !play <search>
        """
        url_type = self.check_string(search)
        action = self.url_type_mapping.get(url_type, None)
        vc = ctx.voice_client
        if not vc:
            custom_player = CustomPlayer()
            vc: CustomPlayer = await ctx.author.voice.channel.connect(
                cls=custom_player)
        if action:
            await action(self, ctx, search, vc)
        else:
            # handle text input
            await ctx.send("Idk that link is suss. Try again.")

    @commands.command()
    @log_command
    async def pause(self, ctx):
        """Skips the current song."""
        vc = ctx.voice_client
        if vc:
            if vc.is_playing() and not vc.is_paused():
                await vc.pause()
            else:
                await ctx.send("Nothing is playing.")
        else:
            await ctx.send("The bot is not connected to a voice channel")

    @commands.command()
    @log_command
    async def resume(self, ctx):
        """Resumes the current song."""
        vc = ctx.voice_client
        if vc:
            if vc.is_paused():
                await vc.resume()
            else:
                await ctx.send("Nothing is paused.")
        else:
            await ctx.send("The bot is not connected to a voice channel")

    @commands.command()
    @log_command
    async def skip(self, ctx):
        """Skip the current song."""
        vc = ctx.voice_client
        if vc:
            if not vc.is_playing():
                return await ctx.send("Nothing is playing.")
            if vc.queue.is_empty:
                return await vc.stop()

            await vc.seek(vc.current.length * 1000)
            if vc.is_paused():
                await vc.resume()
        else:
            await ctx.send("The bot is not connected to a voice channel.")

    async def play_spotify_track(self, ctx: discord.ext.commands.Context, track: str, vc: CustomPlayer):
        track = await spotify.SpotifyTrack.search(track, return_first=True)
        if vc.is_playing() or not vc.queue.is_empty:
            vc.queue.put(item=track)
            await ctx.send(embed=discord.Embed(
                title=track.title,
                url=track.uri,
                description=f"Queued {track.title} in {vc.channel}"
            ))
        else:
            await vc.play(track)
            await ctx.send(embed=discord.Embed(
                title=track.title,
                url=track.uri,
                description=f"Queued {track.title} in {vc.channel}"
            ))

    async def play_spotify_playlist(self, ctx: discord.ext.commands.Context, playlist: str, vc: CustomPlayer):
        await ctx.send("Loading playlist...")
        async for partial in spotify.SpotifyTrack.iterator(query=playlist):
            if vc.is_playing() or not vc.queue.is_empty:
                vc.queue.put(item=partial)
            else:
                await vc.play(partial)
                await ctx.send(embed=discord.Embed(
                    title=vc.current.title,
                    description=f"Playing {vc.current.title} in {vc.channel}"
                ))

    async def play_youtube_song(self, ctx: discord.ext.commands.Context, query: str, vc: CustomPlayer):
        try:
            # remove time from youtube link
            query = re.sub(r'&t=\d+', '', query)
            print(query)
            track = await wavelink.NodePool.get_node().get_tracks(wavelink.YouTubeTrack, query)
            track = track[0]
            if vc.is_playing() or not vc.queue.is_empty:
                vc.queue.put(item=track)
                await ctx.send(embed=discord.Embed(
                    title=track.title,
                    url=track.uri,
                    description=f"Queued {track.title} in {vc.channel}"
                ))
            else:
                await vc.play(track)
                await ctx.send(embed=discord.Embed(
                    title=vc.current.title,
                    url=vc.current.uri,
                    description=f"Playing {vc.current.title} in {vc.channel}"
                ))
        except Exception as e:
            await ctx.send(f"That link is weird. Make sure theres no timestamp at the end.")

    async def play_youtube_playlist(ctx: discord.ext.commands.Context, playlist: str):
        # play youtube playlist
        pass

    async def play_query(self, ctx: discord.ext.commands.Context, search: str, vc: CustomPlayer):
        # convert query to youtube url
        track = await wavelink.YouTubeTrack.search(search, return_first=True)
        if vc.is_playing() or not vc.queue.is_empty:
            vc.queue.put(item=track)
            await ctx.send(embed=discord.Embed(
                title=track.title,
                url=track.uri,
                description=f"Queued {track.title} in {vc.channel}"
            ))
        else:
            await vc.play(track)
            await ctx.send(embed=discord.Embed(
                title=vc.current.title,
                url=vc.current.uri,
                description=f"Playing {vc.current.title} in {vc.channel}"
            ))

    # Map URL types to their corresponding functions
    url_type_mapping = {
        'Spotify Track': play_spotify_track,
        'Spotify Playlist': play_spotify_playlist,
        'Spotify Album': play_spotify_playlist,
        'YouTube Song': play_youtube_song,
        'YouTube Playlist': play_youtube_playlist,
        'Text': play_query,
    }

    def check_string(self, input_string):

        youtube_pattern = re.compile(
            (r'https?://(www\.)?(youtube|youtu)(\.com|\.be)/'
             '(playlist\?list=|watch\?v=|embed/|)([a-zA-Z0-9-_]+)(\&t=\d+s)?'
             '|https://youtu.be/([a-zA-Z0-9-_]+)(\?t=\d+s)?'))
        spotify_pattern = re.compile(
            (r'https?://open\.spotify\.com/(album|playlist|track)'
             '/([a-zA-Z0-9-]+)(/[a-zA-Z0-9-]+)?(\?.*)?'))

        youtube_match = youtube_pattern.match(input_string)
        spotify_match = spotify_pattern.match(input_string)

        if youtube_match:
            return self.get_youtube_pattern(youtube_match)
        elif spotify_match:
            return self.get_spotify_pattern(spotify_match)
        return 'Text'

    def get_spotify_pattern(self, spotify_match):
        if spotify_match:
            if 'track' in spotify_match.group():
                return 'Spotify Track'
            elif 'playlist' in spotify_match.group():
                return 'Spotify Playlist'
            elif 'album' in spotify_match.group():
                return 'Spotify Album'
            else:
                return 'Spotify URL'

    def get_youtube_pattern(self, youtube_match):
        if youtube_match:
            if 'watch?v=' in youtube_match.group() or 'youtu.be' in youtube_match.group():
                return 'YouTube Song'
            elif 'playlist?list=' in youtube_match.group():
                return 'YouTube Playlist'
            else:
                return 'YouTube URL'
