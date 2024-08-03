import asyncio
import random
from discord.ext import commands
import i18n
from utils.database import add_credits, get_credits

shop_items = {
    'vip': {'price': 1000, 'description': 'VIP-rooli'},
    'väri': {'price': 500, 'description': 'Mukautettu nimen väri'},
    'emoji': {'price': 300, 'description': 'Mukautettu emoji nimen viereen'}
}

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def arvaa(self, ctx):
        number = random.randint(1, 10)
        await ctx.send(i18n.t('games.guess'))

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            guess = await self.bot.wait_for('message', check=check, timeout=30.0)
        except asyncio.TimeoutError:
            return await ctx.send(i18n.t('games.timeout', number=number))

        if guess.content.isdigit() and int(guess.content) == number:
            await ctx.send(i18n.t('games.correct'))
            await add_credits(ctx.author.id, 100)
        else:
            await ctx.send(i18n.t('games.wrong', number=number))

    @commands.command()
    async def krediitit(self, ctx):
        amount = await get_credits(ctx.author.id)
        await ctx.send(i18n.t('games.credits', amount=amount))

    @commands.command()
    async def kauppa(self, ctx):
        embed = discord.Embed(title=i18n.t('shop.title'), description=i18n.t('shop.description'), color=0x00ff00)
        for item, details in shop_items.items():
            embed.add_field(name=item, value=i18n.t('shop.item', description=details['description'], price=details['price']), inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def osta(self, ctx, item: str):
        if item not in shop_items:
            await ctx.send(i18n.t('shop.not_available'))
            return
        user_credits = await get_credits(ctx.author.id)
        if user_credits < shop_items[item]['price']:
            await ctx.send(i18n.t('shop.not_enough_credits'))
            return
        await add_credits(ctx.author.id, -shop_items[item]['price'])
        await ctx.send(i18n.t('shop.purchased', item=item, credits=user_credits - shop_items[item]['price']))