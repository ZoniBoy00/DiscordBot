import asyncio
import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import i18n
from utils.database import update_song_status
from utils.spotify_client import sp

# YouTube DL setup
youtube_dl.utils.bug_reports_message = lambda: ''
ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}
ffmpeg_options = {'options': '-vn'}
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def join(self, ctx):
        if ctx.author.voice is None:
            await ctx.send(i18n.t('music.not_in_voice'))
            return
        channel = ctx.author.voice.channel
        if ctx.voice_client is not None:
            await ctx.voice_client.move_to(channel)
        else:
            await channel.connect()

    @commands.command()
    async def leave(self, ctx):
        if ctx.voice_client is not None:
            await ctx.voice_client.disconnect()
            await update_song_status(ctx.guild.id, None)
        else:
            await ctx.send(i18n.t('music.not_in_voice_channel'))

    @commands.command()
    async def play(self, ctx, *, query):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send(i18n.t('music.not_in_voice'))
                return

        if query.startswith('https://open.spotify.com/'):
            track_id = query.split('/')[-1].split('?')[0]
            try:
                track = sp.track(track_id)
                query = f"{track['name']} {track['artists'][0]['name']}"
            except Exception as e:
                await ctx.send(i18n.t('music.spotify_error'))
                return

        async with ctx.typing():
            try:
                player = await YTDLSource.from_url(query, loop=self.bot.loop)
                ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
            except Exception as e:
                await ctx.send(i18n.t('music.play_error'))
                return

        await ctx.send(i18n.t('music.now_playing', song=player.title))
        await update_song_status(ctx.guild.id, player.title)

    @commands.command()
    async def pause(self, ctx):
        if ctx.voice_client is None or not ctx.voice_client.is_playing():
            await ctx.send(i18n.t('music.not_playing'))
        else:
            ctx.voice_client.pause()
            await ctx.send(i18n.t('music.paused'))

    @commands.command()
    async def resume(self, ctx):
        if ctx.voice_client is None or ctx.voice_client.is_playing():
            await ctx.send(i18n.t('music.not_paused'))
        else:
            ctx.voice_client.resume()
            await ctx.send(i18n.t('music.resumed'))

    @commands.command()
    async def stop(self, ctx):
        if ctx.voice_client is None:
            await ctx.send(i18n.t('music.not_in_voice_channel'))
        else:
            ctx.voice_client.stop()
            await ctx.send(i18n.t('music.stopped'))
            await update_song_status(ctx.guild.id, None)