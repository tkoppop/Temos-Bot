import datetime
import time
import random
import asyncio
import discord
from discord.ext import commands
import core
import config
from modules import model

class Economy(commands.Cog):
    def __init__(self, bot: discord.Client):
        self.bot = bot
    @commands.group(
        
        pass_context=True,
        description="Header for eco related commands",
        aliases=["eco", "e"],
    )
    async def economy(self, ctx: commands.Context) -> None:
        """Economy t->tax,  give->give money,  m->my wallet"""
        if ctx.invoked_subcommand is None:
            await ctx.send("Specify a economy command")

    @economy.command(aliases=["m", "$"])
    async def money(self, ctx: commands.Context, member: discord.Member = None) -> None:
        if member is None:
            user = ctx.author
        else:
            user = member
        with model.User(user).open_economy() as economyData:
            await core.bot_send(
                ctx,
                "{0} has {1} {2}".format(
                    user.display_name,
                    economyData["money"],
                    await core.lukeEmoji(ctx.guild),
                ),
            )
        core.debug_info(ctx.author.name, ctx.guild, await core.lukeEmoji(ctx.guild))

    @economy.command()
    async def give(
        self, ctx: commands.Context, member: discord.Member, amount: int
    ) -> None:
        with model.User(ctx.author).open_economy() as sender:
            with model.User(member).open_economy() as receiver:
                if sender["money"] >= amount >= 0:
                    receiver["money"] += amount
                    sender["money"] -= amount
                    await ctx.send(
                        embed=core.bot_msg(
                            "{0} sent {2} {3} to {1}".format(
                                ctx.author.display_name,
                                member.display_name,
                                amount,
                                await core.lukeEmoji(ctx.guild),
                            )
                        )
                    )
                else:
                    await ctx.send(
                        embed=core.bot_msg(
                            "Not enough {}".format(await core.lukeEmoji(ctx.guild))
                        )
                    )

    @economy.command(aliases=["t"])
    async def tax(self, ctx: commands.Context) -> None:
        """Command to collect periodic tax"""
        current = time.time()

        with model.User(ctx.author).open_economy() as data:
            diff = datetime.timedelta(seconds=(current - data["taxTime"]))
            core.debug_info(current, data["taxTime"], diff, diff.seconds)
            if (diff.days * 86400 + diff.seconds) >= config.economy.taxTime:
                data["money"] += config.economy.taxAmount
                data["taxTime"] = current
                await ctx.send(
                    embed=core.bot_msg(
                        "Collected tax of {0} {1}".format(
                            config.economy.taxAmount, await core.lukeEmoji(ctx.guild)
                        )
                    )
                )

            else:
                cooldown = datetime.timedelta(seconds=config.economy.taxTime)
                rem = cooldown - diff
                await ctx.send(
                    embed=core.bot_msg(f"{rem} remaining before you can tax again")
                )
    

def setup(bot: commands.Bot) -> None:
    bot.add_cog(Economy(bot))