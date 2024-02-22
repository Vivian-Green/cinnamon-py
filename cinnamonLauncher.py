print("cinLauncher started")

import asyncio
import discord
import discord.ext
import subprocess
import time

from cinIO import config, token

mainExecutable = False
client = discord.Client(intents=discord.Intents.all())
bot_prefix = config["prefix"]

def startMainBot():
    global mainExecutable
    if mainExecutable:
        mainExecutable.kill()
    mainExecutable = subprocess.Popen(["startMainBot.bat"])

@client.event
async def on_ready():
    print("cinRebooter session started!")
    startMainBot()

@client.event
async def on_error(self, event):
    print(event)

@client.event
async def on_message(message: discord.message):
    words = message.content.lower().split(" ")
    if words[0] == "!>reboot" and config["adminGuild"] == message.guild.id:
        await message.channel.send("rebooting...")
        startMainBot()

client.run(token)

