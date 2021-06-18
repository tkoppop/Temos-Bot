from typing import Callable, Any
import os
import discord
from discord.ext import commands
import config
import core
import secret
from riotwatcher import LolWatcher
watcher = LolWatcher(secret.key)
os.chdir(os.path.dirname(os.path.abspath(__file__)))

bot = commands.Bot(
    command_prefix=config.bot.prefixes, description="Buying and Selling Lukes"
)

@bot.event
async def on_ready() -> None:
    core.debug_info("Bot logged in as", bot.user.name, bot.user.id)
    await bot.change_presence(
        activity=discord.Game(name=(bot.command_prefix[0] + "help"))
    )
    core.debug_info("Finished setup")

@bot.event
async def on_message(message: discord.Message) -> None:
    await bot.process_commands(message)

default_error_handler = bot.on_command_error

@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError) -> None:
    if not hasattr(ctx.command, "on_error"):
        await core.bot_send(ctx, f'Invalid command used.')
        await default_error_handler(ctx, error)


@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency*1000)}ms')


@bot.command()
async def test(ctx: commands.Context, number: int) -> None:
    await core.bot_send(ctx.channel, str(number + 1))

@bot.command()
async def clear(ctx, amount : int = 1):
    await ctx.channel.purge(limit=amount)

@clear.error
async def bot_error(ctx, error):
    if isinstance(error,commands.MissingRequiredArguments):
        await ctx.send('Please specify an amount of message to delete.')

@bot.command(hidden=True)
@commands.is_owner()
async def reload(ctx: commands.Context) -> None:
    core.debug_info("Reloading extensions")
    success = handle_extensions(bot.reload_extension)
    if success:
        await core.bot_send(ctx, "Reloaded extensions")
    else:
        await core.bot_send(ctx, "At least one extension failed to reload")

@bot.command(aliases=['ls'])
async def leaguestats(ctx, *,summonerName):
    summoner = watcher.summoner.by_name('na1',summonerName)
    stats = watcher.league.by_summoner('na1', summoner['id'])
    num = 0
    if (stats[0]['queueType'] == 'RANKED_SOLO_5x5'):
        num = 0
    else:
        num = 1
    tier = stats[num]['tier']
    rank = stats[num]['rank']
    lp = stats[num]['leaguePoints']
    wins= int(stats[num]['wins'])
    losses = int(stats[num]['losses'])
    wr = int((wins/(wins+losses))* 100)
    await core.bot_send(ctx, f'{summonerName} is currently ranked in {str(tier)}, {str(rank)} with {str(lp)} LP and a {str(wr)}% winrate.')

@bot.event
async def leaguestats_error(ctx, error):
    if isinstance(error,commands.MissingRequiredArguments):
        await ctx.send('Please specify a summoner name')



extensions = [
    "cogs.economy",
    "cogs.stock"
]


def handle_extensions(handler: Callable[[str], Any]) -> bool:
    success = True
    for extension in extensions:
        try:
            handler(extension)
        except Exception as e: 
            core.debug_info(
                f"Failed to use {handler.__name__} on extension {extension}", e
            )
            success = False
        else:
            core.debug_info(f"Used {handler.__name__} on extension {extension}")
    return success



if __name__ == "__main__":
    handle_extensions(bot.load_extension)
    core.debug_info("Starting bot")
    bot.run(secret.token)