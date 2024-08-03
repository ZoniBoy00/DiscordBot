import asyncio
import logging
from discord.ext import commands
import discord
import i18n
from config import TOKEN, COMMAND_PREFIX
from utils.database import init_db
from cogs.music import Music
from cogs.games import Games
from cogs.language import Language

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# i18n setup
i18n.load_path.append('./locales')
i18n.set('fallback', 'en')

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

@bot.event
async def on_ready():
    logger.info(f'{bot.user} has connected to Discord!')
    await bot.add_cog(Music(bot))
    await bot.add_cog(Games(bot))
    await bot.add_cog(Language(bot))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(i18n.t('errors.command_not_found'))
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(i18n.t('errors.missing_argument'))
    else:
        logger.error(f'Unhandled error: {error}')
        await ctx.send(i18n.t('errors.unknown'))

async def main():
    async with bot:
        await init_db()
        await bot.start(TOKEN)

if __name__ == '__main__':
    asyncio.run(main())