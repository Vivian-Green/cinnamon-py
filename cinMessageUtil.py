import os
import time
import discord

from cinShared import *
from cinIO import defaultLoggingHtml

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

    # todo: don't just strip unicode
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