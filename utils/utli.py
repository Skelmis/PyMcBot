import asyncio
import random

import discord


async def GetMessage(
    bot, ctx, contentOne="Default Message", contentTwo="\uFEFF", timeout=100
):
    """
    This function sends an embed containing the params and then waits for a message to return

    Params:
     - bot (commands.Bot object) :
     - ctx (context object) : Used for sending msgs n stuff

     - Optional Params:
        - contentOne (string) : Embed title
        - contentTwo (string) : Embed description
        - timeout (int) : Timeout for wait_for

    Returns:
     - msg.content (string) : If a message is detected, the content will be returned
    or
     - False (bool) : If a timeout occurs
    """
    embed = discord.Embed(
        title=f"{contentOne}",
        description=f"{contentTwo}",
        colour=random.choice(bot.color_list),
    )
    sent = await ctx.send(embed=embed)
    try:
        msg = await bot.wait_for(
            "message",
            timeout=timeout,
            check=lambda message: message.author == ctx.author
            and message.channel == ctx.channel,
        )
        if msg:
            await asyncio.sleep(1)
            await sent.delete()
            await msg.delete()
            return msg.content
    except asyncio.TimeoutError:
        await sent.delete()
        return False
