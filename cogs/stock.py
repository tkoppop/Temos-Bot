import random
import asyncio
import discord
from discord.ext import commands
import core
import config
import secret
from modules import model
from riotwatcher import LolWatcher
watcher = LolWatcher(secret.key)

async def update_stocks() -> None:
    """Updates the stocks"""

    with model.Stocks().open() as stocks:
        for stock in stocks:
            if (stock == "JMSLP"):
                core.debug_info('updating lp')
                summoner = watcher.summoner.by_name('na1','sodacrackers')
                stats = watcher.league.by_summoner('na1', summoner['id'])
                num = 0
                if (stats[0]['queueType'] == 'RANKED_SOLO_5x5'):
                    num = 0
                else:
                    num = 1
                lp = stats[num]['leaguePoints']
                if (stocks[stock] > lp*1000):
                    core.debug_info("James just lost")
                elif (stocks[stock] < lp*1000) and (stocks[stock] != 1000):
                    core.debug_info("James just Won")
                stocks[stock] = lp * 1000
                if stocks[stock] <= 0:
                    stocks[stock] = config.stocks.standard
                
            else:    
                stocks[stock] += random.randint(
                    -1 * config.stocks.change, config.stocks.change
                )
                if stocks[stock] <= 0:
                    stocks[stock] = config.stocks.standard


class Stocks(commands.Cog):
    def __init__(self, bot: discord.Client):
        self.bot = bot

    @commands.group(aliases=["s"], description="Buy and sell stocks")
    async def stocks(self, ctx: commands.Context) -> None:
        """Stocks m->market, p->portfolio, b->buy, s->sell"""

        if ctx.invoked_subcommand is None:
            await ctx.send("Specify a stock command")

    @stocks.command(aliases=["m"])
    async def market(self, ctx: commands.Context) -> None:
        """View current value of stocks"""
        embed = discord.Embed(color=config.bot.color, title="Market")
        with model.Stocks().open() as stocks:
            for stock in stocks:
                embed.add_field(name=stock, value=stocks[stock])
        await ctx.send(embed=embed)

    @stocks.command(aliases=["p", "port", "stocks"])
    async def portfolio(
        self, ctx: commands.Context, member: discord.Member = None
    ) -> None:
        if member is None:
            member = ctx.author
        embed = discord.Embed(
            color=config.bot.color, title=f"{member.display_name} stocks"
        )
        with model.User(member).open_economy() as data:
            with model.Stocks().open() as stocks:
                totalValue = 0
                for stock, amount in data["stocks"].items():
                    if amount > 0:
                        value = amount * stocks[stock]
                        embed.add_field(
                            name=stock,
                            value="{0} x ({1} {2}) = {3} {2}".format(
                                amount,
                                stocks[stock],
                                await core.lukeEmoji(ctx.guild),
                                value,
                            ),
                        )
                        totalValue += value
                embed.add_field(
                    name="Total Value",
                    value="{0} {1}".format(
                        totalValue, await core.lukeEmoji(ctx.guild)
                    ),
                )
        await ctx.send(embed=embed)

    @stocks.command(aliases=["b"])
    async def buy(self, ctx: commands.Context, stock: str, amount: int = 1) -> None:
        with model.User(ctx.author).open_economy() as eco:
            with model.Stocks().open() as stocks:
                if amount <=0:
                    await ctx.send(f"STOP this was removed")
                
                else:
                    if stock.upper() in stocks:
                        stock = stock.upper()
                        price = (
                            stocks[stock] + config.stocks.tradeChange * amount
                        ) * amount
                        if eco["money"] >= price:
                            eco["money"] -= price
                            eco["stocks"][stock] += amount
                            stocks[stock] += config.stocks.tradeChange * amount
                            await core.bot_send(
                                ctx,
                                "Bought {0} {1} for {2} {3}".format(
                                    amount, stock, price, await core.lukeEmoji(ctx.guild),
                                ),
                            )
                        else:
                            await core.bot_send(
                                ctx,
                                "Sorry, you have {0} of {1} {2} {3}".format(
                                    eco["money"],
                                    price,
                                    await core.lukeEmoji(ctx.guild),
                                    "required for this purchase",
                                ),
                            )

                    else:
                        await core.bot_send(
                            ctx,
                            f"Stock {stock} doesnt exist, use 'l.s m' to view all stocks",
                        )

    @stocks.command(aliases=["s"])
    async def sell(self, ctx: commands.Context, stock: str, amount: int = 1) -> None:
        with model.User(ctx.author).open_economy() as eco:
            with model.Stocks().open() as stocks:
                if amount <=0:
                    await ctx.send(f"STOP this was removed")

                else:
                    if stock.upper() in stocks:
                        stock = stock.upper()
                        price = stocks[stock] * amount
                        if eco["stocks"][stock] >= amount:
                            eco["stocks"][stock] -= amount
                            eco["money"] += price
                            stocks[stock] -= config.stocks.tradeChange * amount
                            await core.bot_send(
                                ctx,
                                "Sold {0} {1} for {2} {3}".format(
                                    amount, stock, price, await core.lukeEmoji(ctx.guild),
                                ),
                            )
                        else:
                            await core.bot_send(
                                ctx,
                                "Sorry, you have {0} of {1} {2}".format(
                                    eco["stocks"][stock], stock, "required for this sale",
                                ),
                            )
                    else:
                        await core.bot_send(
                            ctx,
                            f"Stock {stock} doesnt exist, use 'l.s m' view to view all stocks",
                        )

    @stocks.command(hidden=True, aliases=["u"])
    @commands.is_owner()
    async def update(self, ctx: commands.Context) -> None:
        await update_stocks()
        await ctx.send(embed=core.bot_msg("Updated Stocks"))

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        core.debug_info("Economy startup")
        self.bot.loop.create_task(self.track_stocks())
        core.debug_info("Finished economy setup")


    async def track_stocks(self) -> None:
        while not self.bot.is_closed():
            core.debug_info("Updating stocks")
            await update_stocks()
            await asyncio.sleep(config.stocks.updateFrequency)

    # @stocks.command(alias=["lb"])
    # async def leaderboards(self, ctx:commands.Context):
    #     embed = discord.Embed(color=config.bot.color, title="Leaderboard")
    #         for User in model.User():
    #             with model.User(users) as target:
    #                 with target.openeconomy() as mon:
    #                     with model.Stocks().open() as stocks:
    #                         totalValue = 0
    #                         for stock, amount in mon["stocks"].items():
    #                             if amount > 0:
    #                                 value = amount * stocks[stock]
    #                             totalValue += value
    #                         embed  = core.bot_msg(f"{totalValue + mon['money']}")
    #           await ctx.send(embed=embed)








def setup(bot: commands.Bot) -> None:
    bot.add_cog(Stocks(bot))