import discord
from discord.ext import commands
import wavelink
from discord.ext import commands
from wavelink.ext import spotify
import re
import os

cid = os.environ["SPOTIFY_CLIENT_ID"]
csecret = os.environ["SPOTIFY_CLIENT_SECRET"]


class CustomPlayer(wavelink.Player):

    def __init__(self):
        super().__init__()
        self.queue = wavelink.Queue()

        
class Music(commands.Cog):
    """Music cog to hold Wavelink related commands and listeners."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.song_queue = {}
        bot.loop.create_task(self.connect_nodes())

    async def connect_nodes(self):
        """Connect to our Lavalink nodes."""
        await self.bot.wait_until_ready()

        await wavelink.NodePool.create_node(bot=self.bot,
                                            host='0.0.0.0',
                                            port=2333,
                                            password='1234', spotify_client=spotify.SpotifyClient(client_id=cid, client_secret=csecret))

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: CustomPlayer, track: wavelink.Track, reason):
        if not player.queue.is_empty:
            next_track = player.queue.get()
            await player.play(next_track)

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        """Event fired when a node has finished connecting."""
        print(f'Node: <{node.identifier}> is ready!')

    

    def check_string(self, input_string):
        youtube_pattern = re.compile(
            r'https?://(www\.)?(youtube|youtu)(\.com|\.be)/(playlist\?list=|watch\?v=|embed/)([a-zA-Z0-9-_]+)')
        spotify_pattern = re.compile(
            r'https?://open\.spotify\.com/(album|playlist|track)/([a-zA-Z0-9-]+)(/[a-zA-Z0-9-]+)?(\?.*)?')

        youtube_match = youtube_pattern.match(input_string)
        spotify_match = spotify_pattern.match(input_string)

        if youtube_match:
            if 'watch?v=' in youtube_match.group():
                return 'YouTube Song'
            elif 'playlist?list=' in youtube_match.group():
                return 'YouTube Playlist'
            else:
                return 'YouTube URL'
        elif spotify_match:
            if 'album' in spotify_match.group():
                return 'Spotify Album'
            elif 'playlist' in spotify_match.group():
                return 'Spotify Playlist'
            elif 'track' in spotify_match.group():
                return 'Spotify Track'
            else:
                return 'Spotify URL'
        else:
            return 'Text'

    async def play_spotify_track(self, ctx: discord.ext.commands.Context, track: str, vc: CustomPlayer):

        track = await spotify.SpotifyTrack.search(query=track, return_first=True)
        if vc.is_playing() or not vc.queue.is_empty:
            vc.queue.put(item=track)
            await ctx.send(f'Queued {track.title} in {vc.channel}')
        else:
            await vc.play(track)
            await ctx.send(f'Playing {track.title} in {vc.channel}')

    async def play_spotify_playlist(self, ctx: discord.ext.commands.Context, playlist: str, vc: CustomPlayer):
        await ctx.send("Loading playlist...")
        async for partial in spotify.SpotifyTrack.iterator(query=playlist, partial_tracks=True):
            if vc.is_playing() or not vc.queue.is_empty:
                vc.queue.put(item=partial)
            else:
                await vc.play(partial)
                await ctx.send(embed=discord.Embed(
                    title=vc.source.title,
                    description=f"Playing {vc.source.title} in {vc.channel}"
                ))

    async def play_youtube_song(self, ctx: discord.ext.commands.Context, song: str, vc: CustomPlayer):
        if vc.is_playing() or not vc.queue.is_empty:
            vc.queue.put(item=song)
            await ctx.send(embed=discord.Embed(
                title=song.title,
                url=song.uri,
                description=f"Queued {song.title} in {vc.channel}"
            ))
        else:
            await vc.play(song)
            await ctx.send(embed=discord.Embed(
                title=vc.source.title,
                url=vc.source.uri,
                description=f"Playing {vc.source.title} in {vc.channel}"
            ))

    async def play_youtube_playlist(ctx: discord.ext.commands.Context, playlist: str):
        # play youtube playlist
        pass

    async def play_query(self, ctx: discord.ext.commands.Context, search: str, vc: CustomPlayer):
        
        # convert query to youtube url
        track = await wavelink.YouTubeTrack.search(query=search, return_first=True)

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
                title=vc.source.title,
                url=vc.source.uri,
                description=f"Playing {vc.source.title} in {vc.channel}"
            ))
        pass

    # Map URL types to their corresponding functions
    url_type_mapping = {
        'Spotify Track': play_spotify_track,
        'Spotify Playlist': play_spotify_playlist,
        'Spotify Album': play_spotify_playlist,
        'YouTube Song': play_youtube_song,
        'YouTube Playlist': play_youtube_playlist,
        'Text' : play_query,
    }

    @commands.command()
    async def play_media(self, ctx: commands.Context, *, search: str):
        url_type = self.check_string(search)
        action = self.url_type_mapping.get(url_type, None)

        vc = ctx.voice_client
        if not vc:
            custom_player = CustomPlayer()
            vc: CustomPlayer = await ctx.author.voice.channel.connect(cls=custom_player)

        if action:
            await action(self, ctx, search, vc)
        else:
            # handle text input
            pass







"""

@commands.command()
    async def play(self, ctx, *, search: wavelink.YouTubeTrack):
        vc = ctx.voice_client
        if not vc:
            custom_player = CustomPlayer()
            vc: CustomPlayer = await ctx.author.voice.channel.connect(cls=custom_player)

        if vc.is_playing() or not vc.queue.is_empty:

            #
            vc.queue.put(item=search)

            await ctx.send(embed=discord.Embed(
                title=search.title,
                url=search.uri,
                description=f"Queued {search.title} in {vc.channel}"
            ))
        else:
            await vc.play(search)

            await ctx.send(embed=discord.Embed(
                title=vc.source.title,
                url=vc.source.uri,
                description=f"Playing {vc.source.title} in {vc.channel}"
            ))


"""