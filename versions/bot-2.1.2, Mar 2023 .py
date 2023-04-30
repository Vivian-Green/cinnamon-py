#    Cinnamon bot v2.1.2 for discord, written by go fuck yourself, last update Feb 20, 2023 (almost complete re-write to actually function with new discord.py, also goddamn this was awful, and still is)
cinnamonVersion = "2.1.2"
description = "Multi-purpose bot that does basically anything I could think of"

# changelog in README.txt

# todo: move simpleResponses to json, and document over there somehow
# todo: add "run time" prompt
# todo: fix logging

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

def loadConfig(name: str):
    return json.load(open(os.path.join(os.path.dirname(__file__), str("configs\\" + name))))

client = discord.Client(intents=discord.Intents.all())

playlistURLs = []
attachments = ""
prevMessage = ""
messageContent = ""
Nope = 0

simpleResponses = loadConfig("simpleResponses.json")

config = loadConfig("config.json")
token, badEvalWords, bot_prefix= config["token"], config["badEvalWords"], config["prefix"]

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


async def appendToLog(message: object):#todo: make more readable, and make... functional
    global messageContent
    global attachments
    with open(str(os.path.join(os.path.dirname(__file__), str("logs\\" + str(message.guild) + "\\")) + str(message.channel) + '.html'), 'a') as file:  # open correct log file
        if message.author.bot:  # If cinnamon (or another bot))
            print("    >>>CINNAMON" + ": " + messageContent + "\n")  # custom display type for cinnamon
            try:  # attempt to log raw message
                file.write('<p style="padding-left: 20px; margin-left: 5px; padding-top: 8px; padding-bottom: 8px; background-color: ' + hexToRGBA(str(message.author.color), 0.5) + '">' + " \n\n    " + str(time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())) + "<br /><br /> CINNAMON (bot): " + str(messageContent) + "\n" + r"</p>")  # Log time, username, and reply to the open file, and format with css3, but that's unimportant
            except:  # If there is any unicode
                file.write('<p style="padding-left: 20px; margin-left: 5px; padding-top: 8px; padding-bottom: 8px; background-color: #d9b6d9;">' + " \n\n    " + str(time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())) + "<br /><br /> CINNAMON (bot): " + "MESSAGE CONTAINS UNICODE CHARACTERS THAT I DON'T WANT TO FIX AT THIS TIME")  # Display error in log if there are any unicode characters
        else:  # If human
            try:  # attempt to log raw message
                file.write('<p style="padding-left: 20px; margin-left: 20px; padding-top: 8px; padding-bottom: 8px; background-color: ' + hexToRGBA(str(message.author.color), 0.5) + '">' + " \n\n    " + str(time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())) + "<br /><br />" + message.author.display_name + ": " + str(messageContent) + "\n" + r"</p>")  # Log time, username, and reply to the open file, and format with css3, but that's unimportant
            except:  # If there is any unicode
                file.write('<p style="padding-left: 20px; margin-left: 20px; padding-top: 8px; padding-bottom: 8px; background-color: rgba(200, 200, 200, 0.5);">' + " \n\n    " + str(time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())) + "<br /><br />" + message.author.display_name + ": " + "MESSAGE CONTAINS UNICODE CHARACTERS THAT I DON'T WANT TO FIX AT THIS TIME")  # Display error in log if there are any unicode characters
            print("    " + message.author.display_name + ": " + messageContent + "\n")  # Log message to SHELL
        for i in range(len(getURLs(messageContent))):  # For every URL in raw text
            file.write(r'<a href="' + (getURLs(messageContent)[i]) + r'" style="background-color: rgba(150, 200, 255, 0.2);">' + getURLs(messageContent)[i] + '</a>')  # log clickable URL to file
        embeds = str(message.embeds)  # get message.embeds, as it's finnickey for some reason
        attachments = str(message.attachments)  # see above comment, but for message.attatchments
        for i in range(len(getURLs(attachments))):  # for every attatched file
            print(getURLs(attachments)[i][0:-2])  # print file URL to shell
            if ".jpg" in getURLs(attachments)[i][0:-2] or ".png" in getURLs(attachments)[i][0:-2] or ".gif" in getURLs(attachments)[i][0:-2]:  # if attatched file is an image
                if "media.discordapp" in getURLs(attachments)[i][0:-2]:  # If the image is from the discord media guild
                    file.write('<p>Attatchment:: <p><img src="' + getURLs(attachments)[i][0:-2] + '" alr="' + getURLs(attachments)[i][0:-2] + '">')  # embed image into log
            else:  # if not an image
                file.write(r'<a href="' + (getURLs(attachments)[i]) + r'" style="background-color: rgba(150, 200, 255, 0.2);">' + getURLs(attachments)[i] + '</a>')  # embed clickable link into log
        for i in range(len(getURLs(embeds))):  # for every embedded file
            print(getURLs(embeds)[i][0:-2])  # print file URL to shell
            if ".jpg" in getURLs(embeds)[i][0:-2] or ".png" in getURLs(embeds)[i][0:-2] or ".gif" in getURLs(embeds)[i][0:-2]:  # if embedded file is an image
                if "discordapp" in getURLs(embeds)[i][0:-2]:  # if file is from a discord guild
                    file.write('<p>Discord embed: <p><img src="' + getURLs(embeds)[i][0:-2] + '" alr="' + getURLs(embeds)[i][0:-2] + '">')  # embed image into log
            else:  # if embedded file is not an image
                file.write(r'<a href="' + (getURLs(embeds)[i]) + r'" style="background-color: rgba(150, 200, 255, 0.2);">' + getURLs(embeds)[i] + '</a>')  # log raw link to file
        file.close()  # close the file


async def tryToLog(message: object):
    global messageContent
    print("  " + str(time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())))  # print current time
    try:
        await appendToLog(message)
    except:
        if not os.path.exists(os.path.join(os.path.dirname(__file__), str("logs\\" + str(message.guild)))):
            os.makedirs(os.path.join(os.path.dirname(__file__), str("logs\\" + str(message.guild))))
        open(str(os.path.join(os.path.dirname(__file__), str("logs\\" + str(message.guild) + "\\")) + str(message.channel) + '.html'), "w+").close()
        await appendToLog(message)


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

    # fucko rolled 0D20 or 1D0 or something like that
    if int(rolls) < 1: rolls = "1"
    if int(die) < 1: die = "1"

    #return [rolls, die] as int[]
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
        # prompts that make cinnamon stfu
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

    if "cinnamon, eval(" in messageContent.lower():
        if containsAny(messageContent, badEvalWords):
            await message.channel.send("fuck you.")
        else:
            try:
                await message.channel.send(eval(messageContent[15:len(messageContent) - 1]))
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
        #todo: remove when gh fixes his own damn bot
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

    # commands that can't be processed by discord's command api, because it is crap. Oh, wait, it's all the commands. huh.
    if messageContent.lower().startswith(bot_prefix+"superhelp"):
        await message.channel.send(file=discord.File(str(os.path.join(os.path.dirname(__file__), str("assets\\Cinnamon Bot Help.html")))))
    if messageContent.lower().startswith(bot_prefix+"getlog"):
        await message.author.send(file=discord.File(str(os.path.join(os.path.dirname(__file__), str("logs\\" + str(message.guild) + "\\")) + str(message.channel) + '.html')))
        await message.channel.send("Check your DM's!")
    if messageContent.lower().startswith(bot_prefix+"test"):
        await message.channel.send("Hey, you're not a doofus! Good job, you!")
    if messageContent.lower().startswith(bot_prefix+"goodbot"):
        await message.channel.send(("Arigatogozaimasu, " + message.author.display_name + "-sama! >.<"))


class Main:
    @client.event
    async def on_ready():
        print("\n\n\n\n\nLogin Successful!\nName:", client.user.name, "\nID:", client.user.id)
        print("Discord.py version:", discord.__version__, "\nCinnamon version:", cinnamonVersion)
        print("\n\n\n\n\n")
        await client.change_presence(activity=discord.Game('Call me cinnamon'))

    @client.event
    async def on_server_join(guild):
        await client.send_message(guild, "Hiya! you seem to have added me to your guild! Thanks for that! ~<3")
        await client.send_message(guild, "try typing !>superhelp for an in depth list of all the things I can do!")

    @client.event
    async def on_error(self, event):
        print("fuck! I oopsie whoopsied! I fucko boingoed!")
        logging.warning(traceback.format_exc())
        print(event)
        try:
            message = event[0]
            await message.channel.send("I fucked up. I'll won't better next time, and I'm not sorry. Also ur a bitch. You like that, don't you?")
        except:
            print("I.. I fucked up telling discord people I fucked up....")

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