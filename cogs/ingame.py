import asyncio
import concurrent

import discord
from discord.ext import commands
from concurrent.futures.thread import ThreadPoolExecutor

from minecraft.exceptions import ProxyConnection, YggdrasilError

from utils.PlayerWrapper import PlayerWrapper
from utils.utli import GetMessage


class Ingame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.executor = ThreadPoolExecutor()
        self.player = None
        self.isPycraftInstance = False

    async def SendChatToDiscord(self, bot, message, guildId):
        try:
            if not self.isPycraftInstance:
                # This should only be used by PlayerWrapper instances
                return

            if guildId not in bot.account_dict:
                return

            data = await bot.config.find(guildId)
            if not data or "bot channel" not in data:
                return

            channel = bot.get_channel(data["bot channel"])
            await channel.send(embed=discord.Embed.from_dict({"description": message}))
        except:
            pass

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} cog has been loaded\n-----")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if not message.guild:
            return

        if message.guild.id not in self.bot.account_dict:
            return

        if message.guild.id not in self.bot.database_entries:
            return

        if message.content.startswith(
            self.bot.database_entries[message.guild.id]["prefix"]
        ):
            return

        if self.bot.database_entries[message.guild.id]["channel"] is None:
            return

        # TODO clean this content so it sends names rather then <@123413412> etc shit
        # msg = f"{message.author.display_name} -> {message.content}"
        player = self.bot.account_dict[message.guild.id]
        player.SendChat(message.content)

        try:
            await message.delete()
        except discord.errors.NotFound:
            pass

    @commands.command(
        name="connect", description="Connect a minecraft account to the server",
    )
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def connect(self, ctx):
        try:
            await ctx.message.delete()
        except discord.errors.NotFound:
            pass

        if ctx.guild.id in self.bot.account_dict:
            await ctx.send(
                "A connection should already be established. Kill it with the `disconnect` command if wanted."
            )
            return

        """
        if len(self.bot.account_dict[ctx.guild.id]) >= self.bot.free_accounts_per_guild:
            await ctx.send(
                "You have reached the maximum accounts you can use for this guild!\n||If you wish to upgrade, "
                "please join our discord and create a ticket. `info` command|| ",
                delete_after=30,
            )
            return
        """

        questions = [
            ["What is the account email/username?", "Typically an email address."],
            [
                "What is the account password?",
                "This will be deleted and is not stored.",
            ],
            [
                "What server should I connect to?",
                "If it doesnt use the default port, add the port after the server.\n`myserver.com 12345` as an example",
            ],
        ]
        answers = []
        for question in questions:
            placeholder = await GetMessage(self.bot, ctx, question[0], question[1])
            if placeholder is False:
                await ctx.send("Cancelling.", delete_after=15)
                return

            answers.append(placeholder)

        print(ctx.author.name, answers[0])

        if len(answers) != 3:
            await ctx.send(
                "Unknown issue, please join our support discord and create a ticket.\n||Discord can be found in the "
                "`info` command|| ",
                delete_after=15,
            )
            return

        try:
            player = PlayerWrapper(answers[0], answers[1], self.bot, ctx.guild.id)
        except YggdrasilError as e:
            await ctx.send(f"Login failure: `{e}`")
        else:
            if " " in answers[2]:
                ip, port = answers[2].split(" ")
                player.SetServer(ip, port=int(port))
            else:
                player.SetServer(answers[2])
            print("Server set")
            futures = []
            futures.append(self.executor.submit(player.Connect))
            futures.append(self.executor.submit(player.HandleChat))
            print("Submitted to executor")
            self.bot.account_dict[ctx.guild.id] = player
            print("Set in dict")
            await ctx.send(
                f"`{answers[0]}` should have connected to `{answers[2]}`",
                delete_after=15,
            )

            noChannel = False
            if ctx.guild.id in self.bot.database_entries:
                if self.bot.database_entries[ctx.guild.id]["channel"] is None:
                    noChannel = True

            if ctx.guild.id not in self.bot.database_entries:
                noChannel = True

            if noChannel:
                await ctx.send(
                    "Please note, as you have not set a bot channel chat cannot be sent from Minecraft to discord "
                    "or discord to Minecraft. To set this up please run the `sbc <channel>` command, "
                    "then disconnect and reconnect your account. ",
                    delete_after=30,
                )

            # Check for thread errors
            for _ in range(15):
                await asyncio.sleep(2.5)
                for future in concurrent.futures.as_completed(futures):
                    try:
                        print(future.result())
                    except ProxyConnection as e:
                        print(e)
                    except Exception as e:
                        print(e)

    @commands.command(
        name="disconnect", description="Disconnect your account from the server"
    )
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def disconnect(self, ctx):
        await ctx.message.delete()
        if ctx.guild.id not in self.bot.account_dict:
            await ctx.send("A connection is not already established.")
            return

        player = self.bot.account_dict[ctx.guild.id]

        try:
            player.Disconnect()
        except OSError:
            pass
        self.bot.account_dict.pop(ctx.guild.id)
        await ctx.send("The account should have disconnected", delete_after=15)

    @commands.command(
        name="sudo", description="Get your account to say something!", usage="<message>"
    )
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def sudo(self, ctx, *, message):
        if ctx.guild.id not in self.bot.account_dict:
            await ctx.send("A connection is not already established.")
            return

        player = self.bot.account_dict[ctx.guild.id]
        player.SendChat(message)

        await ctx.send(f"`{player.auth_token.username}` should have said: `{message}`")


def setup(bot):
    bot.add_cog(Ingame(bot))
