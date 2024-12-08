# handles logging functions

import time
import discord

from cinMessageUtil import getMessageInfo, getAttachments
from cinPalette import *

regularTextHTMLHeader = '<p class="text"'
indentedLoggingCSSHeader = '<p class="indentedText"'




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
