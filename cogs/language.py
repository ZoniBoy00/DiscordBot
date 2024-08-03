from discord.ext import commands
import i18n
from utils.database import set_language, get_language

class Language(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setlang(self, ctx, lang: str):
        if lang not in ['en', 'fi', 'sv']:
            await ctx.send(i18n.t('language.not_supported'))
            return
        await set_language(ctx.guild.id, lang)
        i18n.set('locale', lang)
        await ctx.send(i18n.t('language.changed', locale=lang))

    @commands.command()
    async def getlang(self, ctx):
        lang = await get_language(ctx.guild.id)
        await ctx.send(i18n.t('language.current', locale=lang))

    @commands.Cog.listener()
    async def on_command(self, ctx):
        lang = await get_language(ctx.guild.id)
        i18n.set('locale', lang)