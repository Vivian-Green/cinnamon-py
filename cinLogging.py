# handles logging functions

import os
import time
import discord

from cinIO import config
from cinShared import *
from cinPalette import *

defaultLoggingHTMLPath = os.path.join(os.path.dirname(__file__), config["defaultLoggingHtml"])
with open(defaultLoggingHTMLPath, "r") as defaultLoggingHtmlFile:
    defaultLoggingHtml = defaultLoggingHtmlFile.readlines()

regularTextHTMLHeader = '<p class="text"'
indentedLoggingCSSHeader = '<p class="indentedText"'

def getURLs(string):
    return re.findall(urlRegex, string)

def hexToRGBA(hexValue, alpha):
    # todo: what the fuck is this doing
    h = tuple(int(hexValue.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))
    return "rgba(" + str(h[0]) + ", " + str(h[1]) + ", " + str(h[2]) + ", " + str(alpha) + ")"

# ---------- get things from message

class MessageInfo:
    def __init__(self, color, timestamp, author_name):
        self.color = color
        self.timestamp = timestamp
        self.author_name = author_name

def getMessageInfo(message: discord.message):
    color = hexToRGBA(str(message.author.color), 0.5)
    timestamp = message.created_at.strftime("%a, %d %b %Y %H:%M:%S +0000")
    author_name = message.author.display_name

    return MessageInfo(color, timestamp, author_name)

def getLogFilePath(message: discord.message):
    # gets the path to the log file a given message should be in, after ensuring it exists
    logFolderPath = os.path.join(os.path.dirname(__file__), str("logs\\" + str(message.guild)))
    logFilePath = os.path.join(logFolderPath, str(message.channel) + '.html')

    # ensure folder exists
    os.makedirs(logFolderPath, exist_ok=True)

    # ensure file exists
    if not os.path.isfile(logFilePath):
        with open(logFilePath, "w+") as logFile:
            logFile.writelines(defaultLoggingHtml)
    return logFilePath

def getAttachments(message: discord.message):
    attachments = [attachment.url for attachment in message.attachments]

    for attachment in message.attachments:
        if attachment.url not in message.content and attachment.url not in attachments:
            attachments.append(attachment.url)

    # Get message.embeds, message.attachments, and urls in message.contents, and tape them together
    embeds = [str(embed.url) for embed in message.embeds]
    attachments = getURLs(str(message.attachments))

    attachments.extend(embeds)
    attachments.extend(getURLs(message.content))

    return attachments

# ---------- end get things from message
# ---------- print/log message of type

def printCinnamonMessage(message: discord.message):
    indentedMessageContent = message.content.replace("\n", "\n      " )
    print(f'    {labelColor}>>>CINNAMON:\n      {labelColor}{indentedMessageContent}')

def printDiscordMessage(message: discord.message):
    indentedMessageContent = message.content.replace("\n", "\n      " )
    messageInfo = getMessageInfo(message)
    print(f'    {labelColor}{messageInfo.author_name}:\n      {defaultColor}{indentedMessageContent}')

def logCinnamonMessage(message: discord.message):
    messageInfo = getMessageInfo(message)
    timestamp = message.created_at.strftime("%a, %d %b %Y %H:%M:%S +0000")

    logFilePath = getLogFilePath(message)
    with open(logFilePath, 'a', encoding='utf-8') as logFile:
        try:
            logFile.write(f'{regularTextHTMLHeader} style="background-color: {messageInfo.color}">{messageInfo.timestamp}<br /><br />CINNAMON (bot): {message.content}<br /></p>')
        except Exception as err:
            #todo: log err
            logFile.write(f'{regularTextHTMLHeader}>{timestamp}<br /><br />CINNAMON (bot): FAILED TO LOG MESSAGE<br /></p>')
def logDiscordMessage(message: discord.message):
    messageInfo = getMessageInfo(message)

    logFilePath = getLogFilePath(message)
    with open(logFilePath, 'a', encoding='utf-8') as logFile:
        logFile.write(f'{regularTextHTMLHeader} style="background-color: {messageInfo.color}">{messageInfo.timestamp}<br /><br />{messageInfo.author_name}: {message.content}<br /></p>')

def printLabelWithInfo(label, info = None):
    if info:
        info = f": {highlightedColor}{info}"
        print(f"  {labelColor}{label}: {highlightedColor}{info}")
    else:
        print(f"  {labelColor}{label}")
def printHighlighted(text):
    print(f"  {highlightedColor}{text}")
def printDefault(text):
    print(f"  {defaultColor}{text}")
def printErr(text):
    print(f"  {errorColor}{text}")
def printDebug(text):
    print(f"  {debugColor}{text}")



def logAttachmentsFromMessage(message):
    attachments = getAttachments(message)
    messageInfo = getMessageInfo(message)

    # Loop through every attached file
    logFilePath = getLogFilePath(message)
    with open(logFilePath, 'a', encoding='utf-8') as logFile:
        for i in range(len(attachments)):
            file_url = attachments[i][0:-3]
            if len(file_url) > 0:
                printHighlighted(file_url)

                # If the attached file is an image
                urlIsImage = ".jpg" in file_url or ".png" in file_url or ".webp" in file_url or ".gif" in file_url
                if urlIsImage:
                    # write html for image to log
                    logFile.write(f'\n{indentedLoggingCSSHeader} style="background-color: {messageInfo.color}"><img src="{file_url}" alt="{file_url}" class="embeddedImage" style="max-height: 50%; height: auto; loading="lazy""></p>')
                else:
                    # add clickable link into log
                    logFile.write(r'<a href="' + file_url + r'" style="background-color: rgba(150, 200, 255, 0.2);">' + file_url + '</a>')

        logFile.write("\n")

# ---------- end print/log message of type


async def tryToLog(message: discord.message):
    global defaultLoggingHtml

    # print current time
    printLabelWithInfo(time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()))

    if message.author.bot:
        printCinnamonMessage(message)
        logCinnamonMessage(message)
    else:
        printDiscordMessage(message)
        logDiscordMessage(message)
        logAttachmentsFromMessage(message)
