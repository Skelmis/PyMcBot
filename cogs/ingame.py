from __future__ import print_function

import sys
import re

from pyCraft.minecraft import authentication
from pyCraft.minecraft.exceptions import YggdrasilError
from pyCraft.minecraft.networking.connection import Connection
from pyCraft.minecraft.networking.packets import Packet, clientbound, serverbound, PacketBuffer
from pyCraft.minecraft.compat import input

import discord
from discord.ext import commands
from discord.ext.tasks import loop
import os
from concurrent.futures import ThreadPoolExecutor
import asyncio

import time
import functools

import cogs._json

class Alts():

    def __init__(self, bot, username, password, channel=None):
        """
        Init for Alts class

        Params:
         - bot (commands.Bot object) : This is our discord bot object.
         - username (string) : Details used to login.
         - password (string) : Details used to login.

        Optional Params:
         - channel (int) : Can be used to overide the default channel
                           specified in the config.json file as the
                           place to send chat messages to.
        """

        self.username = username
        self.password = password
        self.admins = ['Skelmis']
        self.loop = asyncio.get_event_loop()
        self.ingame = Ingame(bot)
        self.discord_bot = bot
        self.message_channel = channel or bot.channel

    def send_chat(self, message):
        """
        This sends a message packet to the connected server.

        Params:
         - message (string) : The message to send.
        """

        packet = serverbound.play.ChatPacket()
        packet.message = message
        self.connection.write_packet(packet)

    def connect(self, server):
        """
        The main method of the class. Estabhlishes and maintains a connection with a server.

        Params:
         - server (string) : The server to connect to.
        """

        match = re.match(r"((?P<host>[^\[\]:]+)|\[(?P<addr>[^\[\]]+)\])"
                         r"(:(?P<port>\d+))?$", server)
        if match is None:
            raise ValueError("Invalid server address: '%s'." % server)
        self.address = match.group("host") or match.group("addr")
        self.port = int(match.group("port") or 25565)

        auth_token = authentication.AuthenticationToken()
        try:
            auth_token.authenticate(self.username, self.password)
        except YggdrasilError as e:
            print(e)
            sys.exit()
        print("Logged in as %s..." % auth_token.username)
        self.connection = Connection(
            self.address, self.port, auth_token=auth_token)

        def handle_join_game(join_game_packet):
            print('Connected.')

        self.connection.register_packet_listener(
            handle_join_game, clientbound.play.JoinGamePacket)

        def print_chat(chat_packet):
            #global server_chat
            data = "{}" .format(chat_packet.json_data)
            data = data.replace("true", "True")
            data = data.replace("false", "False")
            data = data.replace("none", "None")
            data = eval(data)
            list = []
            #Mcc
            try:
                for key in range(len(data['extra'])):
                    try:
                        list.append(data['extra'][key]['text'])
                    except Exception as e:
                        print(e)
            except:
                pass
            try:
                list.append(data['extra'][3]['extra'][0]['text'])
            except:
                pass
            string = ' '.join(list)
            string = re.sub('\§c|\§f|\§b|\§d|\§a|\§1|\§2|\§3|\§4|\§5|\§6|\§7|\§8|\§9|\§0', '', string)

            try:
                found = re.search('(.+?)  has requested that you teleport to them.', string).group(1)
                if found in self.admins:
                    self.send_chat('/tpyes')
            except AttributeError:
                pass

            self.loop.create_task(self.ingame.SendChatToDiscord(self.message_channel, string))

        self.connection.register_packet_listener(
            print_chat, clientbound.play.ChatMessagePacket)

        self.connection.connect()

        while True:
            time.sleep(1)
            pass

    def QuietVerify(self, server):
        """
        Used to verify if an account works or not, silently.

        This function is essentially Alts.verify(), however it
        does it's work 'silently'. In that it simply returns
        True or False depending on the login status.
        Is used to test account status before attempting to
        establish an Alts.connect() call.

        Params:
         - server (string) : The server to connect to.

        Returns:
         - bool : True or false depending on login outcome

        Notes:
        Provided handling is setup within commands, this
        could easily be used to phase out Alts.verify().
        """

        match = re.match(r"((?P<host>[^\[\]:]+)|\[(?P<addr>[^\[\]]+)\])"
                         r"(:(?P<port>\d+))?$", server)
        if match is None:
            raise ValueError("Invalid server address: '%s'." % server)
        self.address = match.group("host") or match.group("addr")
        self.port = int(match.group("port") or 25565)

        auth_token = authentication.AuthenticationToken()
        try:
            auth_token.authenticate(self.username, self.password)
        except YggdrasilError as e:
            print(e)
            return False
        data = cogs._json.read_json('alts')
        data[self.username] = self.password
        cogs._json.write_json(data, 'alts')
        connection = Connection(
            self.address, self.port, auth_token=auth_token)

        connection.connect()
        connection.disconnect()
        return True

    def verify(self, server):
        """
        Used to verify if an account works or not.

        This is not a silently execution, depending on
        the outcome it will print a message to console.

        Params:
         - server (string) : The server to connect to.
        """

        match = re.match(r"((?P<host>[^\[\]:]+)|\[(?P<addr>[^\[\]]+)\])"
                         r"(:(?P<port>\d+))?$", server)
        if match is None:
            raise ValueError("Invalid server address: '%s'." % server)
        self.address = match.group("host") or match.group("addr")
        self.port = int(match.group("port") or 25565)

        auth_token = authentication.AuthenticationToken()
        try:
            auth_token.authenticate(self.username, self.password)
        except YggdrasilError as e:
            print(e)
            return
        data = cogs._json.read_json('alts')
        data[self.username] = self.password
        cogs._json.write_json(data, 'alts')
        connection = Connection(
            self.address, self.port, auth_token=auth_token)

        connection.connect()
        connection.disconnect()
        print(f"Successful login for: {self.username}")
        return


class Ingame(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def SendChatToDiscord(self, channel, message):
        channel = self.bot.get_channel(int(channel))
        await channel.send(f"```{message}```")

    @commands.Cog.listener()
    async def on_ready(self):
        print("Ingame Cog has been loaded\n-----")

    @commands.Cog.listener()
    async def on_connect(self):
        print("Attempting Mc connection.")
        await asyncio.sleep(10)
        loop = asyncio.get_event_loop()
        self.bot.account = Alts(self.bot, self.bot.username, self.bot.password)
        check = functools.partial(self.bot.account.QuietVerify, self.bot.server)
        loginReturn = await loop.run_in_executor(ThreadPoolExecutor(), check)
        if loginReturn == True:
            self.bot.account_dict[self.bot.username] = self.bot.account

            thing = functools.partial(self.bot.account.connect, self.bot.server)
            blockReturn = await loop.run_in_executor(ThreadPoolExecutor(), thing)

    @commands.command()
    @commands.is_owner()
    async def verify(self, ctx, *, args):
        """
        Takes a list of accounts in the supplied format and tests if they are
        'legit' or not. Output is saved in a json file.

        Format:
        account@gmail.com:Password
        account2@gmail.com:password
        """
        await ctx.message.delete()
        alts = args.split('\n')
        print(alts)
        message = await ctx.send(content="Starting testing on the supplied accounts")
        for account in alts:
            username, password = account.split(':')
            await message.edit(content=f'Testing: {username}')
            await CheckAlt(self.bot, username, password)
            await asyncio.sleep(2.5)
        await message.edit(content='Testing complete')

    @commands.command()
    @commands.is_owner()
    async def connect(self, ctx, username, password, channel=None):
        loop = asyncio.get_event_loop()
        if not channel:
            account = Alts(self.bot, username, password)
        else:
            account = Alts(self.bot, username, password, int(channel))

        check = functools.partial(account.QuietVerify, 'mc-central.net')
        loginReturn = await loop.run_in_executor(ThreadPoolExecutor(), check)
        if loginReturn == True:
            self.bot.account_dict[username] = account

            thing = functools.partial(account.connect, 'mc-central.net')
            blockReturn = await loop.run_in_executor(ThreadPoolExecutor(), thing)

    @commands.command()
    @commands.is_owner()
    async def accounts(self, ctx):
        accounts = ''
        for key in self.bot.account_dict:
            accounts += f'{key}\n'
        await ctx.send(f'`{accounts}`')

    @commands.command()
    @commands.is_owner()
    async def control(self, ctx, username, *, message):
        if not username in self.bot.account_dict:
            await ctx.send(f"`{username}` not in accounts currently logged in, please run the accounts command to see avaliable accounts to control")
            return
        account = self.bot.account_dict[username]
        loop = asyncio.get_event_loop()
        thing = functools.partial(account.send_chat, message)
        blockReturn = await loop.run_in_executor(ThreadPoolExecutor(), thing)
        await ctx.send(f"Getting account: `{username}`\nTo send the message: `{message}`")

    @commands.command()
    @commands.is_owner()
    @commands.cooldown(1, 1.5, commands.BucketType.default)
    async def send(self, ctx, *, message):
        loop = asyncio.get_event_loop()
        thing = functools.partial(self.bot.account.send_chat, message)
        blockReturn = await loop.run_in_executor(ThreadPoolExecutor(), thing)

    @commands.command()
    @commands.is_owner()
    @commands.cooldown(1, 1.5, commands.BucketType.default)
    async def reply(self, ctx, *, message):
        message = f'/r {message}'
        loop = asyncio.get_event_loop()
        thing = functools.partial(self.bot.account.send_chat, message)
        blockReturn = await loop.run_in_executor(ThreadPoolExecutor(), thing)

async def CheckAlt(bot, username, password):
    loop = asyncio.get_event_loop()
    account = Alts(bot, username, password)
    thing = functools.partial(account.verify, 'mc-central.net')
    blockReturn = await loop.run_in_executor(ThreadPoolExecutor(), thing)
    return

def setup(bot):
    bot.add_cog(Ingame(bot))
