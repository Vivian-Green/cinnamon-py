# handles logging functions

import os
import time
import discord

from cinIO import config
from cinShared import *
from cinPalette import *

# todo: don't just strip unicode

defaultLoggingHTMLPath = os.path.join(os.path.dirname(__file__), config["defaultLoggingHtml"])
with open(defaultLoggingHTMLPath, "r") as defaultLoggingHtmlFile:
    defaultLoggingHtml = defaultLoggingHtmlFile.readlines()

regularTextHTMLHeader = '<p class="text"'
indentedLoggingCSSHeader = '<p class="indentedText"'





def hexToRGBA(hexValue, alpha):
    # todo: what the fuck is this doing
    h = tuple(int(hexValue.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))
    return "rgba(" + str(h[0]) + ", " + str(h[1]) + ", " + str(h[2]) + ", " + str(alpha) + ")"



# ---------- get things from message

class MessageInfo:
    def __init__(self, color, timestamp, author_name: str, logFilePath, content: str = "", isDM: bool = False):
        self.color = color
        self.timestamp = timestamp
        self.author_name = author_name
        self.logFilePath = logFilePath
        self.content = content

        self.isDM = isDM

# todo: memoize
def getMessageInfo(message: discord.message):
    if not message: return None

    try: color = hexToRGBA(str(message.author.color), 0.5)
    except: color = "#aa44bb"
    try: timestamp = message.created_at.strftime("%a, %d %b %Y %H:%M:%S +0000")
    except: timestamp = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()) # default to now
    try: logFilePath = getLogFilePath(message)
    except: logFilePath = None

    return MessageInfo(color, timestamp, message.author.display_name, logFilePath, stripUnicode(message.content), message.guild is None)



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
    print(f'    {labelColor}{message.guild.id}.{message.channel.name} >>>CINNAMON:\n      {labelColor}{indentedMessageContent}')

def printDiscordMessage(message: discord.message):
    indentedMessageContent = message.content.replace("\n", "\n      " )
    print(f'    {labelColor}{message.guild.id}.{message.channel.name} {message.author.display_name}:\n      {defaultColor}{indentedMessageContent}')

def logCinnamonMessage(message: discord.message):
    messageInfo = getMessageInfo(message)
    with open(messageInfo.logFilePath, 'a', encoding='utf-8') as logFile:
        logFile.write(f'{regularTextHTMLHeader} style="background-color: {messageInfo.color}">{messageInfo.timestamp}<br /><br />CINNAMON (bot): {messageInfo.content}<br /></p>')

def logDiscordMessage(message: discord.message):
    messageInfo = getMessageInfo(message)
    with open(messageInfo.logFilePath, 'a', encoding='utf-8') as logFile:
        logFile.write(f'{regularTextHTMLHeader} style="background-color: {messageInfo.color}">{messageInfo.timestamp}<br /><br />{messageInfo.author_name}: {messageInfo.content}<br /></p>')



# ---------- end print/log message of type

async def tryToLog(message: discord.message):
    printLabelWithInfo(time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()))

    if message.author.bot:
        printCinnamonMessage(message)
        logCinnamonMessage(message)
    else:
        printDiscordMessage(message)
        logDiscordMessage(message)
        logAttachmentsFromMessage(message)

# ----------



# ----------

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

    log_entries = []

    for attachment in attachments:
        file_url = attachment[0:-3]
        if len(file_url) > 0:
            printHighlighted(file_url)

            # Determine if the attached file is an image or not
            if any(ext in file_url for ext in [".jpg", ".png", ".webp", ".gif"]):
                log_entries.append(
                    f'\n{indentedLoggingCSSHeader} style="background-color: {messageInfo.color};">'
                    f'<img src="{file_url}" alt="{file_url}" class="embeddedImage" style="max-height: 50%; height: auto;" loading="lazy">'
                    f'</p>'
                )
            else:
                log_entries.append(
                    f'\n<a href="{file_url}" style="background-color: rgba(150, 200, 255, 0.2);">{file_url}</a>'
                )

    with open(messageInfo.logFilePath, 'a', encoding='utf-8') as logFile:
        logFile.write(f"\n{' '.join(log_entries)}\n")
