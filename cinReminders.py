import datetime
import math
import time
import dateparser
import discord

import cinIO
from cinLogging import printErr, printDefault, printDebug
from cinShared import *

from cinIO import config, reminders, overwriteCache, userData

bigNumber = config["bigNumber"]
relativeTimeRegex = r"([\d]+[hdmsMyY])"
discordTimestampRegex = r"<t:(\d+):[DTRFdtrf]>"
absoluteTimeRegex = r"@([\w:]+)"



def relativeTimeToSeconds(relativeTimes):
    time_units = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400, 'w': 604800, 'y': 31536000}
    total_relative_time = 0

    for v in relativeTimes:
        time_flavor = v[-1]
        time_units_str = v[0:-1]

        if time_flavor in time_units:
            total_relative_time += int(time_units_str) * time_units[time_flavor]

    return total_relative_time


def getTimeAndReminderText(message: discord.message, args):
    timeDiff = cinIO.getOrCreateUserData(str(message.author.id))["timezone"] * 3600 - time.timezone
    print(timeDiff)

    reminderText = " ".join(args[1:])  # Combine the reminder text

    # Find Discord timestamps in the arguments
    discordTimestamps = re.findall(discordTimestampRegex, args[0])
    print(f"Discord timestamps: {discordTimestamps}")  # Debug statement

    # Find relative times in the arguments
    relativeTimesWithIndices = re.finditer(relativeTimeRegex, args[0])
    relativeTimes = [v.group() for v in relativeTimesWithIndices]
    print(f"Relative times: {relativeTimes}")  # Debug statement

    # Find absolute times in the arguments
    absoluteTimes = re.findall(absoluteTimeRegex, args[0])
    print(f"Absolute times: {absoluteTimes}")  # Debug statement

    totalReminderTime = None
    if len(discordTimestamps) > 0:
        totalReminderTime = int(discordTimestamps[0])
    elif len(relativeTimes) > 0:
        totalReminderTime = time.time() + relativeTimeToSeconds(relativeTimes)
    elif len(absoluteTimes) > 0:
        absoluteTime = dateparser.parse(" ".join(absoluteTimes))
        totalReminderTime = absoluteTime.timestamp()
        print(totalReminderTime)
    else:
        printErr("No valid time format found")

    isAbsoluteTime = len(discordTimestamps) > 0 or len(absoluteTimes) > 0
    isRelativeTime = len(relativeTimes) > 0

    print(f"getTimeAndReminderText: {totalReminderTime}")
    return [int(totalReminderTime), reminderText, isAbsoluteTime, isRelativeTime]




'''def getTimeAndReminderText(args):
    reminderText = ""

    relativeSyntaxRegex = re.compile(relativeTimeRegex)
    relativeTimesWithIndices = relativeSyntaxRegex.finditer(args[0])
    relativeTimes = []
    for v in relativeTimesWithIndices:
        relativeTimes.append(v.group())

    printDefault(relativeTimes)

    totalRelativeTime = None
    if len(relativeTimes) > 0:
        totalRelativeTime = relativeTimeToSeconds(relativeTimes)
        if len(args) > 1:
            reminderText = " ".join(args[1:])
    else:
        printErr("len(relativeTimes) <= 0")

    return [totalRelativeTime, reminderText]'''

async def newReminder(args, message):
    # called directly from command
    thisReminder = {
        "userID": message.author.id
    }
    timeAndReminderText = ["0", "default"]
    timeAndReminderText[0], timeAndReminderText[1], isAbsoluteTime, isRelativeTime = getTimeAndReminderText(message, args)

    if timeAndReminderText[0] is not None:
        timeDiff = cinIO.getOrCreateUserData(str(message.author.id))["timezone"] * 3600 - time.timezone
        print(f"timeDiff: {timeDiff}")  # Debug statement

        totalReminderTime = timeAndReminderText[0]# + timeDiff
        print(f"totalReminderTime: {totalReminderTime}")  # Debug statement
        print(f"time.time(): {time.time()}")

        if isAbsoluteTime:
            # is unix timestamp
            thisTime = int(round(totalReminderTime))
            print(f"unix time: {thisTime}")  # Debug statement
        elif isRelativeTime:
            # is relative time - seconds from now
            thisTime = int(round(timeDiff + totalReminderTime))
            print(f"unix time from relative: {thisTime}")  # Debug statement
        else:
            printErr("No valid time format found")
            return
    else:
        printErr("No valid time format found")
        return

    thisReminder["text"] = timeAndReminderText[1]
    thisReminder["channelID"] = message.channel.id

    if timeAndReminderText[1] == "":
        timeAndReminderText[1] = "default text :3"
    messageText = f"Set a reminder at <t:{thisTime}> for \n> {timeAndReminderText[1]}"

    reminders[str(thisTime)] = thisReminder
    overwriteCache("reminders.json", reminders)

    await message.channel.send(messageText)




'''def newReminder(args, message):
    thisReminder = {
        "userID": message.author.id
    }
    timeAndReminderText = getTimeAndReminderText(args)

    thisTime = int(time.time() + timeAndReminderText[0])
    thisReminder["text"] = timeAndReminderText[1]
    thisReminder["channelID"] = message.channel.id

    reminders[str(thisTime)] = thisReminder
    overwriteCache("reminders.json", reminders)'''

def delReminderByTimestamp(timestamp):
    del reminders[timestamp]
    cinIO.overwriteCache("reminders.json", cinIO.reminders)

def getReminderStatus():
    checkingTime = time.time() + 1  # check 1 second ahead bc ping
    closestReminderTime = bigNumber

    keysToRemove = []
    lateReminders = []

    for key in reminders:
        # todo: handle key isn't
        thisReminderTime = int(round(float(key)))
        if thisReminderTime < checkingTime:
            keysToRemove.append(key)
            lateReminders.append(reminders[key])

        elif thisReminderTime - checkingTime < closestReminderTime:
            closestReminderTime = thisReminderTime - checkingTime

    if len(keysToRemove) > 0:
        for v in keysToRemove:
            del reminders[v]
        overwriteCache("reminders.json", reminders)

    return [closestReminderTime, lateReminders]

def getUserReminders(userID):
    theseReminders = {k: v for k, v in reminders.items() if v['userID'] == userID}
    return theseReminders

async def reminderMenu(message: discord.message):
    userID = message.author.id
    myReminders = getUserReminders(userID)

    # Sort reminders by time (assuming 'reminderTime' is a timestamp)
    sortedReminders = sorted(myReminders.items(), key=lambda x: x[0])

    menuText = f"<@{userID}>'s reminders:"
    i = 0 # ima be honest ik there's a better way to do both of these at once but I'm writing this in python and this is faster than trying to find the right way
    for reminderTime, reminderData in sortedReminders:
        emoji_letter = f":regional_indicator_{chr(97 + i)}:"
        reminderText = reminderData.get("text")
        menuText += f"\nReminder at <t:{reminderTime}> for:\n> {emoji_letter}`    ` {reminderText}"
        i += 1
    menuText += "\n\nto delete a reminder, click below:"

    myMessage = await message.channel.send(menuText)

    for i in range(len(sortedReminders)): # code that breaks if it contains any
        emoji_letter = chr(127462 + i)
        print(emoji_letter)
        await myMessage.add_reaction(emoji_letter)