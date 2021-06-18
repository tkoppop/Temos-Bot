import datetime
import time
import random
import asyncio
import discord
from discord.ext import commands
import core
import config
from random import seed
from random import randint
from modules import model
seed(1)
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
                if ((sender["money"] >= amount) & (amount >= 0)):
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
    
    @economy.command(aliases=["cf", "c"])
    async def coinflip(self, ctx: commands.Context, choice:int, amount:int):

        """Coinflip function, enter 0 for heads 1 for tails"""
        with model.User(ctx.author).open_economy() as data:
            if((choice == 0) | (choice == 1)):
                if (data["money"]>= amount) & (amount > 0):
                    value = randint(0,1)
                    if value == 0:
                        await ctx.send(embed=core.bot_msg(f"it was heads"))
                    else :
                        await ctx.send(embed=core.bot_msg(f"it was tails"))
                    if value == choice:
                        data["money"] += amount
                        await ctx.send(embed=core.bot_msg(f"You won {amount}"))
                    else:
                        data["money"] -= amount
                        await ctx.send(embed=core.bot_msg(f"You Lost {amount}"))

                else: 
                    await ctx.send(embed = core.bot_msg(f"you don't have enough money for that poser"))
            
            else :
                await ctx.send(embed = core.bot_msg(f"You can't bet on neither heads or tails"))


    @economy.command(aliases=["rps"])
    async def rockpaperscissors(self, ctx: commands.Context, choice:str, amount:int):
        """Rock Paper Scissors"""
        output = 0
        with model.User(ctx.author).open_economy() as data:
            if(choice == 'r') | (choice == 'p')|(choice == 's'):
                """rock == 0, paper == 1, scissors == 2"""
                if (data["money"]>= amount) & (amount > 0):
                    value = randint(0,2)
                    if(choice == 'r') :
                        if(value == 2):
                            await ctx.send(embed = core.bot_msg(f"your opponent chose scissors"))
                            output = 0
                        elif(value == 1):
                            await ctx.send(embed = core.bot_msg(f"your opponent chose paper"))
                            output = 1
                        else:
                            await ctx.send(embed = core.bot_msg(f"your opponent chose rock"))
                            output = 2

                    elif( choice == 'p'):
                        if(value == 2):
                            await ctx.send(embed = core.bot_msg(f"your opponent chose scissors"))
                            output = 1
                        elif(value == 1):
                            await ctx.send(embed = core.bot_msg(f"your opponent chose paper"))
                            output = 2
                        else:
                            await ctx.send(embed = core.bot_msg(f"your opponent chose rock"))
                            output = 0    
                    else:
                        if(value == 2):
                            await ctx.send(embed = core.bot_msg(f"your opponent chose scissors"))
                            output = 2
                        elif(value == 1):
                            await ctx.send(embed = core.bot_msg(f"your opponent chose paper"))
                            output = 0
                        else:
                            await ctx.send(embed = core.bot_msg(f"your opponent chose rock"))
                            output = 1
                    if(output == 0):
                        data["money"] += amount
                        await ctx.send(embed = core.bot_msg(f"You win {amount}!"))
                    elif(output == 1):
                        data["money"] -= amount
                        await ctx.send(embed = core.bot_msg(f"You Lose {amount} :("))
                    else:
                        await ctx.send(embed = core.bot_msg(f"You tie"))
                else:
                    await ctx.send(embed = core.bot_msg(f"You don't have enough money for that"))     
            
            else:
                await ctx.send(embed = core.bot_msg(f"you have to choose one of rock(r) paper (p) or scissors(s)"))




def setup(bot: commands.Bot) -> None:
    bot.add_cog(Economy(bot))