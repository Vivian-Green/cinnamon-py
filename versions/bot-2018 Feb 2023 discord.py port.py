# Cinnamon bot v2.0.0 for discord, written by go fuck yourself, last update Feb 20, 2023 (almost complete re-write to actually function with new discord.py, also goddamn this was awful, and still is)
cinnamonVersion = "2.0.0"

# old text:
# Cinnamon bot v1.0.0 for discord, written by go fuck yourself, last update March 2, 2018 (almost complete re-write to force sfw defaults, and a simplified way to modify a channel's config)

# a fair amount of code is heavily based on sources other than my own brain, also I have no idea what code came from what source at this point
# most of it's mine, and some of it isn't. some of it is also based on someone else's code, and modified a lot
# also, I don't think I credited any images, so, yeah, none of those are mine unless otherwise noted

# and I'm self-taught... don't kill me

# default command prefix: !>
# get image: [image]

import time
from random import randint
#import random
#import sys
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
#from discord.voice_client import VoiceClient
from discord.ext import commands

token = "MTA3NzQwNDE3Njg3NjgzODkyMg.GokyHp.jhXJX6fEpisLr4PUTM1f3TpA9tntlrbZDiSCyw"

description = "Multi-purpose bot that does basically anything I could think of"
bot_prefix = "!>"
# commands.when_mentioned_or('!>')
inDev = 0  # don't set this to 1 unless you are a dev, aka me.
# client = commands.Bot(description=description, command_prefix=bot_prefix, intents=discord.Intents.all())

client = discord.Client(intents=discord.Intents.all())

tempVar = 0
tempVar2 = 0
Nope = 0
annoy = ""
annoyTime = time.strftime("%H:%M:%S", time.gmtime())
attachments = ""
chatMod = 1  # don't change it here, it will do literally nothing, the value just needs to be defined here. Go to your channel's config file
queue = []
songLength = 0
playing = 0
CTX = 0
all_url = []
playlistURLs = []
fileBackup = []
muted = []
nsfw = 0
nsfwCheck = 0
reconnectTime = 5

prevMessage = ""

def ytCrawl(url):  # http://pantuts.com/2013/02/16/youparse-extract-urls-from-youtube/
    global playlistURLs
    global all_url
    sTUBE = ''
    final_url = []

    if 'list=' in url:
        eq = url.rfind('=') + 1
        cPL = url[eq:]

    else:
        print('Incorrect Playlist.')
        exit(1)

    try:
        yTUBE = urllib.request.urlopen(url).read()
        sTUBE = str(yTUBE)
    except urllib.error.URLError as e:
        print(e.reason)

    tmp_mat = re.compile(r'watch\?v=\S+?list=' + cPL)
    mat = re.findall(tmp_mat, sTUBE)

    if mat:
        playlistURLs = []
        for PL in mat:
            yPL = str(PL)
            if '&' in yPL:
                yPL_amp = yPL.index('&')
                final_url.append('https://www.youtube.com/' + yPL[:yPL_amp])
                if not str('https://www.youtube.com/' + yPL[:yPL_amp]) in playlistURLs:
                    playlistURLs.append(str('https://www.youtube.com/' + yPL[:yPL_amp]))

        all_url = list(set(final_url))

    ##        i = 0
    ##        while i < len(all_url):
    ##            sys.stdout.write(all_url[i] + '\n')
    ##            time.sleep(0.04)
    ##            i = i + 1

    else:
        print('No videos found.')
        exit(1)
    return all_url


def getURLs(string):
    return re.findall('(http)s?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|%[0-9a-fA-F][0-9a-fA-F])+', string)

def hexToRGBA(hexValue, alpha):
    h = tuple(int(hexValue.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))
    return "rgba(" + str(h[0]) + ", " + str(h[1]) + ", " + str(h[2]) + ", " + str(alpha) + ")"

async def createConfig(message: object):
    global chatMod
    global nsfw

    if not message.author.display_name.lower() == "cinnamon":
        try:
            os.makedirs(os.path.join(os.path.dirname(__file__), str("configs\\" + str(message.guild))))
            with open(str(os.path.join(os.path.dirname(__file__), str("configs\\" + str(message.guild) + "\\")) + str(message.channel) + '.config'), 'a') as file:
                file.write("chatMod = 1")
                file.write("nsfw = 0")
            await message.channel.send("Config file created for this channel! type !>settings (if you are a chatmod/admin/owner) to edit, or !>superhelp for detailed info!")

        except:
            with open(str(os.path.join(os.path.dirname(__file__), str("configs\\" + str(message.guild) + "\\")) + str(message.channel) + '.config'), 'w') as file:
                file.write("")

            with open(str(os.path.join(os.path.dirname(__file__), str("configs\\" + str(message.guild) + "\\")) + str(message.channel) + '.config'), 'a') as file:
                if chatMod == 1:
                    file.write("chatMod = 1\n")
                else:
                    file.write("chatMod = 0\n")
                if nsfw == 1:
                    file.write("nsfw = 1")
                else:
                    file.write("nsfw = 0")
            await message.channel.send("Config file created for this channel! type !>settings (if you are a chatmod/admin/owner) to edit, or !>superhelp for detailed info!\n\n(and if this is the discord bot list guild, hi! I attempted to make this bot fit the rules, but I may have messed up a bit because this is my first discord bot (that I've been writing for months...), please inform me if this is the case, as it's certainly not intentional behavior)")


async def appendToLog(message: object, messageContent: str):
    global attachments
    with open(str(os.path.join(os.path.dirname(__file__), str("logs\\" + str(message.guild) + "\\")) + str(message.channel) + '.html'), 'a') as file:  # open correct log file
        if message.author.bot:  # If cinnamon (or another bot))
            print(">>>CINNAMON" + ": " + messageContent + "\n" + r"\n")  # custom display type for cinnamon
            try:  # attempt to log raw message
                file.write('<p style="padding-left: 20px; margin-left: 5px; padding-top: 8px; padding-bottom: 8px; background-color: ' + hexToRGBA(str(message.author.color), 0.5) + '">' + " \n\n    " + str(time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())) + "<br /><br /> CINNAMON (bot): " + str(messageContent) + "\n" + r"</p>")  # Log time, username, and reply to the open file, and format with css3, but that's unimportant
            except:  # If there is any unicode
                file.write('<p style="padding-left: 20px; margin-left: 5px; padding-top: 8px; padding-bottom: 8px; background-color: #d9b6d9;">' + " \n\n    " + str(time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())) + "<br /><br /> CINNAMON (bot): " + "MESSAGE CONTAINS UNICODE CHARACTERS THAT I DON'T WANT TO FIX AT THIS TIME")  # Display error in log if there are any unicode characters
        else:  # If human
            try:  # attempt to log raw message
                file.write('<p style="padding-left: 20px; margin-left: 20px; padding-top: 8px; padding-bottom: 8px; background-color: ' + hexToRGBA(str(message.author.color), 0.5) + '">' + " \n\n    " + str(time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())) + "<br /><br />" + message.author.display_name + ": " + str(messageContent) + "\n" + r"</p>")  # Log time, username, and reply to the open file, and format with css3, but that's unimportant
            except:  # If there is any unicode
                file.write('<p style="padding-left: 20px; margin-left: 20px; padding-top: 8px; padding-bottom: 8px; background-color: rgba(200, 200, 200, 0.5);">' + " \n\n    " + str(time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())) + "<br /><br />" + message.author.display_name + ": " + "MESSAGE CONTAINS UNICODE CHARACTERS THAT I DON'T WANT TO FIX AT THIS TIME")  # Display error in log if there are any unicode characters
            print("  " + message.author.display_name + ": " + messageContent + "\n")  # Log message to SHELL
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


async def roll(num, messageContent, message):  # You want comments on this thing? DO IT YOURSELF!  (rolls D&D die based on input, "num" being the die (4, 6, 8, 10, 12, 20, 100), messageContent being the string (when it gets to this function, "<adv/dis> <+/- modifier>"), and message is the original, inputted message
    global tempVar2
    messageContent = messageContent[len(str(num)) + 1:len(messageContent)]

    if num == 10:
        startnum = 0
    else:
        startnum = 1

    if len(messageContent) > 1:
        tempVar2 = 0

        if messageContent.lower()[tempVar2] == "-":
            for i in range(len(messageContent) - 1):
                if messageContent.lower()[tempVar2 + 1] != " ":
                    tempVar2 += 1
                    print(messageContent[1:tempVar2])
            await message.channel.send("D" + str(num) + ": " + str(randint(startnum, startnum + num - 1) - int(messageContent[1:tempVar2 + 1])))
            messageContent = messageContent[tempVar2:len(messageContent)]
            print(messageContent)


        elif messageContent.lower()[tempVar2] == "+":
            for i in range(len(messageContent) - 1):
                if messageContent.lower()[tempVar2 + 1] != " ":
                    tempVar2 += 1
                    print(messageContent[1:tempVar2])
            await message.channel.send("D" + str(num) + ": " + str(randint(startnum, startnum + num - 1) + int(messageContent[1:tempVar2 + 1])))
            messageContent = messageContent[tempVar2:len(messageContent)]
            print(messageContent)


        elif messageContent.lower().startswith("dis"):
            messageContent = messageContent[4:len(messageContent)]

            if len(messageContent) < 1:
                tempVar2 = randint(startnum, startnum + num - 1)
                tempVar3 = randint(startnum, startnum + num - 1)
                await message.channel.send("D" + str(num) + ": " + str(tempVar2))
                await message.channel.send("D" + str(num) + ": " + str(tempVar3) + "\n")
                if tempVar2 > tempVar3:
                    await message.channel.send("Result: " + str(tempVar3))
                else:
                    await message.channel.send("Result: " + str(tempVar2))

            else:
                tempVar2 = 1
                if messageContent.lower()[0] == "-":
                    for i in range(len(messageContent) - 1):
                        if messageContent.lower()[tempVar2] != " ":
                            tempVar2 += 1
                    tempVar4 = randint(int(messageContent[1:tempVar2]) + startnum, num + int(messageContent[1:len(messageContent)]) + startnum - 1)
                    tempVar3 = randint(int(messageContent[1:tempVar2]) + startnum, num + int(messageContent[1:len(messageContent)]) + startnum - 1)
                    await message.channel.send("D" + str(num) + ": " + str(tempVar4))
                    await message.channel.send("D" + str(num) + ": " + str(tempVar3) + "\n")
                    if tempVar4 > tempVar3:
                        await message.channel.send("Result: " + str(tempVar3))
                    else:
                        await message.channel.send("Result: " + str(tempVar4))
                elif messageContent.lower()[0] == "+":
                    for i in range(len(messageContent) - 1):
                        if messageContent.lower()[tempVar2] != " ":
                            tempVar2 += 1
                    tempVar4 = randint(int(messageContent[1:tempVar2]) + startnum, num + int(messageContent[1:len(messageContent)]) + startnum - 1)
                    tempVar3 = randint(int(messageContent[1:tempVar2]) + startnum, num + int(messageContent[1:len(messageContent)]) + startnum - 1)
                    await message.channel.send("D" + str(num) + ": " + str(tempVar4))
                    await message.channel.send("D" + str(num) + ": " + str(tempVar3) + "\n")
                    if tempVar4 > tempVar3:
                        await message.channel.send("Result: " + str(tempVar3))
                    else:
                        await message.channel.send("Result: " + str(tempVar4))


        elif messageContent.lower().startswith("adv"):
            messageContent = messageContent[4:len(messageContent)]

            if len(messageContent) < 1:
                tempVar2 = randint(startnum, startnum + num - 1)
                tempVar3 = randint(startnum, startnum + num - 1)
                await message.channel.send("D" + str(num) + ": " + str(tempVar2))
                await message.channel.send("D" + str(num) + ": " + str(tempVar3) + "\n")
                if tempVar2 > tempVar3:
                    await message.channel.send("Result: " + str(tempVar2))
                else:
                    await message.channel.send("Result: " + str(tempVar3))

            else:
                tempVar2 = 1
                if messageContent.lower()[0] == "-":
                    for i in range(len(messageContent) - 1):
                        if messageContent.lower()[tempVar2] != " ":
                            tempVar2 += 1
                    tempVar4 = randint(int(messageContent[1:tempVar2]) + startnum, num + int(messageContent[1:len(messageContent)]) + startnum - 1)
                    tempVar3 = randint(int(messageContent[1:tempVar2]) + startnum, num + int(messageContent[1:len(messageContent)]) + startnum - 1)
                    await message.channel.send("D" + str(num) + ": " + str(tempVar4))
                    await message.channel.send("D" + str(num) + ": " + str(tempVar3) + "\n")
                    if tempVar4 < tempVar3:
                        await message.channel.send("Result: " + str(tempVar3))
                    else:
                        await message.channel.send("Result: " + str(tempVar4))
                elif messageContent.lower()[0] == "+":
                    for i in range(len(messageContent) - 1):
                        if messageContent.lower()[tempVar2] != " ":
                            tempVar2 += 1
                    tempVar4 = randint(int(messageContent[startnum:tempVar2]) + startnum, num + int(messageContent[1:len(messageContent)]) + startnum - 1)
                    tempVar3 = randint(int(messageContent[startnum:tempVar2]) + startnum, num + int(messageContent[1:len(messageContent)]) + startnum - 1)
                    await message.channel.send("D" + str(num) + ": " + str(tempVar4))
                    await message.channel.send("D" + str(num) + ": " + str(tempVar3) + "\n")
                    if tempVar4 < tempVar3:
                        await message.channel.send("Result: " + str(tempVar3))
                    else:
                        await message.channel.send("Result: " + str(tempVar4))


    else:
        await message.channel.send("D" + str(num) + ": " + str(randint(startnum, num + startnum - 1)))


class Main:

    @client.event
    async def on_ready():
        global annoy
        global annoyTime
        global reconnectTime
        print("\n\n\n\n\n")
        print("Login Successful!")
        print("Name:", client.user.name)
        print("ID:", client.user.id)
        print("Version:", discord.__version__)
        print("Cinnamon version:", cinnamonVersion)
        discord.Activity(name="Call me Cinnamon!", type=5)
        print("\n\n\n\n\n")
        reconnectTime = 5

        # await client.add_cog(Commands(client))
        # await client.add_cog(Polling(client))
        # await client.add_cog(Main())

    @client.event
    async def on_server_join(guild):
        await client.send_message(guild, "Hiya! you seem to have added me to your guild! Thanks for that! ~<3")
        await client.send_message(guild, "try typing !>superhelp for an in depth list of all the things I can do!")

    @client.event
    async def on_error(self, event):
        print("fuck! I oopsie whoopsied! I fucko boingoed!")
        #message = event[0]

        logging.warning(traceback.format_exc())

        print(event)
        #await message.channel.send("I fucked up. I'll won't better next time, and I'm not sorry. Also ur a bitch")

    @client.event
    async def on_message(message):
        # ~~~~~~~~ define some global stuffs
        global tempVar2
        global fileBackup

        global prevMessage  # previous message get!
        global Nope  # "Sleep" bool get!
        global annoy  # This is dated, but breaks the program if deleted, so, "annoy" get!
        global annoyTime  # see above!
        global attachments  # I don't know why I made this global, but it doesn't really matter because this is the only function that uses it! ("attatchments" get!)
        global chatMod
        global inDev
        global muted
        global nsfwCheck
        global nsfw
        prevMessage = message  # archive this message if I ever have any function that requires the use of 2 messages back
        messageContent = message.content  # I don't want to type message.content 5000 times

        print(messageContent)
        # TEMPORARY! VERY TEMPORARY!
        if messageContent.lower() == "cinnamon, drop the nuke":
            await message.channel.send("LAUNCHING...")
            time.sleep(10)
            await message.channel.send("5 SECONDS TO IMPACT")
            time.sleep(1)
            await message.channel.send("4 SECONDS TO IMPACT")
            time.sleep(1)
            await message.channel.send("3 SECONDS TO IMPACT")
            time.sleep(1)
            await message.channel.send("2 SECONDS TO IMPACT")
            time.sleep(1)
            await message.channel.send("1 SECONDS TO IMPACT")
            time.sleep(1)
            await message.channel.send("NUKE DROPPED")
            time.sleep(2)
            with open(str(os.path.join(os.path.dirname(__file__), str("logs\\" + "killerPenguino0" + "\\")) + "main" + '.html'), "r") as file:
                tempVar2 = file.readlines()
                tempVar3 = 0
                for i in range(len(tempVar2)):
                    if tempVar2[tempVar3].startswith("</p><p style=") or len(tempVar2[tempVar3]) < 5:
                        del tempVar2[tempVar3]
                    else:
                        if tempVar2[tempVar3].startswith("</p>"):
                            tempVar2[tempVar3] = (tempVar2[tempVar3][4: len(tempVar2[tempVar3]) - 4])
                            if tempVar2[tempVar3].startswith("<a href"):
                                while not tempVar2[tempVar3].startswith(">"):
                                    tempVar2[tempVar3] = tempVar2[tempVar3][1: len(tempVar2[tempVar3])]
                                tempVar2[tempVar3] = tempVar2[tempVar3][1: len(tempVar2[tempVar3])]
                                tempVar4 = 0
                                while not tempVar2[tempVar3][tempVar4] == "<":
                                    tempVar4 += 1
                                await message.channel.send("OLD LOG: " + tempVar2[tempVar3][0:tempVar4])
                        else:
                            await message.channel.send("OLD LOG: " + tempVar2[tempVar3][47: len(tempVar2[tempVar3])])
                        tempVar3 += 1

        # ~~~~~~~ get config file

        try:
            with open(str(os.path.join(os.path.dirname(__file__), str("configs\\" + str(message.guild) + "\\")) + str(message.channel) + '.config'), 'r') as file:
                tempVar2 = (file.readlines())
                if len(tempVar2) > 0:
                    print(tempVar2)
                    for i in range(len(tempVar2)):
                        exec(tempVar2[i], globals())
                        print(chatMod)
                else:
                    await createConfig(message)
        except:
            await createConfig(message)

        # ~~~~~~~~ check if the user is muted, if do, delete the message immediately

        if message.author.display_name.lower() in muted:
            await message.delete()

        # ~~~~~~~~ if not command (commands aren't really used anymore, but they are still supported)

        if not messageContent.startswith("!>"):
            print("    " + str(time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())))  # print current time
            # os.path.join(os.path.dirname(__file__), str("logs\\"+str(message.guild)+"\\"))#testing path
            try:
                await appendToLog(message, messageContent)
            except:
                if not os.path.exists(os.path.join(os.path.dirname(__file__), str("logs\\" + str(message.guild)))):
                    os.makedirs(os.path.join(os.path.dirname(__file__), str("logs\\" + str(message.guild))))
                open(str(os.path.join(os.path.dirname(__file__), str("logs\\" + str(message.guild) + "\\")) + str(message.channel) + '.html'), "w+").close()
                # with open(str(os.path.join(os.path.dirname(__file__), str("logs\\"+str(message.guild)+"\\"))+str(message.channel)+'.html'), 'w+') as file:
                # file.close()
                await appendToLog(message, messageContent)
            if chatMod == 1:  # If the moderator function is active
                if messageContent.lower().startswith("ass"):  # also, I know I could have done this way easier, and able to be changed per-guild by checking within a list, but...
                    await message.delete()  # Delete the offensive message
                    await message.channel.send("Lol butts")  # Explain why the message was deleted, in global
                    return
                if messageContent.lower().startswith("arse"):
                    await message.delete()  # See 2 up
                    await message.channel.send("Lol butts")  # See 2 up
                    return
                if messageContent.lower().startswith("bitch"):
                    await message.delete()  # See 2 up
                    await message.channel.send("Hehe... dogs are so adorable <3")  # See 2 up
                    return
                if messageContent.lower().startswith("cunt"):
                    await message.delete()  # See 2 up
                    await message.channel.send("I have one of those!")  # See 2 up
                    return
                if messageContent.lower().startswith("cock"):
                    await message.delete()
                    await message.channel.send("*Cuckoo")
                    return
                if messageContent.lower().startswith("dick"):
                    await message.delete()
                    await message.channel.send("Bad word!")
                    return
                if messageContent.lower().startswith("fuck you"):
                    await message.delete()
                    await message.channel.send("Please do")
                    return
                elif messageContent.lower().startswith("fuck me"):
                    await message.delete()
                    await message.channel.send("ok")
                    return
                elif messageContent.lower().startswith("fuck"):
                    await message.delete()
                    await message.channel.send("Bad!")
                elif messageContent.lower().startswith("fuk"):
                    await message.delete()
                    await message.channel.send("Bad!")
                    return
                if messageContent.lower().startswith("nigger"):
                    await message.delete()
                    await message.channel.send("I know you are, but what am I?")
                    return
                if messageContent.lower().startswith("pussy"):
                    await message.delete()
                    await message.channel.send("I have one of those!")
                    return
                if messageContent.lower().startswith("piss"):
                    await message.delete()
                    await message.channel.send("No! Bad person!")
                    return
                if messageContent.lower().startswith("whore"):
                    await message.delete()
                    await message.channel.send("*respectable woman")
                    return
                if messageContent.lower().startswith("slut"):
                    await message.delete()
                    await message.channel.send("*respectable woman")
                    return
                if messageContent.lower().startswith("bastard"):
                    await message.delete()
                    await message.channel.send("Hahaha you said the bad language word")
                    return
            if not (Nope > 0 or message.author.bot):  # if cinnamon is in "awake" mode
                for i in range(len(messageContent)):  # for every characyer in the message

                    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~muting

                    if messageContent.lower().startswith("cinnamon mute "):
                        if message.author.permissions_in(message.channel).manage_messages:
                            muted.append(messageContent[14:len(messageContent)])
                            await message.channel.send(messageContent[14:len(messageContent)] + " muted! The mute will last until you unmute them, or I am disabled. You will have to manually reinstate the mute if I am restarted")
                        else:
                            await message.channel.send("You must be of chatmod rank (able to delete messages) to toggle a mute! Don't worry, they're temporary")
                        break
                    if messageContent.lower().startswith("cinnamon, mute "):
                        if message.author.permissions_in(message.channel).manage_messages:
                            muted.append(messageContent[15:len(messageContent)])
                            await message.channel.send(messageContent[15:len(messageContent)] + " muted! The mute will last until you unmute them, or I am disabled. You will have to manually reinstate the mute if I am restarted")
                        else:
                            await message.channel.send("You must be of chatmod rank (able to delete messages) to toggle a mute! Don't worry, they're temporary")
                        break
                    if messageContent.lower().startswith("cinnamon unmute "):
                        if message.author.permissions_in(message.channel).manage_messages:
                            muted.remove(messageContent[16:len(messageContent)])
                            await message.channel.send("unmuted " + messageContent[16:len(messageContent)])
                        else:
                            await message.channel.send("You must be of chatmod rank (able to delete messages) to toggle a mute! Don't worry, they're temporary")
                        break
                    if messageContent.lower().startswith("cinnamon unmute "):
                        if message.author.permissions_in(message.channel).manage_messages:
                            muted.remove(messageContent[17:len(messageContent)])
                            await message.channel.send("unmuted " + messageContent[17:len(messageContent)])
                        else:
                            await message.channel.send("You must be of chatmod rank (able to delete messages) to toggle a mute! Don't worry, they're temporary")
                        break

                    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~back and fourth

                    if messageContent.lower() == "arise, cinnamon":  #
                        if nsfw == 1:
                            await message.channel.send("Ufufu... To be woken up by a guy after having no idea what happened before you fell asleep... how mysterious <3")
                        else:
                            await message.channel.send("Ohayogozaimasu!!!")
                    if messageContent.lower() == "cinnamon, you are dismissed":
                        await message.channel.send("***bows***")
                    if (messageContent.lower().startswith("hype")) and (message.author.display_name.lower() != "cinnamon"):
                        await message.channel.send("HYPE!!!!!!!!!")
                        break
                    if messageContent.lower().startswith("can't you, cinnamon"):
                        await message.channel.send("I can")
                    if messageContent.lower().startswith("hello, cinnamon"):
                        await message.channel.send("Ohayo, " + message.author.display_name + "! =D")
                    if messageContent.lower().startswith("right, cinnamon"):
                        await message.channel.send("Correct")
                    if messageContent.lower().startswith("slaps cinnamon "):
                        await message.channel.send(";-;")
                    if messageContent.lower().startswith("spanks cinnamon "):
                        if nsfw == 1:
                            await message.channel.send("Ufufu~ <3")
                    if messageContent.lower().startswith("slaps cinnamon*"):
                        await message.channel.send(";-;")
                    if messageContent.lower().startswith("spanks cinnamon*"):
                        if nsfw == 1:
                            await message.channel.send("Ufufu~ <3")
                    if messageContent.lower().startswith("cinnamon, summon"):
                        await message.channel.send("***summons***")
                    if messageContent.lower().startswith("*applauds*"):
                        await message.channel.send("***also applauds***")
                    if messageContent.lower().startswith("good cinnamon"):
                        await message.channel.send(("Arigatogozaimasu, " + message.author.display_name + "-sama! ***blushes***   >.<"))
                    if messageContent.lower().startswith("good job, cinnamon"):
                        await message.channel.send("Arigatogozaimasu!")
                    if messageContent.lower().startswith("good job cinnamon"):
                        await message.channel.send("Arigatogozaimasu!")
                    if messageContent.lower().startswith("cinnamon, be silenced"):
                        await message.channel.send("Hai!")
                        Nope = 5
                    if messageContent.lower() == "thank you, cinnamon":
                        await message.channel.send("***purrs***")
                    if messageContent.lower() == "thank you cinnamon":
                        await message.channel.send("***purrs***")
                    if messageContent.lower().startswith("cinnamon!"):
                        await message.channel.send("I heard my name, have I been called? ***Nya~***")
                    if messageContent.lower().startswith("shinnamon"):
                        await message.channel.send("Watashi wa kiku ashita no namae. Watashi wa yoba rete imasuka? ***Nya~***")
                    if messageContent.lower().startswith("*pets cinnamon*") or messageContent.lower().startswith("*pets cinnamon"):
                        await message.channel.send("***Nyaaaaa~***")
                    if messageContent.lower().startswith("*head pats cinnamon"):
                        await message.channel.send("***purr~***")
                    if messageContent.lower().startswith("*strokes*") or messageContent.lower().startswith("*strokes cinnamon*"):
                        if nsfw == 1:
                            await message.channel.send("*Ufufu* ***~<3***")
                        else:
                            await message.channel.send("nyaaa***~<3***")
                    if messageContent.lower().startswith("cinnamon, slap"):
                        await message.channel.send("***slaps***")
                    if messageContent.lower().startswith("cinnamon slap"):
                        await message.channel.send("***slaps***")
                    if messageContent.lower().startswith("good night, cinnamon"):
                        await message.channel.send("Jyaa ne!! ***bows***")
                        Nope = 50
                    if messageContent.lower().startswith("good night cinnamon"):
                        await message.channel.send("Jyaa ne!! ***bows***")
                        Nope = 50
                    if messageContent.lower() == "good morning, cinnamon":
                        await message.channel.send("***Cat yawn noise***")
                        await message.channel.send("Ohayo, " + message.author.display_name + "-san")
                    if messageContent.lower() == "good morning cinnamon":
                        await message.channel.send("***Cat yawn noise***")
                        await message.channel.send("Ohayo, " + message.author.display_name + "-san")
                    if (messageContent.lower().startswith("xd")) and (message.author.display_name.lower() != "cinnamon"):
                        await message.channel.send("xD")
                    if (messageContent.lower().startswith("nya")) and (message.author.display_name.lower() != "cinnamon"):  # Nyaa!
                        tempVar2 = randint(1, 10)
                        if tempVar2 == 1:
                            await message.channel.send("Nyaaa~")
                        elif tempVar2 == 2:
                            await message.channel.send("Nya")
                        elif tempVar2 == 3:
                            await message.channel.send("Nyan")
                        elif tempVar2 == 4:
                            await message.channel.send("Nya nyan?")
                        elif tempVar2 == 5:
                            await message.channel.send("Nyaaaan~")
                        elif tempVar2 == 6:
                            await message.channel.send("Nyan na")
                        elif tempVar2 == 7:
                            await message.channel.send("Nya?")
                        elif tempVar2 == 8:
                            await message.channel.send("Nyaaa?")
                        elif tempVar2 == 9:
                            await message.channel.send("Nyan nya")
                        elif tempVar2 == 10:
                            await message.channel.send("Nyan nyaaan?")
                    if messageContent.lower().startswith("sinnamon"):  # Bittersweer candy bowl
                        await message.channel.send("Paulo, ruler of all cat *playas* is not here")
                    if messageContent.lower().startswith("glomps cinnamon"):
                        if nsfw == 1:
                            await message.channel.send("***I fly back from the impact into the wall, my shocked face turning red as your-***")
                            await message.channel.send("Sorry, wrong chat! XD")
                        else:
                            await message.channel.send("***Gets glomped***")
                    if messageContent.lower().startswith("kawaii"):
                        await message.channel.send("***projectile vomits sparkles***")
                    if messageContent.lower().startswith("kemonomimi"):
                        if nsfw == 1:
                            await message.channel.send("Somebody talking about japanese not-quite-furry trash?")
                    if messageContent.lower().startswith("nekomimi"):
                        if nsfw == 1:
                            await message.channel.send("Somebody talking about me?")
                    if messageContent.lower().startswith("eroge") and message.author.display_name.lower() != "cinnamon":
                        if nsfw == 1:
                            await message.channel.send("I heard eroge; I'm all cat ears")  # see below red text
                    if messageContent.lower().startswith("hentei") or messageContent.lower().startswith("chinese cartoon") or messageContent.lower().startswith("futanari"):
                        if nsfw == 1:
                            await message.channel.send("it's called hentai, and it's art")  # haha funny joke
                    if messageContent.lower().startswith("cashew"):
                        await message.channel.send("*Kashou")
                        break
                    if nsfw == 1:
                        if messageContent.lower().startswith("fuck you, cinnamon"):
                            await message.channel.send(("Your wish is my command, " + message.author.display_name + "-sama"))
                        if messageContent.lower().startswith("fuck you cinnamon"):
                            await message.channel.send(("Your wish is my command, " + message.author.display_name + "-sama"))
                        if messageContent.lower().startswith("fuck me cinnamon"):
                            await message.channel.send("私は自分の猫を食べながら私のお尻で犯されている〜")  # I don't know much vulgar japanese; yes, I did use google translate for this, also, it's "I'm gettign fucked in the ass while eating my own pussy" as quoted by Daniel (the sexbang) (non-baby penis) (the sexbang) Avidan
                        if messageContent.lower().startswith("fuck me, cinnamon"):
                            await message.channel.send("私は自分の猫を食べながら私のお尻で犯されている〜")
                    if messageContent.lower().startswith("winks at cinnamon"):
                        await message.channel.send(";)")

                    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~semi-complex

                    if messageContent.lower().startswith("cinnamon, become the "):  # Homestuck reference
                        await message.channel.send(("***" + messageContent[21:len(messageContent)] + " noises***"))
                    if messageContent.lower().startswith("cinnamon, become a "):
                        await message.channel.send(("***" + messageContent[19:len(messageContent)] + " noises***"))
                    if messageContent.lower().startswith("cinnamon, become an "):
                        await message.channel.send(("***" + messageContent[20:len(messageContent)] + " noises***"))
                    if (messageContent.lower().startswith("cinnamon, become ")) and not (messageContent.lower().startswith("cinnamon, become a ")) and not (messageContent.lower().startswith("cinnamon, become an ")) and not (messageContent.lower().startswith("cinnamon, become the")):
                        await message.channel.send(("***" + messageContent[17:len(messageContent)] + " noises***"))
                    if messageContent.lower().startswith("hugs cinnamon"):  # back to the futu- back-and-fourth
                        await message.channel.send(("***hugs " + message.author.display_name + " back***"))
                    if messageContent.lower().startswith("cinnamon, hug "):  # El gonish shive, tedd to grace about girl eliot
                        await message.channel.send(("***hugs " + messageContent[14:len(messageContent)] + "***"))
                    if messageContent.lower().startswith("cinnamon hug "):  # El gonish shive, tedd to grace about girl eliot
                        await message.channel.send(("***hugs " + messageContent[13:len(messageContent)] + "***"))
                    if messageContent.lower().startswith("cinnamon, attack "):
                        await message.channel.send(("***nibbles at " + messageContent[17:len(messageContent)] + "'s ankles***"))
                    if messageContent.lower().startswith("cinnamon attack "):
                        await message.channel.send(("***nibbles at " + messageContent[16:len(messageContent)] + "***"))
                    if messageContent.lower().startswith("*throws "):
                        await message.channel.send(("***catches " + messageContent[7:len(messageContent)] + "**"))
                    if messageContent.lower().startswith("*drops "):
                        await message.channel.send(("***catches " + messageContent[6:len(messageContent)] + "**"))
                    if messageContent.lower().startswith("cinnamon, kys"):  # Friendly stuff
                        await message.channel.send("a'k!")  # Sequential art, scarlet
                        Nope = 1000
                    if messageContent.lower().startswith("cinnamon kys"):  # varient spelling
                        await message.channel.send("a'k!")
                        Nope = 1000
                    if messageContent.lower().startswith("kys cinnamon"):  # varient spelling
                        await message.channel.send("a'k!")
                        Nope = 1000
                    if messageContent.lower().startswith("cinnamon, say"):  # Cause of several role play sessions...
                        await message.delete()
                        await message.channel.send((messageContent[14:len(messageContent)]))
                    if messageContent.lower().startswith("cinnamon say"):  # Cause of several role play sessions...
                        await message.delete()
                        await message.channel.send((messageContent[13:len(messageContent)]))
                    if messageContent.lower().startswith("cinnamon, distraction"):
                        if nsfw == 1:
                            await message.channel.send(["https://hentaihaven.org", "https://pornhub.com", "https://e621.net/", "https://www.redtube.com/", "https://rule34.xxx", "https://www.xvideos.com/", "https://rule34.paheal.net", "http://leekspin.com/", "http://www.staggeringbeauty.com/", "http://www.theuselessweb.com/", "http://ehentai.org/"][randint(0, 10)])
                        else:
                            await message.channel.send("I am being distracting! pay no attention to whatever " + message.author.display_name + " is doing!")
                    if messageContent.lower().startswith("cinnamon, conversation starter"):
                        with open(os.path.join(os.path.dirname(__file__), str("assets\\conversation starters.txt")), "r") as file:
                            tempVar2 = file.readlines()
                            await message.channel.send((tempVar2[randint(0, len(tempVar2) - 1)]))
                    if messageContent.lower().startswith("cinnamon, cat"):
                        await message.channel.send("I can't find a good image scraper for 100's of cat pictures ;-;")
                        # os.listdir(os.path.join(os.path.dirname(__file__), str("assets\\cats")))
                        # await message.channel.send( file=discord.File(os.path.join(os.path.dirname(__file__), str("assets\\cats\\"))+os.listdir(os.path.join(os.path.dirname(__file__), str("assets\\cats")))[randint(0, len(os.listdir(os.path.join(os.path.dirname(__file__), str("assets\\cats")))))]);
                    if messageContent.lower().startswith("cinnamon, rick roll"):  # Never gonna give you up!
                        await message.channel.send("""We're no strangers to love \nYou know the rules and so do I \nA full commitment's what I'm thinking of \nYou wouldn't get this from any other guy""")
                        await message.channel.send("""I just want to tell you how I'm feeling \nGotta make you understand""")
                        await message.channel.send("""Never gonna give you up, never gonna let you down \nNever gonna run around and desert you \nNever gonna make you cry, never gonna say goodbye \nNever gonna tell a lie and hurt you""")
                        await message.channel.send("""We've known each other for so long \nYour heart's been aching but you're too shy to say it \nInside we both know what's been going on \nWe know the game and we're gonna play it""")
                        await message.channel.send("""And if you ask me how I'm feeling \nDon't tell me you're too blind to see""")
                        await message.channel.send("""Never gonna give you up, never gonna let you down \nNever gonna run around and desert you \nNever gonna make you cry, never gonna say goodbye \nNever gonna tell a lie and hurt you""")
                        await message.channel.send("""Never gonna give you up, never gonna let you down \nNever gonna run around and desert you \nNever gonna make you cry, never gonna say goodbye \nNever gonna tell a lie and hurt you""")
                        await message.channel.send("""We've known each other for so long \nYour heart's been aching but you're too shy to say it \nInside we both know what's been going on \nWe know the game and we're gonna play it""")
                        await message.channel.send("""I just want to tell you how I'm feeling \nGotta make you understand""")
                        await message.channel.send("""Never gonna give you up, never gonna let you down \nNever gonna run around and desert you \nNever gonna make you cry, never gonna say goodbye \nNever gonna tell a lie and hurt you""")
                        await message.channel.send("""https://www.youtube.com/watch?v=dQw4w9WgXcQ""")
                    if messageContent.lower().startswith("cinnamon, body check"):
                        if nsfw == 1:
                            await message.channel.send("*glances down* (checking crap)")
                            await message.channel.send("test *test* **test** ***test*** <3")
                            time.sleep(0.5)
                            await message.channel.send("Chat functions: close enough")
                            await message.channel.send("q-q https https://68.media.tumblr.com/4a08436fcc3b506a0cf4bccffa00019c/tumblr_okpobdtKfC1twgfw0o2_r1_500.gif")
                            time.sleep(1)
                            if message.content.lower().startswith("q-q https"):
                                await message.channel.send("Meh, gifs aren't important anyway")
                            else:
                                await message.channel.send("gif test: close enough")
                        await message.channel.send("my body is ready")
                    if messageContent.lower().startswith("cinnamon, google ") and not messageContent.lower().startswith("cinnamon, google images "):
                        messageContent = messageContent[17:len(messageContent)].replace(" ", '+')
                        await message.channel.send(("https://www.google.com/search?q=" + messageContent))
                        break
                    if messageContent.lower().startswith("cinnamon, google images "):
                        messageContent = messageContent[24:len(messageContent)].replace(" ", '+')
                        await message.channel.send(("https://www.google.com/search?tbm=isch&q=" + messageContent))
                        break
                    if messageContent.lower().startswith("cinnamon, search ") and not messageContent.lower().startswith("cinnamon, google images "):
                        messageContent = messageContent[17:len(messageContent)].replace(" ", '+')
                        await message.channel.send(("https://www.google.com/search?q=" + messageContent))
                        break
                    if messageContent.lower().startswith("cinnamon, image search "):
                        messageContent = messageContent[23:len(messageContent)].replace(" ", '+')
                        await message.channel.send(("https://www.google.com/search?tbm=isch&q=" + messageContent))
                        break
                    if messageContent.lower().startswith("cinnamon, lovecalc"):
                        embed = discord.Embed(title="**:heart: Love calculation for " + messageContent.split(" ")[2] + " and " + messageContent.split(" ")[3] + "**:", description="Percentage: {}%".format(((int((str(re.sub('[^0123456789abcdefghijklmnopqrstuvwxyz ]', '', messageContent, 36))).split(" ")[2], 36) + int((str(re.sub('[^0123456789abcdefghijklmnopqrstuvwxyz ]', '', messageContent, 36))).split(" ")[3], 36)) % 101)), color=0xff7979)
                        embed.set_footer(text="(don't take this seriously, you can bang anyone (with consent))")
                        await message.channel.send(embed=embed)
                    if messageContent.lower().startswith("cinnamon, ping"):
                        t1 = time.perf_counter()
                        await client.send_typing(message.channel)
                        t2 = time.perf_counter()
                        embed = discord.Embed(title=None, description='Ping: {}ms'.format(round((t2 - t1) * 1000)), color=0x2874A6)
                        await message.channel.send(embed=embed)
                    if messageContent.lower().startswith("put up"):  #:)
                        for ii in range(len(messageContent)):
                            messageContent = messageContent[1:len(messageContent)]
                            if messageContent.lower().startswith("wolfjob"):
                                await message.channel.send(file=discord.File(str(os.path.join(os.path.dirname(__file__), str("assets\\misc\\wolfjob.jpg")))))
                    if messageContent.lower().startswith("cinnamon, eval("):
                        if "()" in messageContent or "{" in messageContent:
                            await message.channel.send("fuck you.")
                        else:
                            await message.channel.send(eval(messageContent[15:len(messageContent) - 1]))

                    # !!!~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~[~~~START IMAGE GET SECTION!!!]

                    if messageContent.lower().startswith("for shame"):
                        await message.channel.send(file=discord.File(str(os.path.join(os.path.dirname(__file__), str("assets\\misc\\flandersShame.png")))))
                    if nsfw == 1:  # note to self: edit in a sfw version of this, because its original purpose is to *call out* nsfw things
                        if messageContent.lower().startswith(":lewdsign:") or messageContent.startswith("lewdSign") or messageContent.lower().startswith(":lewd sign:") or messageContent.lower().startswith(":lewd_sign:"):
                            await message.channel.send(file=discord.File(str(os.path.join(os.path.dirname(__file__), str("assets\\lewdSign\\") + str(randint(0, 13)) + ".png"))))
                            messageContent = messageContent[1:len(messageContent)]

                    # !!!---------------------------------------------------------------------------------------------------------------[!!!START D&D SECTION!!!]

                    if messageContent.lower().startswith("roll d"):
                        messageContent = messageContent[6:len(messageContent)]
                        if messageContent.lower().startswith("4"):
                            await roll(4, messageContent, message)
                        if messageContent.lower().startswith("6"):
                            await roll(6, messageContent, message)
                        if messageContent.lower().startswith("8"):
                            await roll(8, messageContent, message)
                        if messageContent.lower().startswith("10"):
                            await roll(10, messageContent, message)
                        if messageContent.lower().startswith("12"):
                            await roll(12, messageContent, message)
                        if messageContent.lower().startswith("20"):
                            await roll(20, messageContent, message)
                        if messageContent.lower().startswith("100"):
                            await roll(100, messageContent, message)

                    messageContent = messageContent[1:len(messageContent)]

            else:  # If asleep:
                for i in range(len(messageContent)):  # scan message
                    if messageContent.lower() == "good morning, cinnamon":  # If message contains command to wake up
                        await message.channel.send("Ohayogozaimasu...")
                        Nope = 0  # release the kraken
                    if messageContent.lower() == "good morning cinnamon":  # If message contains command to wake up
                        await message.channel.send("Ohayogozaimasu...")
                        Nope = 0  # release the kraken
                    messageContent = messageContent[1:len(messageContent)]
                Nope -= 1  # I forget what this is for, but it's *probably* important

        #
        #                           commands that I don't know how to process in the actual discord commands api! aka all of them!
        #

        else:  # If command (still within on_message
            print("    " + str(time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())))
            print("!!>" + message.author.display_name + ": " + messageContent + "\n")

            # commands that can't be processed by discord's command api, because it is crap. Oh, wait, it's all the commands. huh.
            if messageContent.lower().startswith("!>vote"):
                with open(str(os.path.join(os.path.dirname(__file__), str("polls\\" + str(message.guild) + ".")) + str(message.channel) + '.CinnPoll'), 'r') as file:
                    fileBackup = file.readlines()
                with open(str(os.path.join(os.path.dirname(__file__), str("polls\\" + str(message.guild) + ".")) + str(message.channel) + '.CinnPoll'), 'a') as file:
                    fileBackup = file.readlines()
                    tempVar3 = 0
                    for i in range(len(fileBackup)):
                        if fileBackup[i].lower().startswith(messageContent.lower()[7:len(messageContent)]):
                            tempVar3 = 1
                            tempVar2 = 0
                            while fileBackup[i][tempVar2] != ":":
                                tempVar2 += 1
                            print(fileBackup[i])
                            fileBackup[i] = fileBackup[i][0:tempVar2] + ": " + str(int(fileBackup[i][tempVar2 + 1:len(fileBackup[i])]) + 1)
                    if tempVar3 == 0:
                        fileBackup.append("\n" + messageContent[7:len(messageContent)] + ": 1")
                with open(str(os.path.join(os.path.dirname(__file__), str("polls\\" + str(message.guild) + ".")) + str(message.channel) + '.CinnPoll'), 'w') as file:
                    for i in range(len(fileBackup)):
                        file.write(fileBackup[i])
            if messageContent.lower().startswith("!>new_poll"):
                with open(str(os.path.join(os.path.dirname(__file__), str("polls\\" + str(message.guild) + ".")) + str(message.channel) + '.CinnPoll'), 'w') as file:
                    file.write("poll: " + messageContent[11:len(messageContent)])
            if messageContent.lower().startswith("!>get_poll"):
                with open(str(os.path.join(os.path.dirname(__file__), str("polls\\" + str(message.guild) + ".")) + str(message.channel) + '.CinnPoll'), 'r') as file:
                    fileBackup = file.readlines()
                    tempVar2 = ""
                    for i in range(len(fileBackup)):
                        if i != 0:
                            tempVar2 = tempVar2 + "- " + str(fileBackup[i])[0:len(fileBackup[i])]
                    embed = discord.Embed(title=(str("------***" + str(fileBackup[0])[0:len(fileBackup[0])] + ":***") + "------"), description=str(tempVar2), color=0xffaaff)
                    await message.channel.send(embed=embed)
            if messageContent.lower().startswith("!>superhelp"):
                await message.channel.send(file=discord.File(str(os.path.join(os.path.dirname(__file__), str("assets\\Cinnamon Bot Help.html")))))
            if messageContent.lower() == "!>toggle_indev":
                if message.author.permissions_in(message.channel).manage_messages:
                    if inDev == 0:
                        # there are currently no in-dev features, lol
                        await message.channel.send("Boop boop be doop! Enabling in-dev features! This may break some formatting and/or reference files that don't yet exist. If you enable these features, things may break. You have been warned.")
                        inDev = 1
                    else:
                        await message.channel.send("Disabling in dev features, good choice. (certain residual effects may percist, such as muting. this toggle only enables/disabhles access to commands.)")
                        inDev = 0
                else:
                    await message.channel.send("You have to be chatmod+ (have the ability to delete messages) in order to toggle the indev features, dummy!")
            if messageContent.lower().startswith("!>mute"):
                if message.author.permissions_in(message.channel).manage_messages:
                    muted.append(messageContent[7:len(messageContent)].lower())
                    await message.channel.send(messageContent[7:len(messageContent)] + " muted! The mute will last until you unmute them, or I am disabled. You will have to manually reinstate the mute if I am restarted")
                else:
                    await message.channel.send("You must be of chatmod rank (able to delete messages) to toggle a mute! Don't worry, they're temporary")
            if messageContent.lower().startswith("!>unmute"):
                if message.author.permissions_in(message.channel).manage_messages:
                    try:
                        muted.remove(messageContent[9:len(messageContent)].lower())
                        await message.channel.send("unmuted " + messageContent[9:len(messageContent)])
                    except:
                        await message.channel.send("That person either doesn't exist or isn't muted")
                else:
                    await message.channel.send("You must be of chatmod rank (able to delete messages) to toggle a mute! Don't worry, they're temporary")
            if messageContent.lower().startswith("!>settings"):
                if message.author.permissions_in(message.channel).manage_messages:  # this command is for chat moderator rank or higher
                    with open(str(os.path.join(os.path.dirname(__file__), str("configs\\" + str(message.guild) + "\\")) + str(message.channel) + '.config'), 'r') as file:
                        tempVar2 = file.readlines()
                        tempVar3 = ""
                        for i in range(len(tempVar2)):
                            tempVar3 = str(tempVar3 + tempVar2[i] + "\n")
                    await message.channel.send("Current settings for this channel:\n\n" + tempVar3)
                else:
                    await message.channel.send("You don't have a high enough rank to use this command!")
            if messageContent.lower().startswith("!>getlog"):
                await message.author.send(file=discord.File(str(os.path.join(os.path.dirname(__file__), str("logs\\" + str(message.guild) + "\\")) + str(message.channel) + '.html')))
                await message.channel.send("Check your DM's!")
            if messageContent.lower().startswith("!>enable_nsfw"):
                if message.author.permissions_in(message.channel).manage_messages:
                    if nsfwCheck == 0:
                        await message.channel.send("Endble NSFW for thic channel? this action is irreversable! (enter command again to confirm)")
                        nsfwCheck = 1
                    else:
                        await message.channel.send("enabling...")
                        nsfw = 1
                        await createConfig(message)
                else:
                    await message.channel.send("You don't have a high enough rank to use this command!")
            if messageContent.lower().startswith("!>chatmod"):
                messageContent = message.content
                if message.channel.permissions_for(message.author).manage_messages:  # this command is for chat moderator rank or higher
                    if len(messageContent) > 11:
                        chatMod = int(messageContent[12])
                        await createConfig(message)
                    else:
                        with open(str(os.path.join(os.path.dirname(__file__), str("configs\\" + str(message.guild) + "\\")) + str(message.channel) + '.config'), 'r') as file:
                            tempVar2 = file.readlines()
                            await message.channel.send((tempVar2[0]))
                else:
                    await message.channel.send("You don't have a high enough rank to use this command!")
            if messageContent.lower().startswith("!>test"):
                await message.channel.send("Hey, you're not a doofus! Good job, you!")
            if messageContent.lower().startswith("!>sscstest"):
                await message.channel.send("Yep, not a doofus in the slightest ^_^")
            if messageContent.lower().startswith("!>goodbot"):
                await message.channel.send(("Arigatogozaimasu, " + message.author.display_name + "-sama! >.<"))
            if messageContent.lower().startswith("!>get_muted"):
                await message.channel.send(str(muted))


class Commands:  # There's probably "pass_message" or whatever. I didn't find it
    @commands.command(pass_context=True, no_pm=True)
    async def test(self, _ctx):
        print("can't even get a ping & pong to work")

    @commands.command(pass_context=True, no_pm=True)
    async def SSCSTest(self, _ctx):
        print("pass message you incompetant fish!")

    @commands.command(pass_context=True, no_pm=True)
    async def GoodBot(self, _ctx):
        print("you are an butt")

    @commands.command(pass_context=True, no_pm=True)
    async def chatmod(self, _ctx):
        print("the command api sucks")

    @commands.command(pass_context=True, no_pm=True)
    async def settings(self, _ctx):
        print("discord, pass message into commands, not ctx. this is literal child's play. I *need* message.channel, message.author, etc. But I have to pass everything through on_message for that. It's not that hard of a fix")

    @commands.command(pass_context=True, no_pm=True)
    async def getLog(self, _ctx):
        print("can't even get this to work")

    @commands.command(pass_context=True, no_pm=True)
    async def superHelp(self, _ctx):
        """----- this page is horribly formatted; get a better one with this!"""
        print("this command is processed in the main message handler")

    @commands.command(pass_context=True, no_pm=True)
    async def enable_indev(self, _ctx):
        #"don't"
        print("take a wild guess where this command is processed")

    @commands.command(pass_context=True, no_pm=True)
    async def mute(self, _ctx):
        print("this command is processed in the main message handler")

    @commands.command(pass_context=True, no_pm=True)
    async def unmute(self, _ctx):
        print("this command is processed in the main message handler")

    @commands.command(pass_context=True, no_pm=True)
    async def get_muted(self, _ctx):
        print("guess what? command can't be processed here, because there's no message passed!")


class Polling:  # polling commands start here! don't put normal ones in hereor you are a doofus!

    @commands.command(pass_context=True, no_pm=True)
    async def get_poll(self, _ctx):
        print("this command is processed in the main message handler")

    @commands.command(pass_context=True, no_pm=True)
    async def new_poll(self, _ctx):
        print("this command is processed in the main message handler")

    @commands.command(pass_context=True, no_pm=True)
    async def vote(self, _ctx):
        print("this command is processed in the main message handler")


# START BACKGROUND SECTION

async def background():
    counter = 1
    await client.wait_until_ready()
    while not client.is_closed:
        await asyncio.sleep(300)
        print("Still alive! " + str(counter))
        counter += 1


# END BACKGROUND SECTION

# client = commands.Bot(command_prefix=commands.when_mentioned_or('!>'), description='A very trustworthy bot', intents=discord.Intents.all())
# client = discord.Client(intents=discord.Intents.all())

loop = asyncio.get_event_loop()
loop.create_task(background())

while True:
    try:
        client.run(token)
    except:
        reconnectTime += 5
        print("FAILED TO RUN CLIENT, RETRYING IN " + str(reconnectTime) + "...")
        time.sleep(reconnectTime)
