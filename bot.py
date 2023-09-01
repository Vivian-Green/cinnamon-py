# Cinnamon bot v2.6.0 for discord, written by Viv, last update Sept 1, 2023 (added whitelist /solve implementation by https://github.com/Koenig-Heinrich-der-4te )
cinnamonVersion = "2.6.0"
description = "Multi-purpose bot that does basically anything I could think of"

# changelog in README.txt
# todo: this line exists in README.txt, fix that:
#      - Once you somehow gotten this file and invited the bot to your server, if for some reason it is not nicknamed "cinnamon", fix that, as some commands are otherwise recursive
# todo: migrate README.txt to README.md
# todo: read all of this code & ensure "Cinnamon Bot Help.html" is up to date
# todo: find mystery crash cause, re-enable minecraft features
# todo: figure out how to get logging colors to work in console, not just in pycharm
# todo: make reminders embeds
# todo: rename Nope variable to something more descriptive
# todo: make reminders cache if it doesn't exist
# todo: move configs to yaml?

cinPalette = {
    "regular": "\033[38:5:182m",
    "header": "\033[38:5:170m",
    "misc": "\033[0m \033[37m",
    "highlighted": "\033[0m \033[38:5:39m"
}
debugSettings = {
    "doMc": False,
    "doReminders": True
}

# !!!~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~[START DEFINITIONS & IMPORTS]

import platform
import os
import os.path
os.system("color")

from logging import warning
import traceback

import time
from datetime import datetime

import asyncio
import discord
import discord.ext
from discord.ext import tasks

import random
import subprocess
import math



import cinDice
import cinLogging # logging import changed to only import warning to prevent confusion here
from cinSolve import solve
from cinShared import *
from cinReminders import newReminder, getReminderStatus
import cinPromptFunctions
from cinIO import config, strings, simpleResponses, minecraftConfig, token, conversationStarters



client = discord.Client(intents=discord.Intents.all())

playlistURLs = []
initTime = datetime.now().replace(microsecond=0)
initTimeSession = datetime.now().replace(microsecond=0)
Nope = 0

cinMcFolder = os.path.join(os.path.dirname(__file__), str("minecraft\\"))
mcServer = None

youtubeUrlRegex = r'watch\?v=\S+?list='

badParenthesisRegex = r"\(([ \t\n])*(-)*([ \t\n\d])*\)" #catches parenthesis that are empty, or contain only a number, including negative numbers

bot_prefix = config["prefix"]
adminGuild = config["adminGuild"]
loopDelay = config["loopDelay"]
bigNumber = config["bigNumber"]

# !!!~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~[END DEFINITIONS & IMPORTS]

async def sendRuntime(message: discord.message):
    global initTime
    global initTimeSession
    rn = datetime.now().replace(microsecond=0)
    timeDeltaSession = (rn - initTimeSession)
    timeDelta = (rn - initTime)

    await message.channel.send(f"this discord session runtime: {str(timeDeltaSession)} \ncinnamon runtime: {str(timeDelta)}")



async def handleSimpleResponses(message, messageContent):
    for key, value in simpleResponses.items():
        sendResponse = False
        if value[1] == "contains":
            if key.lower() in messageContent.lower():
                sendResponse = True
        elif value[1] == "eval":
            if eval(key):
                sendResponse = True

        if sendResponse:
            if value[0] == "raw":
                response = value[2]
            elif value[0] == "eval":
                first = value[2][0]
                second = eval(value[2][1])
                third = value[2][2]
                response = "".join([first, str(second), third])
            else:
                continue

            await message.channel.send(response)
            break

async def handlePrompts(message: discord.message, messageContent):
    global Nope

    await handleSimpleResponses(message, messageContent)

    if "cinnamon, lovecalc" in messageContent.lower():
        await cinPromptFunctions.lovecalc(message, messageContent)
    if "cinnamon, rick roll" in messageContent.lower() or "cinnamon, rickroll" in messageContent.lower():  # Never gonna give you up!
        await cinPromptFunctions.rickRoll(message)
    if containsAny(messageContent, strings["sleepTexts"]["any"]):
        await cinPromptFunctions.sleepPrompts(message, messageContent, Nope)

    if "/solve " in messageContent.lower() or "cinnamon, eval(" in messageContent.lower():
        await solve(message, messageContent)
    if "roll " in messageContent.lower():
        await cinDice.rollWrapper(message, messageContent)
    if "cinnamon, conversation starter" in messageContent.lower():
        await message.channel.send((conversationStarters[random.randint(0, len(conversationStarters) - 1)]))

    if containsAny(messageContent, ["cinnamon, say", "cinnamon say"]):
        startChar = containsAny(messageContent, ["cinnamon, say", "cinnamon say"]) + 1
        await message.delete()
        await message.channel.send((messageContent[startChar:len(messageContent)]))

    if "lewdsign" in messageContent.lower() or "lewd sign" in messageContent.lower() or "lewd_sign" in messageContent.lower():
        lewdSignPath = str(os.path.join(os.path.dirname(__file__), str("assets\\lewdSign\\") + str(random.randint(0, 13)) + ".png"))
        await message.channel.send(file=discord.File(lewdSignPath))

async def handleRegularMessage(message: discord.message, messageContent):
    global Nope

    await cinLogging.tryToLog(message)
    ImAwakeAndNotTalkingToABot = Nope <= 0 and not message.author.bot

    if ImAwakeAndNotTalkingToABot:
        await handlePrompts(message, messageContent)
    else:
        # sleepy prompts
        Nope -= 1
        if containsAny(messageContent, ["good morning, cinnamon", "good morning cinnamon"]):
            await message.channel.send("Ohayogozaimasu...")
            Nope = 0  # release the kraken
        if "arise, cinnamon" in messageContent.lower():
            await message.channel.send("'mornin'!")
            Nope = 0



async def mcCommand(message: discord.message, words):
    global mcServer

    if not debugSettings["doMc"]:
        return

    if words[1] == "help":
        await message.channel.send("current server: dev")

    if words[1] == "start":
        if mcServer:
            await message.channel.send("Server already started!")
            print("Server already started.")
        else:
            await message.channel.send("starting server...")
            # todo: add args to config
            mcServerBatch = f"""java -Xms2G -Xmx2G -XX:+UseG1GC -jar "{minecraftConfig['devServerPath']}\spigot.jar" nogui"""
            print(mcServerBatch)

            os.chdir(minecraftConfig["devServerPath"])
            mcServer = subprocess.Popen(mcServerBatch, stdin=asyncio.subprocess.PIPE)  # , stdout=subprocess.PIPE)
            print("Server started.")

    if words[1] == "command":
        mcCommandText = "".join(words[2:])
        if mcServer is not None:
            stdout, stderr = await mcServer.communicate(f"{mcCommandText}\n".encode())
            print(f"stdin: `{mcCommandText}\n`")
        else:
            await message.channel.send("mcServer is None")
            # todo: err if mc server isn't started

async def handleCommand(message, messageContent):
    global mcServer
    words = messageContent.lower().split(" ")

    print(f"  {cinPalette['header']}{str(time.strftime('%a, %d %b %Y %H:%M:%S +0000', time.gmtime()))}")
    print(f"    !!>{message.author.display_name}: {cinPalette['highlighted']}{messageContent}\n")

    if words[0] == bot_prefix+"ping":
        await cinPromptFunctions.ping(message)
    if words[0] == bot_prefix+"dox":
        await cinPromptFunctions.dox(message)

    if words[0] == bot_prefix+"help":
        await message.channel.send("https://htmlpreview.github.io/?https://github.com/Vivian-Green/cinnamon-py/blob/main/assets/Cinnamon%20Bot%20Help.html")
        # await message.channel.send(file=discord.File(str(os.path.join(os.path.dirname(__file__), str("assets\\Cinnamon Bot Help.html")))))
    if words[0] == bot_prefix+"getlog":
        await message.author.send(file=discord.File(str(os.path.join(os.path.dirname(__file__), str("logs\\" + str(message.guild) + "\\")) + str(message.channel) + '.html')))
        await message.channel.send("Check your DM's!")

    if words[0] == bot_prefix+"goodbot":
        await message.channel.send(("Arigatogozaimasu, " + message.author.display_name + "-sama! >.<"))

    if words[0] == bot_prefix+"runtime":
        await sendRuntime(message)
    if words[0] == bot_prefix+"guildid":
        await message.channel.send(f"this guild: {str(message.guild.id)}\nadmin guild: {adminGuild}")

    if words[0] == bot_prefix+"remindme":
        newReminder(words[1:], message)
        await message.channel.send("I'll remind you of... that... then... yeah.")

    if words[0] == bot_prefix+"version":
        await message.channel.send(f"cinnamon: {cinnamonVersion}\ndiscord: {discord.__version__}\npython: {platform.python_version()}")

    #words is messageContent.lower().split(" ")
    if words[0] == bot_prefix+"minecraft":
        await mcCommand(message, words)


# noinspection PyTypeChecker
class Main:
    @client.event
    async def on_ready():

        global initTimeSession

        print(f"\n\n\n\n\n{cinPalette['highlighted']}Login Successful!{cinPalette['header'] + ''} \n  Name:{cinPalette['highlighted'] + ''}{client.user.name} \n{cinPalette['header'] + ''}  ID: {cinPalette['highlighted']}{client.user.id}")
        print(cinPalette['header'], " Discord.py version:", cinPalette['highlighted'], discord.__version__, cinPalette['header'], "\n  Cinnamon version:", cinPalette['highlighted'], cinnamonVersion)
        print("\n\n\n\n\n")
        initTimeSession = datetime.now().replace(microsecond=0)
        #await client.change_presence(activity=discord.Game('Call me cinnamon'))

        try:
            nonDiscordLoop.start()
        except Exception as err:
            print(repr(err))
            print(traceback.format_exc())

    @client.event
    async def on_server_join(guild):
        await client.send_message(guild, "Hiya! you seem to have added me to your server! Thanks for that! ~<3")
        await client.send_message(guild, "try typing !>help for an in depth list of all the things I can do!")

    @client.event
    async def on_error(self, event):
        print(strings["errors"]["misc"])
        warning(traceback.format_exc())
        print(event)
        try:
            message = event[0]
            await message.channel.send(strings["errors"]["miscDisc"])
        except Exception as err:
            print(strings["errors"]["failedToSendErr"])
            print(repr(err))
            print(traceback.format_exc())

    @client.event
    async def on_message(message):
        messageContent = message.content

        # If command (still within on_message)
        if messageContent.startswith(bot_prefix):
            await handleCommand(message, messageContent)
        else:  # If not command (commands aren't really used anymore, but they are still supported)
            await handleRegularMessage(message, messageContent)


# noinspection PyUnresolvedReferences
async def mcLoop():
    if mcServer is not None:

        if mcServer.stdout is None:
            print("mcServer.stdout is None")
        else:
            # why does this stop the OTHER thread - the one handling the discord bot - from running??? they're separate threads-
            for line in mcServer.stdout:
                print(line)
                await asyncio.sleep(0.1)  # duct tape to break for other thread - does not work after mc finishes printing
    else:
        print("mcServer is None")



async def handleReminders():
    closestReminderTime, lateReminders = getReminderStatus()

    for reminder in lateReminders:
        channel = client.get_channel(reminder["channelID"])
        messageText = f'Yo <@{reminder["userID"]}> you asked me to remind you about some kinda "{reminder["text"]}" right about now.. or whatever that means'
        await channel.send(messageText)

    return closestReminderTime

lastStatusUpdateTime = 0
@tasks.loop(seconds = loopDelay)
async def nonDiscordLoop():
    global debugSettings
    global lastStatusUpdateTime

    # started after client on_ready event
    if debugSettings["doMc"]:
        await mcLoop()
    if debugSettings["doReminders"]:
        #todo: use event structure for this instead of taping things to a loop
        closestReminderTime = await handleReminders()
        if closestReminderTime != bigNumber:
            hours = math.floor(closestReminderTime / 3600)
            mins = math.floor((closestReminderTime / 60) % 60)
            secs = math.floor(closestReminderTime % 60)
            print(f"next reminder is in {hours}h {mins}m {secs}s")


    if time.time()-lastStatusUpdateTime > (60-loopDelay/2):
        lastStatusUpdateTime = time.time()

        #every minute, update status
        rn = datetime.now()
        thisHour = rn.hour
        thisMinute = rn.minute
        amOrPm = "am"
        if thisHour > 12:
            amOrPm = "pm"
            thisHour -= 12
        if thisHour == 0:
            thisHour = 12

        if thisMinute < 10:
            thisMinute = "".join(["0", str(thisMinute)])

        print(f"status updated at {thisHour}:{thisMinute}{amOrPm}")
        await client.change_presence(activity=discord.Game(f'online @{thisHour}:{thisMinute}{amOrPm} PST'))



client.run(token)