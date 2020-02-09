from __future__ import print_function

import getpass
import sys
import re
from optparse import OptionParser

from pyCraft.minecraft import authentication
from pyCraft.minecraft.exceptions import YggdrasilError
from pyCraft.minecraft.networking.connection import Connection
from pyCraft.minecraft.networking.packets import Packet, clientbound, serverbound
from pyCraft.minecraft.compat import input

import discord
from discord.ext import commands
from discord.ext.tasks import loop
import os
from concurrent.futures import ThreadPoolExecutor
import asyncio
import functools

import time

global server_chat
server_chat = ""

global ingame_commands
ingame_commands = "Placeholder"

connected = False

def IngameClient(username, password, server, dump_packets=False):
    match = re.match(r"((?P<host>[^\[\]:]+)|\[(?P<addr>[^\[\]]+)\])"
                     r"(:(?P<port>\d+))?$", server)
    if match is None:
        raise ValueError("Invalid server address: '%s'." % server)
    address = match.group("host") or match.group("addr")
    port = int(match.group("port") or 25565)

    auth_token = authentication.AuthenticationToken()
    try:
        auth_token.authenticate(username, password)
    except YggdrasilError as e:
        print(e)
        sys.exit()
    print("Logged in as %s..." % auth_token.username)
    connection = Connection(
        address, port, auth_token=auth_token)

    if dump_packets:
        def print_incoming(packet):
            if type(packet) is Packet:
                # This is a direct instance of the base Packet type, meaning
                # that it is a packet of unknown type, so we do not print it.
                return
            print('--> %s' % packet, file=sys.stderr)

        def print_outgoing(packet):
            print('<-- %s' % packet, file=sys.stderr)

        connection.register_packet_listener(
            print_incoming, Packet, early=True)
        connection.register_packet_listener(
            print_outgoing, Packet, outgoing=True)

    def handle_join_game(join_game_packet):
        print('Connected.')

    connection.register_packet_listener(
        handle_join_game, clientbound.play.JoinGamePacket)

    def print_chat(chat_packet):
        global server_chat
        data = "{}" .format(chat_packet.json_data)
        data = data.replace("true", "True")
        data = data.replace("false", "False")
        data = data.replace("none", "None")
        data = eval(data)
        list = []
        #Mc-central chat formatting
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

    connection.register_packet_listener(
        print_chat, clientbound.play.ChatMessagePacket)

    connection.connect()

    while True:
        try:
            global ingame_commands
            if ingame_commands != "Placeholder":
                commandList = ingame_commands.split('\n')
                for text in commandList:
                    if text == "/respawn":
                        print("respawning...")
                        packet = serverbound.play.ClientStatusPacket()
                        packet.action_id = serverbound.play.ClientStatusPacket.RESPAWN
                        connection.write_packet(packet)
                    else:
                        packet = serverbound.play.ChatPacket()
                        packet.message = text
                        connection.write_packet(packet)
            ingame_commands = "Placeholder"
        except:
            pass
        time.sleep(1)

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

class Ingame(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.chat_check_loop.start()

    def cog_unload(self):
        self.check_task.cancel()

    """
    I run the connect func within on_connect on the basis that the client has
    connected before the chat loop begins 15 seconds after on_ready for
    functional reasons at the time of implementation, may not be needed now.
    """

    @commands.Cog.listener()
    async def on_connect(self):
        print("Ingame Cog is ready, attempting Mc connection.")
        loop = asyncio.get_event_loop()
        thing = functools.partial(IngameClient, self.bot.username, self.bot.password, self.bot.server)
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

def setup(bot):
    bot.add_cog(Ingame(bot))
