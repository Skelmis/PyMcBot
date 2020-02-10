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

global server_chat
server_chat = ""

global ingame_commands
ingame_commands = "Placeholder"

connected = False

async def SendChat(self):
    print("Running send chat")
    channel = self.bot.get_channel(int(self.bot.channel))
    while True:
        global server_chat
        if not server_chat:
            pass
        else:
            if server_chat != 'Placeholder':
                await channel.send(f"```{server_chat}```")
            server_chat = ""
        await asyncio.sleep(0.5)

class Alts():

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.admins = ['Skelmis']

    def send_chat(self, message):
        packet = serverbound.play.ChatPacket()
        packet.message = message
        self.connection.write_packet(packet)

    def test():
        def testtwo():
            print("returns")

    def connect(self, server):

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
            data = cogs._json.read_json('alts')
            data[self.username] = self.password
            cogs._json.write_json(data, 'alts')

        self.connection.register_packet_listener(
            handle_join_game, clientbound.play.JoinGamePacket)

        def print_chat(chat_packet):
            global server_chat
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
            server_chat = server_chat + string + '\n'

            try:
                found = re.search('(.+?)  has requested that you teleport to them.', string).group(1)
                if found in self.admins:
                    self.send_chat('/tpyes')
            except AttributeError:
                pass

        self.connection.register_packet_listener(
            print_chat, clientbound.play.ChatMessagePacket)

        self.connection.connect()

        while True:
            time.sleep(1)
            pass


    def verify(self, server):
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
        self.chat_check_loop.start()

    def cog_unload(self):
        self.check_task.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        print("Ingame Cog has been loaded\n-----")

    @commands.Cog.listener()
    async def on_connect(self):
        print("Attempting Mc connection.")
        await asyncio.sleep(10)
        loop = asyncio.get_event_loop()
        self.bot.account = Alts(self.bot.username, self.bot.password)
        thing = functools.partial(self.bot.account.connect, self.bot.server)
        blockReturn = await loop.run_in_executor(ThreadPoolExecutor(), thing)

    @commands.command()
    async def checktest(self, ctx):
        #self.bot.account
        #thing = functools.partial(self.bot.account.test.testtwo, self.bot.server)
        loop = asyncio.get_event_loop()
        blockReturn = await loop.run_in_executor(ThreadPoolExecutor(), self.bot.account.test.testtwo)

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
            await CheckAlt(username, password)
            await asyncio.sleep(2.5)
        await message.edit(content='Testing complete')

    @commands.command()
    @commands.is_owner()
    async def connect(self, ctx, username, password):
        loop = asyncio.get_event_loop()
        account = Alts(username, password)
        thing = functools.partial(account.connect, 'mc-central.net')
        blockReturn = await loop.run_in_executor(ThreadPoolExecutor(), thing)

    @commands.command()
    @commands.is_owner()
    async def send(self, ctx, *, message):
        loop = asyncio.get_event_loop()
        thing = functools.partial(self.bot.account.send_chat, message)
        blockReturn = await loop.run_in_executor(ThreadPoolExecutor(), thing)

    @commands.Cog.listener()
    async def on_ready(self):
        await asyncio.sleep(15)
        print("Attempting to run send chat")
        await SendChat(self)

    @commands.command()
    @commands.is_owner()
    @commands.cooldown(1, 1.5, commands.BucketType.default)
    async def sudo(self, ctx, *, command):
        global ingame_commands
        if ingame_commands == "Placeholder":
            ingame_commands = command + '\n'
        else:
            ingame_commands = ingame_commands + commands + '\n'
        await ctx.send(f"Sudoing: `{command}`")

    @commands.command()
    @commands.is_owner()
    @commands.cooldown(1, 1.5, commands.BucketType.default)
    async def reply(self, ctx, *, command):
        global ingame_commands
        if ingame_commands == "Placeholder":
            ingame_commands = '/r ' + command + '\n'
        else:
            ingame_commands = ingame_commands + '/r ' + commands + '\n'
        await ctx.send(f"Replying: `{command}`")

    @loop(seconds=1)
    async def chat_check_loop(self):
        if self.bot.ingame_text != "Placeholder":
            global ingame_commands
            commandList = self.bot.ingame_text.split("\n")
            for command in commandList:
                if ingame_commands == "Placeholder":
                    ingame_commands = command + '\n'
                else:
                    ingame_commands = ingame_commands + command + '\n'
            self.bot.ingame_text = "Placeholder"

    @chat_check_loop.before_loop
    async def before_chat_check_loop(self):
        await self.bot.wait_until_ready()

async def CheckAlt(username, password):
    loop = asyncio.get_event_loop()
    account = Alts(username, password)
    thing = functools.partial(account.verify, 'mc-central.net')
    blockReturn = await loop.run_in_executor(ThreadPoolExecutor(), thing)
    return

def setup(bot):
    bot.add_cog(Ingame(bot))
