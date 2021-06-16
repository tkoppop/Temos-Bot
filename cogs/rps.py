import asyncio
from discord.ext import commands


class rps(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(aliases=['rps'])
    async def rockPaperScissors(ctx, *, message: str) -> None:
        
        await ctx.send(message)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(rps(bot))