import json
import difflib
import cinIO
print("bot started")
cinnamonVersion = "2.9.0"
description = "Multi-purpose bot that does basically anything I could think of"


# changelog in README.txt
# todo: this line exists in README.txt, fix that:
#      - Once you somehow gotten this file and invited the bot to your server, if for some reason it is not nicknamed "cinnamon", fix that, as some commands are otherwise recursive
# todo: migrate README.txt to README.md
# todo: read all of this code & ensure "Cinnamon Bot Help.html" is up to date
# todo: find mystery crash cause, re-enable minecraft features
# todo: rename Nope variable to something more descriptive
# todo: repeating reminders?
# todo: recomment. everything.

# todo: bug - absolute times are absolutely FUCKED
# todo: rework time system entirely

debugSettings = { # todo: what the FUCK is this doing in code
    "doMc": False,
    "doReminders": True
}

commandsList = [ # todo: what the FUCK is this doing in code, decouple and import from modules at least?
    "ping",
    "dox",
    "help",
    "getlog",
    "goodbot",
    "runtime",
    "guildid",
    "remindme",
    "reminder",
    "reminders",
    "version",
    "minecraft",
    "reboot",
    "set",
    "get",
    "cinloggingchannel",
    "podcast",
    "clip",
    "setclipfile",
    "getclips",
    "getallclips",
    "renderclips"
]

# !!!~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~[DEFINITIONS & IMPORTS]

import platform
import sys
import os
import os.path

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
import cinPromptFunctions
import cinLogging # logging import changed to only import warning to prevent confusion here
from cinLogging import printHighlighted, printDefault, printLabelWithInfo, printErr, printDebug
from cinSolve import solve
from cinShared import *
from cinReminders import newReminder, getReminderStatus, reminderMenu, getUserReminders, delReminderByTimestamp, handleReminderReaction, checkForReminders
from cinIO import config, strings, simpleResponses, minecraftConfig, token, conversationStarters, userData, getOrCreateUserData
from cinPalette import *
from cinYoinkytModule import setclipfile, clip, getClips, getAllClips, renderClips

os.system("color")



client = discord.Client(intents=discord.Intents.all())

playlistURLs = []
initTime = datetime.now().replace(microsecond=0)
initTimeSession = datetime.now().replace(microsecond=0)
Nope = 0

cinMcFolder = os.path.join(os.path.dirname(__file__), str("minecraft\\"))
mcServer = None

youtubeUrlRegex = r'watch\?v=\S+?list='
badParenthesisRegex = r"\(([ \t\n])*(-)*([ \t\n\d])*\)" # catches parenthesis that are empty, or contain only a number, including negative numbers

bot_prefix = config["prefix"]
adminGuild = config["adminGuild"]
loopDelay = config["loopDelay"]
bigNumber = config["bigNumber"]

lewdiasID = "617406542521696275"

clip_file_names = ""

print(f"cinnamon's timezone is: {time.timezone}")

# !!!~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~[I DON'T KNOW WHERE TO PUT THIS]

async def sendRuntime(message: discord.message):
    global initTime
    global initTimeSession
    rn = datetime.now().replace(microsecond=0)
    timeDeltaSession = (rn - initTimeSession)
    timeDelta = (rn - initTime)

    await message.channel.send(f"this discord session runtime: {str(timeDeltaSession)} \ncinnamon runtime: {str(timeDelta)}")


def download_audio(video_url):
    # download
    command = [
        'yt-dlp',
        '-f', 'bestaudio[ext=mp3]/bestaudio',
        '-o', f'yoinked.m4a',
        '--', video_url
    ]
    subprocess.run(" ".join(command), check=True)


# !!!~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~[REGULAR MESSAGE HANDLING]

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
    words = messageContent.lower().split(" ")

    compareText = messageContent.lower()
    if containsAny(compareText, ["cinnamon, slap", "cinnamon slap"]):
        await message.channel.send("***slaps***")
        if containsAny(compareText, ["lewdie", "lewdias", lewdiasID]):
            await message.channel.send("ow-", delete_after=2)

    if "cinnamon, lovecalc" in compareText:
        await cinPromptFunctions.lovecalc(message, messageContent)
    if containsAny(compareText, ["cinnamon, rick roll", "cinnamon, rickroll"]):  # Never gonna give you up!
        await cinPromptFunctions.rickRoll(message)
    if containsAny(messageContent, strings["sleepTexts"]["any"]):
        await cinPromptFunctions.sleepPrompts(message, Nope)

    if "/solve " in compareText or "cinnamon, eval(" in compareText:
        await solve(message, messageContent)
    if "roll " in compareText:
        await cinDice.rollWrapper(message, messageContent)
    if "clip" in compareText or ":" in compareText:
        await clip(words, message)
    if "cinnamon, conversation starter" in compareText:
        await message.channel.send((conversationStarters[random.randint(0, len(conversationStarters) - 1)]))

    if containsAny(messageContent, ["cinnamon, say", "cinnamon say"]):
        startChar = containsAny(messageContent, ["cinnamon, say", "cinnamon say"]) + 1
        await message.delete()
        await message.channel.send((messageContent[startChar:len(messageContent)]))

    if "lewdsign" in messageContent.lower() or "lewd sign" in messageContent.lower() or "lewd_sign" in messageContent.lower():
        lewdSignPath = str(os.path.join(os.path.dirname(__file__), str("assets\\lewdSign\\") + str(random.randint(0, 13)) + ".png"))
        await message.channel.send(file=discord.File(lewdSignPath))

async def handleRegularMessage(message: discord.message):
    global Nope
    messageContent = message.content

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

# !!!~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~[COMMAND HANDLING]

async def setCommand(message: discord.message):
    messageContent = message.content
    words = messageContent.lower().split(" ")
    args = words[1:]
    print(args)

    userIDStr = str(message.author.id)
    thisUserData = getOrCreateUserData(userIDStr) # make sure it exists

    if args[0] == "timezone":
        userData[userIDStr]["timezone"] = int(args[1])
        userTimeZone = userData[userIDStr]["timezone"]
        await message.channel.send(f"your timezone is now {userTimeZone}")

async def handleGetCommand(message: discord.message):
    messageContent = message.content
    words = messageContent.lower().split(" ")
    args = words[1:]
    print(args)

    userIDStr = str(message.author.id)
    thisUserData = getOrCreateUserData(userIDStr) # make sure it exists

    # usage: !>get timezone 5
    if args[0] == "timezone":
        await message.channel.send(f"your timezone is: {str(userData[userIDStr]['timezone'])}")


async def mcCommand(message: discord.message, words):
    global mcServer

    if not debugSettings["doMc"]:
        return

    if words[1] == "help":
        await message.channel.send("current server: dev")

    if words[1] == "start":
        if mcServer:
            await message.channel.send("Server already started!")
            printHighlighted("Server already started.")
        else:
            await message.channel.send("starting server...")
            # todo: add args to config
            mcServerBatch = f"""java -Xms2G -Xmx2G -XX:+UseG1GC -jar "{minecraftConfig['devServerPath']}\spigot.jar" nogui"""
            printDefault(mcServerBatch)

            os.chdir(minecraftConfig["devServerPath"])
            mcServer = subprocess.Popen(mcServerBatch, stdin=asyncio.subprocess.PIPE)  # , stdout=subprocess.PIPE)
            printHighlighted("Server started.")

    if words[1] == "command":
        mcCommandText = "".join(words[2:])
        if mcServer is not None:
            stdout, stderr = await mcServer.communicate(f"{mcCommandText}\n".encode())
            printDefault(f"stdin: `{mcCommandText}\n`")
        else:
            await message.channel.send("mcServer is None")
            # todo: err if mc server isn't started


async def handleCommand(message):
    global commandsList
    global mcServer
    messageContent = message.content
    words = messageContent.lower().split(" ")
    wordsCaseSensitive = messageContent.split(" ")

    printLabelWithInfo(time.strftime('%a, %d %b %Y %H:%M:%S +0000', time.gmtime()))
    printLabelWithInfo(f"  !!>{message.author.display_name}", messageContent)

    command = words[0][len(bot_prefix):]

    if command not in commandsList:
        printErr("command not in commandsList")
        return

    print(f"'{command}'")

    match command:
        case "cinloggingchannel":
            config["debugMessageChannelID"] = str(message.channel.id)
            cinIO.writeConfig("config.yaml", config)
            await message.channel.send("updated config")

        case "ping":
            await cinPromptFunctions.ping(message)

        case "dox":
            await cinPromptFunctions.dox(message)

        case "help":
            await message.channel.send("https://htmlpreview.github.io/?https://github.com/Vivian-Green/cinnamon-py/blob/main/assets/Cinnamon%20Bot%20Help.html")
            # await message.channel.send(file=discord.File(str(os.path.join(os.path.dirname(__file__), str("assets\\Cinnamon Bot Help.html")))))

        case "getlog":
            await message.author.send(file=discord.File(
                os.path.join(os.path.dirname(__file__), f"logs/{str(message.guild)}/{str(message.channel)}.html")
            ))
            await message.channel.send("Check your DM's!")

        case "goodbot":
            await message.channel.send(f"Arigatogozaimasu, {message.author.display_name}-sama! >.<")

        case "runtime":
            await sendRuntime(message)

        case "guildid":
            await message.channel.send(f"this guild: {str(message.guild.id)}\nadmin guild: {adminGuild}")

        case "remindme" | "reminder":
            await newReminder(wordsCaseSensitive[1:], message)

        case "reminders":
            await reminderMenu(message)

        case "set":
            await setCommand(message)

        case "get":
            await handleGetCommand(message)

        case "version":
            await message.channel.send(f"cinnamon: {cinnamonVersion}\ndiscord: {discord.__version__}\npython: {platform.python_version()}")

        case "minecraft":
            await mcCommand(message, words)

        case "!>reboot" if config["adminGuild"] == message.guild.id:
            sys.exit([0])

        case "setclipfile":
            await setclipfile(wordsCaseSensitive, message)
        case "getclips":
            await getClips(wordsCaseSensitive, message)
        case "getallclips":
            await getAllClips(message)
        case "renderclips":
            await renderClips(message)

        # Default case if no command matches
        case _:
            printErr(f"Unknown command {command}")


    if isinstance(message.channel, discord.DMChannel) and words[0] == "!>podcast":
        video_url = words[1]
        output_dir = 'downloads'
        os.makedirs(output_dir, exist_ok=True)

        try:
            download_audio(video_url)
            await message.channel.send(file=discord.File('yoinked.m4a'))
        except Exception as e:
            await message.channel.send(f"An error occurred: {str(e)}")

# !!!~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~[DISCORD EVENTS]

@client.event
async def on_ready():
    global initTimeSession
    initTimeSession = datetime.now().replace(microsecond=0)

    printHighlighted(f"{fiveLines}Login Successful!")
    printLabelWithInfo("  Name: ", client.user.name)
    printLabelWithInfo("  ID: ", client.user.id)
    printLabelWithInfo("  Discord.py version: ", discord.__version__)
    printLabelWithInfo("  Cinnamon version: ", cinnamonVersion)
    printDefault(fiveLines)

    # init second thread, if it is not already running
    try:
        nonDiscordLoop.start()
    except asyncio.CancelledError:
        printErr("Non-Discord loop is already running.")
    except Exception as err:
        printErr(repr(err))
        printErr(traceback.format_exc())

    if not (config["debugMessageChannelID"] is None):
        print(config["debugMessageChannelID"])
        debugMessageChannel = client.get_channel(int(config["debugMessageChannelID"]))
        await debugMessageChannel.send("cinnamon started!")

@client.event
async def on_server_join(guild):
    # todo: does this still work though
    await client.send_message(guild, "Hiya! you seem to have added me to your server! Thanks for that! ~<3")
    await client.send_message(guild, "try typing !>help for an in depth list of all the things I can do!")

@client.event
async def on_error(self, event):
    printErr(strings["errors"]["misc"])
    warning(traceback.format_exc())
    printErr(event)
    try:
        await event[0].channel.send(strings["errors"]["miscDisc"])
    except Exception as err:
        printErr(strings["errors"]["failedToSendErr"])
        printErr(repr(err))
        printErr(traceback.format_exc())

@client.event
async def on_message(message):
    if message.content.startswith(bot_prefix):
        await handleCommand(message)
    else:
        await handleRegularMessage(message)


@client.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    if not reaction.message.author.bot:  # todo: specifically check if the message is from cinnamon
        return

    if "reminder" in reaction.message.content.lower():
        await handleReminderReaction(reaction, user)


async def mcLoop():
    if mcServer is not None:

        if mcServer.stdout is None:
            printErr("mcServer.stdout is None")
        else:
            # why does this stop the OTHER thread - the one handling the discord bot - from running??? they're separate threads-
            for line in mcServer.stdout:
                printDefault(line)
                await asyncio.sleep(0.1)  # duct tape to break for other thread - does not work after mc finishes printing
    else:
        printDefault("mcServer is None")


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
        await checkForReminders(client)

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

        printHighlighted(f"status updated at {thisHour}:{thisMinute}{amOrPm}")
        await client.change_presence(activity=discord.Game(f'online @{thisHour}:{thisMinute}{amOrPm} PST'))



client.run(token)
