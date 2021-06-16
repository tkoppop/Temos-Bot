import discord
import config


async def lukeEmoji(guild: discord.Guild) -> discord.Emoji:
    """Attempts to return a LukeBux emoji"""
    try:
        for e in guild.emojis:
            if e.name == "nicetry":
                return e
    except AttributeError:
        pass
    try:
        with open("resources/nicetry.png", "rb") as i:
            emoji = await guild.create_custom_emoji(name="nicetry", image=i.read())
        return emoji
    except (discord.errors.Forbidden, AttributeError):
        return "SC"


def bot_msg(value: str) -> discord.Embed:
    """Returns a customized embed with the given message"""
    return discord.Embed(color=config.bot.color, description=value)

async def bot_send(channel: discord.abc.Messageable, message: str) -> discord.Message:
    """Sends the message as an embed"""
    return await channel.send(embed=bot_msg(message))


# Debug method
def debug_info(*messages: object) -> None:
    """Function for printing seperate information chunks"""
    for line in messages:
        print(line)
    print("-----")