# Cinnamon bot v2.5.3 for discord, written by Viv, last update Aug 30, 2023 (hotfix to make /solve slightly less insecure)
cinnamonVersion = "2.5.3"
description = "Multi-purpose bot that does basically anything I could think of"

# changelog in README.txt
# todo: time and datetime usage is redundant, remove one
# todo: this line exists in README.txt, fix that:
#      - Once you somehow gotten this file and invited the bot to your server, if for some reason it is not nicknamed "cinnamon", fix that, as some commands are otherwise recursive
# todo: make "cinnamon, cat" work

cinPalette = {
    "regular": "\033[38:5:182m",
    "header": "\033[38:5:170m",
    "misc": "\033[0m \033[37m",
    "highlighted": "\033[0m \033[38:5:39m"
}



# !!!~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~[START DEFINITIONS & IMPORTS]

import platform

import os
os.system("color")
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
from discord.ext import commands, tasks

import random
import re

import cinDice
import cinLogging # logging import changed to only import warning to prevent confusion here

import subprocess
import sys

import math



def loadConfig(name: str):
    # todo: DRY
    return json.load(open(os.path.join(os.path.dirname(__file__), str("configs\\" + name))))

def loadCache(name: str):
    return json.load(open(os.path.join(os.path.dirname(__file__), str("cache\\" + name))))


client = discord.Client(intents=discord.Intents.all())

playlistURLs = []
attachments = ""
prevMessage = ""
messageContent = ""
initTime = datetime.now().replace(microsecond=0)
initTimeSession = datetime.now().replace(microsecond=0)
Nope = 0


cinMcFolder = os.path.join(os.path.dirname(__file__), str("minecraft\\"))
mcServer = None


relativeTimeRegex = r"([\d]+[hdmsMyY])"
urlRegex = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
youtubeUrlRegex = r'watch\?v=\S+?list='

badParenthesisRegex = r"\(([ \t\n])*(-)*([ \t\n\d])*\)" #catches parenthesis that are empty, or contain only a number, including negative numbers


# !!!~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~[END DEFINITIONS & IMPORTS]
# !!!~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~[START CONFIG]


simpleResponses = loadConfig("simpleResponses.json")

config = loadConfig("config.json")
token = loadConfig("token.json")["token"]
strings = loadConfig("strings.json")
minecraftConfig = loadConfig("minecraft.json")

reminders = loadCache("reminders.json")

bot_prefix = config["prefix"]
badEvalWords = config["badEvalWords"]
adminGuild = config["adminGuild"]

def joinWithGlobalVars(textsToJoin):
    # todo: unsure if you can modify v directly in `for v in table:` in python, figure that out & apply here if relevant
    for i in range(len(textsToJoin)):
        if textsToJoin[i] in globals():
            textsToJoin[i] = globals()[textsToJoin[i]]
    return "".join(textsToJoin)


#pre-processes any relevant configs
def processConfigs():
    strings['help']['guildIsNotAdminGuildMsg'] = joinWithGlobalVars(strings['help']['guildIsNotAdminGuildMsg'])
processConfigs()


# !!!~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~[END CONFIG]
# !!!~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~[START REMINDME]
def overwriteCache(name: str, newData):
    
    thisCachePath = os.path.join(os.path.dirname(__file__), str("cache\\" + name))

    os.remove(thisCachePath)
    with open(thisCachePath, 'w') as f:
        json.dump(newData, f, indent=4)

    
    #with open(thisCachePath, 'r+') as f:
     #   f.seek(0)  # <--- should reset file position to the beginning.
     #   json.dump(newData, f, indent=4)
     #   f.truncate()

def relativeTimeToSeconds(relativeTimes):
    minuteInSeconds = 60
    hourInSeconds = minuteInSeconds*60
    dayInSeconds = hourInSeconds*24
    weekInSeconds = dayInSeconds*7
    monthInSeconds = dayInSeconds*30.4 #todo: be smarter than this
    yearInSeconds = dayInSeconds*365

    totalRelativeTime = 0
    for v in relativeTimes:
        timeFlavor = v[-1]#the letter specifying which type of time unit is being specified
        timeUnitsStr = v[0:-1]
        print(timeUnitsStr)
        print(timeFlavor)
        timeUnits = int(timeUnitsStr)
        if timeFlavor == "s":
            print(timeUnitsStr+" seconds")
            totalRelativeTime += timeUnits
        elif timeFlavor == "m":
            print(timeUnitsStr+" minutes")
            totalRelativeTime += timeUnits * minuteInSeconds
        elif timeFlavor == "h":
            print(timeUnitsStr+" hours")
            totalRelativeTime += timeUnits * hourInSeconds
        elif timeFlavor == "d":
            print(timeUnitsStr+" days")
            totalRelativeTime += timeUnits * dayInSeconds
        elif timeFlavor == "w":
            print(timeUnitsStr+" weeks")
            totalRelativeTime += timeUnits * weekInSeconds
        elif timeFlavor == "y":
            print(timeUnitsStr+" years")
            totalRelativeTime += timeUnits * yearInSeconds

    print(totalRelativeTime)
    return totalRelativeTime
    
def getTimeAndReminderText(args):
    reminderText = ""

    relativeSyntaxRegex = re.compile(relativeTimeRegex)
    relativeTimesWithIndices = relativeSyntaxRegex.finditer(args[0])
    relativeTimes = []
    for v in relativeTimesWithIndices:
        relativeTimes.append(v.group())

    print(relativeTimes)

    if len(relativeTimes) > 0:
        totalRelativeTime = relativeTimeToSeconds(relativeTimes)
        if len(args) > 1:
            reminderText = " ".join(args[1:])
    else:
        print("len(relativeTimes) <= 0")

    return [totalRelativeTime, reminderText]

def newReminder(args, message):
    thisReminder = {}
    thisReminder["userID"] = message.author.id
    timeAndReminderText = getTimeAndReminderText(args)

    thisTime = int(time.time() + timeAndReminderText[0])
    thisReminder["text"] = timeAndReminderText[1]
    thisReminder["channelID"] = message.channel.id

    reminders[str(thisTime)] = thisReminder
    overwriteCache("reminders.json", reminders)

async def handleReminders():
    checkingTime = time.time() + 1  # check 1 second ahead bc ping
    closestReminderTime = 999999999999

    keysToRemove = []

    for key in reminders:
        thisReminderTime = int(key)
        if thisReminderTime < checkingTime:
            # remind

            keysToRemove.append(key)
            thisReminder = reminders[key]

            channel = client.get_channel(thisReminder["channelID"])
            messageText = f'Yo <@{thisReminder["userID"]}> you asked me to remind you about some kinda "{thisReminder["text"]}" right about now.. or whatever that means'
            await channel.send(messageText)
        elif thisReminderTime-checkingTime < closestReminderTime:
            closestReminderTime = thisReminderTime-checkingTime

    if len(keysToRemove) > 0:
        for v in keysToRemove:
            del reminders[v]
        overwriteCache("reminders.json", reminders)
    print(f"next reminder is in {math.floor(closestReminderTime/60)} minutes {math.floor(closestReminderTime%60)} seconds")

# !!!~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~[END REMINDME]

def getURLs(string):
    return re.findall(urlRegex, string)


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
        regexString = re.compile(youtubeUrlRegex + playlistID)
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
    isFromAdminGuild = adminGuild == message.guild.id

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
        if isFromAdminGuild:
            myCharOffset = [15, 1]
            if "cinnamon, eval(" in messageContent.lower():
                myCharOffset = [15, 1]
            else:
                myCharOffset = [7, 0]
            
            textToEval = messageContent[myCharOffset[0]:len(messageContent) - myCharOffset[1]]
            
            # check if eval contains bad words OR parenthesis with only whitespace
            containsBadParenthesis = re.findall(badParenthesisRegex, textToEval)
            containsBadWords = containsAny(textToEval, badEvalWords)
            containsBadWords = containsBadWords or containsEmptyParenthesis
        
            if containsBadWords:
                await message.channel.send("fuck you. (noticed bad keywords in eval)")
            else:

                evalResult = None
                try:
                    evalResult = eval(textToEval)
                except Exception:
                    evalResult = "snake said no (python couldn't resolve eval)"

                await message.channel.send(evalResult)
            messageContent = ""
        else:
            await message.channel.send(strings['help']['guildIsNotAdminGuildMsg'])

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
    global mcServer
    isFromAdminGuild = adminGuild == message.guild.id
    words = messageContent.lower().split(" ")

    # todo: move this to logging module
    print(f"  {cinPalette['header']}{str(time.strftime('%a, %d %b %Y %H:%M:%S +0000', time.gmtime()))}")
    print(f"    !!>{message.author.display_name}: {cinPalette['highlighted']}{messageContent}\n")

    # commands that can't be processed by discord's command api, because it is crap (as of 5 years ago, I have not checked this since). Oh, wait, it's all the commands. huh.
    # todo: switch case this bish
    if words[0] == bot_prefix+"help":
        await message.channel.send("https://htmlpreview.github.io/?https://github.com/Vivian-Green/cinnamon-py/blob/main/assets/Cinnamon%20Bot%20Help.html")
        # await message.channel.send(file=discord.File(str(os.path.join(os.path.dirname(__file__), str("assets\\Cinnamon Bot Help.html")))))
    if words[0] == bot_prefix+"getlog":
        await message.author.send(file=discord.File(str(os.path.join(os.path.dirname(__file__), str("logs\\" + str(message.guild) + "\\")) + str(message.channel) + '.html')))
        await message.channel.send("Check your DM's!")
    if words[0] == bot_prefix+"test":
        await message.channel.send("Hey, you're not a doofus! Good job, you!")
    if words[0] == bot_prefix+"goodbot":
        await message.channel.send(("Arigatogozaimasu, " + message.author.display_name + "-sama! >.<"))

    if words[0] == bot_prefix+"runtime":
        await sendRuntime(message)

    if words[0] == bot_prefix+"remindme":
        newReminder(words[1:], message)
        await message.channel.send("I'll remind you of... that... then... yeah.")


    if words[0] == bot_prefix+"guildid":
        await message.channel.send(f"this guild: {str(message.guild.id)}\nadmin guild: {adminGuild}")

    if words[0] == bot_prefix+"dox":
        if isFromAdminGuild:
            ip = get('https://api.ipify.org').content.decode('utf8')
            await message.channel.send(f"My public IP address is: {ip}")
        else:
            await message.channel.send(strings['help']['guildIsNotAdminGuildMsg'])
            
    if words[0] == bot_prefix+"version":
        await message.channel.send(f"cinnamon: {cinnamonVersion}\ndiscord: {discord.__version__}\npython: {platform.python_version()}")

    #words is messageContent.lower().split(" ")
    if words[0] == bot_prefix+"minecraft":
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
                mcServer = subprocess.Popen(mcServerBatch, stdin=asyncio.subprocess.PIPE)#, stdout=subprocess.PIPE)
                print("Server started.")

        if words[1] == "command":
            mcCommand = "".join(words[2:])
            if mcServer is not None:
                stdout, stderr = await mcServer.communicate(f"{mcCommand}\n".encode())
                print(f"stdin: `{mcCommand}\n`")
            else:
                await message.channel.send("mcServer is None")
                # todo: err of mc server isn't started


class Main:
    @client.event
    async def on_ready():

        global initTimeSession

        print(f"\n\n\n\n\n{cinPalette['highlighted']}Login Successful!{cinPalette['header'] + ''} \n  Name:{cinPalette['highlighted'] + ''}{client.user.name} \n{cinPalette['header'] + ''}  ID: {cinPalette['highlighted']}{client.user.id}")
        print(cinPalette['header'], " Discord.py version:", cinPalette['highlighted'], discord.__version__, cinPalette['header'], "\n  Cinnamon version:", cinPalette['highlighted'], cinnamonVersion)
        print("\n\n\n\n\n")
        initTimeSession = datetime.now().replace(microsecond=0)
        await client.change_presence(activity=discord.Game('Call me cinnamon'))

        mainLoop.start()

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

@tasks.loop(seconds = 5)
async def mainLoop():

    debugSettings = {
        "doMcLoop": True,
        "doReminders": True
    }
    # started after client on_ready event
    if debugSettings["doMcLoop"]:
        await mcLoop()
    if debugSettings["doReminders"]:
        #todo: use event structure for this instead of taping things to a loop
        
        await handleReminders()

client.run(token)

#asyncio.run(mainLoop())
#asyncio.run(discordLoop())

#print("starting cinnamon:")
#client.run(token)


