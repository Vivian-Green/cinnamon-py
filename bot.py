# Cinnamon bot v2.4.1 for discord, written by Viv, last update Aug 20, 2023 (create strings.json and more refactoring)
cinnamonVersion = "2.4.1"
description = "Multi-purpose bot that does basically anything I could think of"

# changelog in README.txt
# todo: time and datetime usage is redundant, remove one
# todo: this line exists in README.txt, fix that:
#      - Once you somehow gotten this file and invited the bot to your server, if for some reason it is not nicknamed "cinnamon", fix that, as some commands are otherwise recursive
# todo: make "cinnamon, cat" work

# !!!~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~[START DEFINITIONS & IMPORTS]

import os
import os.path
import json

from logging import warning
import traceback

import urllib.request
import urllib.error

import time
from datetime import datetime

import asyncio
import discord
import discord.ext

import random
import re

import cinDice
import cinLogging # logging import changed to only import warning to prevent confusion here


def loadConfig(name: str):
    return json.load(open(os.path.join(os.path.dirname(__file__), str("configs\\" + name))))


client = discord.Client(intents=discord.Intents.all())

playlistURLs = []
attachments = ""
prevMessage = ""
messageContent = ""
initTime = datetime.now().replace(microsecond=0)
initTimeSession = datetime.now().replace(microsecond=0)
Nope = 0

simpleResponses = loadConfig("simpleResponses.json")

config = loadConfig("config.json")
token = loadConfig("token.json")["token"]
strings = loadConfig("strings.json")
badEvalWords = config["badEvalWords"]
bot_prefix = config["prefix"]

# !!!~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~[END DEFINITIONS & IMPORTS]


def getURLs(string):
    return re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', string)


def ytCrawl(url):
    global playlistURLs
    playlistURLs = []

    if 'list=' in url:
        playlistIDStart = url.rfind('=') + 1
        playlistID = url[playlistIDStart:]

        try:
            yTube = urllib.request.urlopen(url).read()
            strYTube = str(yTube)
        except urllib.error.URLError as e:
            print(e.reason)
            return

        # regexString matches for everything after & including the "watch" section of every URL, but ONLY if the end of the URL contains the link to the playlist.
        # EG: 'watch\?v=\S+?list=PLjaVZb8USBJOZkP-6swJPBsat8T34NlLa'
        regexString = re.compile(r'watch\?v=\S+?list=' + playlistID)
        allLinkWatchSections = re.findall(regexString, strYTube)

        if not allLinkWatchSections:
            return

        playlistURLs = []
        for watchSection in allLinkWatchSections:
            watchSection = str(watchSection)

            if not '\\\\u0026' in watchSection:
                return

            yPL_amp = watchSection.index('\\\\u0026')

            playlistURLs.append('https://www.youtube.com/' + watchSection[:yPL_amp])
            if not str('https://www.youtube.com/' + watchSection[:yPL_amp]) in playlistURLs:
                playlistURLs.append(
                    str('https://www.youtube.com/' + watchSection[:yPL_amp]))

    return playlistURLs


def containsAny(textToCheck: str, texts):
    # if textToCheck contains any of texts, return the length of the matching text, which is truthy unless text is ""
    # else, return false
    for text in texts:
        if text in textToCheck.lower():
            return len(text)
    return False


async def sendRuntime(message: object):
    global initTime
    global initTimeSession
    rn = datetime.now().replace(microsecond=0)
    timeDeltaSession = (rn - initTimeSession)
    timeDelta = (rn - initTime)

    await message.channel.send(f"this discord session runtime: {str(timeDeltaSession)} \ncinnamon runtime: {str(timeDelta)}")


async def handleSimpleResponses(message):
    global messageContent

    for key, value in simpleResponses.items():
        if value[0] == "raw":
            response = value[2]
        elif value[0] == "eval":
            first = value[2][0]
            second = eval(value[2][1])
            third = value[2][2]
            response = "".join([first, str(second), third])
        else:
            continue

        if value[1] == "contains":
            if key.lower() in messageContent.lower():
                await message.channel.send(response)
                break
        elif value[1] == "eval":
            if eval(key):
                await message.channel.send(response)
                break


async def rickRoll(message: object):
    for i in range(6):
        await message.channel.send(strings["rickroll"]["texts"][i])


async def handlePrompts(message: object):
    global Nope
    global messageContent

    await handleSimpleResponses(message)

    if containsAny(messageContent, strings["sleepTexts"]["any"]):
        # prompts that make cinnamon go away
        if "cinnamon, be silenced" in messageContent.lower():
            await message.channel.send("Hai!")
            Nope = 5
        if containsAny(messageContent, strings["sleepTexts"]["goodNight"]):
            await message.channel.send("Jyaa ne!! ***bows***")
            Nope = 50
        if containsAny(messageContent, strings["sleepTexts"]["kys"]):
            await message.channel.send("a'k!")  # Sequential art, scarlet
            Nope = 5000

    if containsAny(messageContent, ["cinnamon, say", "cinnamon say"]):
        startChar = containsAny(messageContent, ["cinnamon, say", "cinnamon say"]) + 1
        await message.delete()
        await message.channel.send((messageContent[startChar:len(messageContent)]))

    if "cinnamon, conversation starter" in messageContent.lower():
        with open(os.path.join(os.path.dirname(__file__), str("assets\\conversation starters.txt")), "r") as file:
            conversationStarters = file.readlines()
            await message.channel.send((conversationStarters[random.randint(0, len(conversationStarters) - 1)]))

    if "cinnamon, cat" in messageContent.lower():
        await message.channel.send("I can't find a good image scraper for 100's of cat pictures ;-;")
        # os.listdir(os.path.join(os.path.dirname(__file__), str("assets\\cats")))
        # await message.channel.send( file=discord.File(os.path.join(os.path.dirname(__file__), str("assets\\cats\\"))+os.listdir(os.path.join(os.path.dirname(__file__), str("assets\\cats")))[random.randint(0, len(os.listdir(os.path.join(os.path.dirname(__file__), str("assets\\cats")))))]);

    if "cinnamon, rick roll" in messageContent.lower() or "cinnamon, rickroll" in messageContent.lower():  # Never gonna give you up!
        await rickRoll(message)

    if "cinnamon, lovecalc" in messageContent.lower():
        # every line of this before embed.set_footer used to be a single line.
        # the singular line had two unnecessary and identical re.match calls.
        # the singular line utilized base 36 in 3 separate places, which change nothing about how it functioned.
        # the singular line fucked my dog and ate my wife.
        # I don't know what I was doing there.
        # I don't think I ever knew what I was doing there.

        words = messageContent.split(" ")
        embedTitle = f"**:heart: Love calculation for {words[2]} and {words[3]}**:"

        # trim <@> from tags before XORing their ID's
        firstUserID = int(words[2][2:-1])
        secondUserID = int(words[3][2:-1])
        embedDesc = f"Percentage: {(firstUserID + secondUserID) % 101}%"

        embed = discord.Embed(
            title=embedTitle,
            description=embedDesc,
            color=0xff7979
        )
        embed.set_footer(text="(don't take this seriously, you can bang anyone (with consent))")

        await message.channel.send(embed=embed)

    if "cinnamon, ping" in messageContent.lower():
        t1 = time.perf_counter()
        await client.send_typing(message.channel)
        t2 = time.perf_counter()

        embed = discord.Embed(
            title=None,
            description=f'Ping: {round((t2 - t1) * 1000)}ms',
            color=0x2874A6
        )
        await message.channel.send(embed=embed)

    if "cinnamon, runtime" in messageContent.lower():
        await sendRuntime(message)

    if "cinnamon, eval(" in messageContent.lower() or "/solve " in messageContent.lower():
        if containsAny(messageContent, badEvalWords):
            await message.channel.send("fuck you. (noticed bad keywords in eval)")
        else:
            myCharOffset = [15, 1]
            if "cinnamon, eval(" in messageContent.lower():
                myCharOffset = [15, 1]
            else:
                myCharOffset = [7, 0]

            evalResult = None
            try:
                evalResult = eval(messageContent[myCharOffset[0]:len(messageContent) - myCharOffset[1]])
            except Exception:
                evalResult = "snake said no (python couldn't resolve eval)"

            await message.channel.send(evalResult)
        messageContent = ""

    if "ytplaylist" in messageContent.lower():
        print(messageContent)
        try:
            await message.channel.send("idk why you would want this, it's kind of a debug function, but sure")
            await message.channel.send(ytCrawl("".join(getURLs(messageContent)[0])))
        except Exception:
            await message.channel.send("failed to send URLs, were there too many URLs in the playlist to send? Char limit is 2000")

    if "roll " in messageContent.lower():
        startOfRollText = messageContent.lower().find("roll ")
        rollCommandText = messageContent.lower()[startOfRollText:len(messageContent.lower())]

        response = cinDice.roll(rollCommandText, message)
        await message.channel.send(response)

    if "lewdsign" in messageContent.lower() or "lewd sign" in messageContent.lower() or "lewd_sign" in messageContent.lower():
        await message.channel.send(file=discord.File(str(os.path.join(os.path.dirname(__file__), str("assets\\lewdSign\\") + str(random.randint(0, 13)) + ".png"))))


async def handleRegularMessage(message: object):
    global messageContent
    global Nope

    await cinLogging.tryToLog(message)
    ImAwakeAndNotTalkingToABot = Nope <= 0 and not message.author.bot

    if ImAwakeAndNotTalkingToABot:
        await handlePrompts(message)
    else:
        # sleepy prompts
        Nope -= 1
        if containsAny(messageContent, ["good morning, cinnamon", "good morning cinnamon"]):
            await message.channel.send("Ohayogozaimasu...")
            Nope = 0  # release the kraken
        if "arise, cinnamon" in messageContent.lower():
            await message.channel.send("'mornin'!")
            Nope = 0


async def handleCommand(message: object):
    global messageContent

    print("  " + str(time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())))
    print("    !!>" + message.author.display_name + ": " + messageContent + "\n")

    # commands that can't be processed by discord's command api, because it is crap (as of 5 years ago, I have not checked this since). Oh, wait, it's all the commands. huh.
    if messageContent.lower().startswith(bot_prefix+"help"):
        await message.channel.send("https://htmlpreview.github.io/?https://github.com/Vivian-Green/cinnamon-py/blob/main/assets/Cinnamon%20Bot%20Help.html")
        # await message.channel.send(file=discord.File(str(os.path.join(os.path.dirname(__file__), str("assets\\Cinnamon Bot Help.html")))))
    if messageContent.lower().startswith(bot_prefix+"getlog"):
        await message.author.send(file=discord.File(str(os.path.join(os.path.dirname(__file__), str("logs\\" + str(message.guild) + "\\")) + str(message.channel) + '.html')))
        await message.channel.send("Check your DM's!")
    if messageContent.lower().startswith(bot_prefix+"test"):
        await message.channel.send("Hey, you're not a doofus! Good job, you!")
    if messageContent.lower().startswith(bot_prefix+"goodbot"):
        await message.channel.send(("Arigatogozaimasu, " + message.author.display_name + "-sama! >.<"))
    if messageContent.lower().startswith(bot_prefix+"runtime"):
        await sendRuntime(message)


class Main:
    @client.event
    async def on_ready():
        global initTimeSession

        print(f"\n\n\n\n\nLogin Successful!\nName: {client.user.name} \nID: {client.user.id}")
        print("Discord.py version:", discord.__version__, "\nCinnamon version:", cinnamonVersion)
        print("\n\n\n\n\n")
        initTimeSession = datetime.now().replace(microsecond=0)
        await client.change_presence(activity=discord.Game('Call me cinnamon'))

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
        except Exception:
            print(strings["errors"]["failedToSendErr"])

    @client.event
    async def on_message(message):
        global messageContent
        global prevMessage
        messageContent = message.content

        # If command (still within on_message)
        if messageContent.startswith(bot_prefix):
            await handleCommand(message)
        else:  # If not command (commands aren't really used anymore, but they are still supported)
            await handleRegularMessage(message)

        # store this message if I ever have any function that requires the use of 2 messages back
        prevMessage = message


loop = asyncio.get_event_loop()

client.run(token)
