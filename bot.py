#    Cinnamon bot v2.3.1 for discord, written by Viv, last update Jul 19, 2023 (added runtime command & dedicated token config; cleanup)
cinnamonVersion = "2.3.1"
description = "Multi-purpose bot that does basically anything I could think of"

# changelog in README.txt
# todo: refactor.. comments.. to not be embarrasing if seen by a potential employer
# todo: move readme.txt to readme.md, and separate version history
# todo: time and datetime usage is redundant, remove one

# !!!~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~[START DEFINITIONS & IMPORTS]

import math
import time
import random
import traceback
import logging
import re
import os.path
import os
import urllib.request
import urllib.error
import asyncio
import discord
import discord.ext
import json

from datetime import datetime, timedelta

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
badEvalWords = config["badEvalWords"]
bot_prefix = config["prefix"]

defaultLoggingHtml = ""
with open(os.path.join(os.path.dirname(__file__), config["defaultLoggingHtml"]), "r") as defaultLoggingHtmlFile:
    defaultLoggingHtml = defaultLoggingHtmlFile.readlines()
    defaultLoggingHtmlFile.close()

# !!!~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~[END DEFINITIONS & IMPORTS]


def getURLs(string):
    return re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', string)

def hexToRGBA(hexValue, alpha):
    h = tuple(int(hexValue.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))
    return "rgba(" + str(h[0]) + ", " + str(h[1]) + ", " + str(h[2]) + ", " + str(alpha) + ")"

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
                playlistURLs.append(str('https://www.youtube.com/' + watchSection[:yPL_amp]))

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

    await message.channel.send("this discord session runtime: " + str(timeDeltaSession) + "\ncinnamon runtime: " + str(timeDelta))


async def appendToLog(message: object, logFolderPath: str):
    # writes message to log file AND console
    global messageContent
    global attachments

    logPath = os.path.join(logFolderPath, str(message.channel) + '.html')
    file = open(logPath, 'a', encoding='utf-8')

    author_name = message.author.display_name
    attachments = [attachment.url for attachment in message.attachments]
    timestamp = message.created_at.strftime("%a, %d %b %Y %H:%M:%S +0000")
    color = hexToRGBA(str(message.author.color), 0.5)

    regularTextHTMLHeader = '<p class="text"'
    indentedLoggingCSSHeader = '<p class="indentedText"'

    if message.author.bot:
        print(f'    >>>CINNAMON: {messageContent}\n')
        try:
            file.write(f'{regularTextHTMLHeader} style="background-color: {color}">{timestamp}<br /><br />CINNAMON (bot): {messageContent}<br /></p>')
        except:
            file.write(f'{regularTextHTMLHeader}>{timestamp}<br /><br />CINNAMON (bot): FAILED TO LOG MESSAGE, MAY CONTAIN UNICODE CHARACTERS THAT I DON\'T WANT TO FIX AT THIS TIME<br /></p>')
    else:
        file.write(f'{regularTextHTMLHeader} style="background-color: {color}">{timestamp}<br /><br />{author_name}: {messageContent}<br /></p>')
        print(f'    {author_name}: {messageContent}\n')

    for attachment in message.attachments:
        if attachment.url not in messageContent and attachment.url not in attachments:
            attachments.append(attachment.url)

    # Get message.embeds, message.attachments, and urls in message.contents, and tape them together
    embeds = str(message.embeds)
    attachments = getURLs(str(message.attachments))

    for embed in embeds:
        attachments.append(embed)

    for url in getURLs(messageContent):
        attachments.append(url)

    # Loop through every attached file
    for i in range(len(attachments)):
        file_url = attachments[i][0:-3]
        print(file_url)

        # If the attached file is an image
        urlIsImage = ".jpg" in file_url or ".png" in file_url or ".webp" in file_url or ".gif" in file_url
        if urlIsImage:
            # write html for image to log
            file.write(f'\n{indentedLoggingCSSHeader} style="background-color: {color}"><img src="{file_url}" alt="{file_url}" class="embeddedImage" style="max-height: 50%; height: auto; loading="lazy""></p>')
        else:
            # add clickable link into log
            file.write(r'<a href="' + file_url + r'" style="background-color: rgba(150, 200, 255, 0.2);">' + file_url + '</a>')

    file.write("\n")
    file.close()


async def tryToLog(message: object):
    global messageContent
    global defaultLoggingHtml

    logFolderPath = os.path.join(os.path.dirname(__file__), str("logs\\" + str(message.guild)))
    logFilePath = str(logFolderPath + "\\" + str(message.channel) + '.html')

    # ensure file exists before trying
    if not os.path.exists(logFolderPath):
        # make folder
        os.makedirs(logFolderPath)

    if not os.path.isfile(logFilePath):
        # log doesn't exist yet, make it
        logFile = open(logFilePath, "w+")
        for i in range(len(defaultLoggingHtml)):
            print(defaultLoggingHtml[i])
            logFile.write(defaultLoggingHtml[i])

        logFile.close()

    print("  " + str(time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())))  # print current time
    await appendToLog(message, logFolderPath)


def getRollsAndDice(command):
    # extract rolls from command
    rolls = re.findall(r'\d+d', command)
    if len(rolls) == 0:
        rolls = "1"
    else:
        rolls = rolls[0]
        rolls = rolls[0:-1]

    #extract die from command
    die = re.findall(r'd\d+', command)
    if len(die) == 0:
        die = "20"
    else:
        die = die[0]
        die = die[1:]

    # rolled 0D20 or 1D0 or something like that
    if int(rolls) < 1: rolls = "1"
    if int(die) < 1: die = "1"

    # return [rolls, die] as int[]
    return [int(rolls), int(die)]


async def roll(command: str, message):
    advantage = 0
    results = []

    rollsAndDice = getRollsAndDice(command)
    rolls = rollsAndDice[0]
    die = rollsAndDice[1]

    response = "Rolling "+str(rolls)+" D"+str(die)+"(s)...\n"

    if "adv" in command:
        response = response + "rolling with adv: \n"
        advantage = 1
    elif "dis" in command:
        advantage = -1
        response = response + "rolling with disadv: \n"

    # for each die,
    for i in range(rolls):
        # if there are multiple dice, add roll number to response
        if rolls > 1:
            response = response + "roll " + str(i+1) + ": "

        # generate 2 random rolls,
        rng = [math.floor(random.random()*die), math.floor(random.random()*die)]
        if die != 10:
            # add 1 to non-d10 rolls,
            rng = [rng[0]+1, rng[1]+1]

        # then, if in adv or disadv state, add both rolls to response if in an adv/disadv state, and choose higher or lower rng value,
        if advantage != 0:
            response = response + str(rng) + " - "
            if advantage == 1:
                rng = [max(rng)]
            elif advantage == -1:
                rng = [min(rng)]

        # then, add chosen die to results & response
        results.append(rng[0])
        response = response + str(rng[0]) + "\n"

    # after rolling, if multiple dice were rolled, add some math to response, with results
    if rolls > 1:
        response = response + "average: " + str(sum(results) / len(results))
        response = response + "\nmin: " + str(min(results))
        response = response + "\nmax: " + str(max(results))

    await message.channel.send(response)


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
    await message.channel.send("""We're no strangers to love \nYou know the rules and so do I \nA full commitment's what I'm thinking of \nYou wouldn't get this from any other guy\nI just want to tell you how I'm feeling \nGotta make you understand""")
    await message.channel.send("""Never gonna give you up, never gonna let you down \nNever gonna run around and desert you \nNever gonna make you cry, never gonna say goodbye \nNever gonna tell a lie and hurt you""")
    await message.channel.send("""We've known each other for so long \nYour heart's been aching but you're too shy to say it \nInside we both know what's been going on \nWe know the game and we're gonna play it\nAnd if you ask me how I'm feeling \nDon't tell me you're too blind to see""")
    await message.channel.send("""Never gonna give you up, never gonna let you down \nNever gonna run around and desert you \nNever gonna make you cry, never gonna say goodbye \nNever gonna tell a lie and hurt you\n\nNever gonna give you up, never gonna let you down \nNever gonna run around and desert you \nNever gonna make you cry, never gonna say goodbye \nNever gonna tell a lie and hurt you""")
    await message.channel.send("""We've known each other for so long \nYour heart's been aching but you're too shy to say it \nInside we both know what's been going on \nWe know the game and we're gonna play it""")
    await message.channel.send("""I just want to tell you how I'm feeling \nGotta make you understand\nNever gonna give you up, never gonna let you down \nNever gonna run around and desert you \nNever gonna make you cry, never gonna say goodbye \nNever gonna tell a lie and hurt you""")


async def handlePrompts(message: object):
    global Nope
    global messageContent

    await handleSimpleResponses(message)

    if containsAny(messageContent, ["cinnamon, be silenced", "good night", "kys"]):
        # prompts that make cinnamon go away
        if "cinnamon, be silenced" in messageContent.lower():
            await message.channel.send("Hai!")
            Nope = 5
        if containsAny(messageContent, ["good night, cinnamon", "good night cinnamon"]):
            await message.channel.send("Jyaa ne!! ***bows***")
            Nope = 50
        if containsAny(messageContent, ["cinnamon, kys", "cinnamon kys", "kys cinnamon", "kys, cinnamon"]):
            await message.channel.send("a'k!")  # Sequential art, scarlet
            Nope = 1000

    if containsAny(messageContent, ["cinnamon, say", "cinnamon, say"]):
        startChar = containsAny(messageContent, ["cinnamon, say", "cinnamon, say"]) + 1
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

    if "cinnamon, rick roll" in messageContent.lower():  # Never gonna give you up!
        await rickRoll(message)

    if "cinnamon, lovecalc" in messageContent.lower():
        embed = discord.Embed(title="**:heart: Love calculation for " + messageContent.split(" ")[2] + " and " + messageContent.split(" ")[3] + "**:", description="Percentage: {}%".format(((int((str(re.sub('[^0123456789abcdefghijklmnopqrstuvwxyz ]', '', messageContent, 36))).split(" ")[2], 36) + int((str(re.sub('[^0123456789abcdefghijklmnopqrstuvwxyz ]', '', messageContent, 36))).split(" ")[3], 36)) % 101)), color=0xff7979)
        embed.set_footer(text="(don't take this seriously, you can bang anyone (with consent))")
        await message.channel.send(embed=embed)

    if "cinnamon, ping" in messageContent.lower():
        t1 = time.perf_counter()
        await client.send_typing(message.channel)
        t2 = time.perf_counter()
        embed = discord.Embed(title=None, description='Ping: {}ms'.format(round((t2 - t1) * 1000)), color=0x2874A6)
        await message.channel.send(embed=embed)

    if "cinnamon, runtime" in messageContent.lower():
        await sendRuntime(message)

    if "cinnamon, eval(" in messageContent.lower() or "/solve " in messageContent.lower():
        myCharOffset = [15, 1]
        if "cinnamon, eval(" in messageContent.lower():
            myCharOffset = [15, 1]
        else:
            myCharOffset = [7, 0]

        if containsAny(messageContent, badEvalWords):
            await message.channel.send("fuck you.")
        else:
            try:
                await message.channel.send(eval(messageContent[myCharOffset[0]:len(messageContent) - myCharOffset[1]]))
            except:
                await message.channel.send("snake said no")
        messageContent = ""

    if "ytplaylist" in messageContent.lower():
        print(messageContent)
        try:
            await message.channel.send("idk why you would want this, it's kind of a debug function, but sure")
            await message.channel.send(ytCrawl("".join(getURLs(messageContent)[0])))
        except:
            await message.channel.send("failed to send URLs, were there too many URLs in the playlist to send? Char limit is 2000")

    if "roll " in messageContent.lower():
        await roll(messageContent.lower()[messageContent.lower().find("roll "):len(messageContent.lower())], message)

    if "for shame" in messageContent.lower():
        await message.channel.send(file=discord.File(str(os.path.join(os.path.dirname(__file__), str("assets\\misc\\flandersShame.png")))))
    if "lewdsign" in messageContent.lower() or "lewd sign" in messageContent.lower() or "lewd_sign" in messageContent.lower():
        await message.channel.send(file=discord.File(str(os.path.join(os.path.dirname(__file__), str("assets\\lewdSign\\") + str(random.randint(0, 13)) + ".png"))))
    if "put up" in messageContent.lower() and "wolfjob" in messageContent.lower():  #:)
        await message.channel.send(file=discord.File(str(os.path.join(os.path.dirname(__file__), str("assets\\misc\\wolfjob.jpg")))))


async def handleRegularMessage(message: object):
    global messageContent
    global Nope

    await tryToLog(message)
    ImAwakeAndNotTalkingToABot = Nope <= 0 and not message.author.bot

    if ImAwakeAndNotTalkingToABot:
        await handlePrompts(message)
    else:
        # tape to make lewdie not respond to dumb
        # todo: remove when gh fixes his own damn bot
        if len(messageContent) == 3:
            if containsAny(messageContent, ["..."]) or (bool(re.search(r"\d\.\d", messageContent)) and not containsAny(messageContent, ["0.0", "4.4", "7.7", "9.9"])):
                await message.delete()

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
    if messageContent.lower().startswith(bot_prefix+"superhelp"):
        await message.channel.send(file=discord.File(str(os.path.join(os.path.dirname(__file__), str("assets\\Cinnamon Bot Help.html")))))
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

        print("\n\n\n\n\nLogin Successful!\nName:", client.user.name, "\nID:", client.user.id)
        print("Discord.py version:", discord.__version__, "\nCinnamon version:", cinnamonVersion)
        print("\n\n\n\n\n")
        initTimeSession = datetime.now().replace(microsecond=0)
        await client.change_presence(activity=discord.Game('Call me cinnamon'))

    @client.event
    async def on_server_join(guild):
        await client.send_message(guild, "Hiya! you seem to have added me to your guild! Thanks for that! ~<3")
        await client.send_message(guild, "try typing !>superhelp for an in depth list of all the things I can do!")

    @client.event
    async def on_error(self, event):
        print("I oopsie whoopsied! I fucko boingoed!")
        logging.warning(traceback.format_exc())
        print(event)
        try:
            message = event[0]
            await message.channel.send("I messed up. I'll won't better next time, and I'm not sorry. Also u r suck. You like that, don't you?")
        except:
            print("I.. I messed up telling discord people I messed up....")

    @client.event
    async def on_message(message):
        global messageContent
        global prevMessage  # previous message get!
        messageContent = message.content  # I don't want to type message.content 5000 times

        if messageContent.startswith(bot_prefix):  # If command (still within on_message)
            await handleCommand(message)
        else: # If not command (commands aren't really used anymore, but they are still supported)
            await handleRegularMessage(message)

        prevMessage = message  # store this message if I ever have any function that requires the use of 2 messages back


loop = asyncio.get_event_loop()

client.run(token)