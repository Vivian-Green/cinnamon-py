import os
import re
import time
import json
import discord


def loadConfig(name: str):
    return json.load(open(os.path.join(os.path.dirname(__file__), str("configs\\" + name))))


config = loadConfig("config.json")

defaultLoggingHtml = ""
with open(os.path.join(os.path.dirname(__file__), config["defaultLoggingHtml"]), "r") as defaultLoggingHtmlFile:
    defaultLoggingHtml = defaultLoggingHtmlFile.readlines()
    defaultLoggingHtmlFile.close()


def getURLs(string):
    return re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', string)


def hexToRGBA(hexValue, alpha):
    h = tuple(int(hexValue.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))
    return "rgba(" + str(h[0]) + ", " + str(h[1]) + ", " + str(h[2]) + ", " + str(alpha) + ")"


async def appendToLog(message: object, logFolderPath: str):
    # writes message to log file AND console
    messageContent = message.content

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
            file.write(
                f'{regularTextHTMLHeader} style="background-color: {color}">{timestamp}<br /><br />CINNAMON (bot): {messageContent}<br /></p>')
        except:
            file.write(f'{regularTextHTMLHeader}>{timestamp}<br /><br />CINNAMON (bot): FAILED TO LOG MESSAGE, MAY CONTAIN UNICODE CHARACTERS THAT I DON\'T WANT TO FIX AT THIS TIME<br /></p>')
    else:
        file.write(
            f'{regularTextHTMLHeader} style="background-color: {color}">{timestamp}<br /><br />{author_name}: {messageContent}<br /></p>')
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
            file.write(r'<a href="' + file_url +
                       r'" style="background-color: rgba(150, 200, 255, 0.2);">' + file_url + '</a>')

    file.write("\n")
    file.close()


async def tryToLog(message: object):
    messageContent = message.content
    global defaultLoggingHtml

    logFolderPath = os.path.join(os.path.dirname(
        __file__), str("logs\\" + str(message.guild)))
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

    # print current time
    print("  " + str(time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())))
    await appendToLog(message, logFolderPath)
