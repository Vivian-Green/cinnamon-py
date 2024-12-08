import math
from datetime import datetime, timedelta
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
    try:
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
        return [totalReminderTime, reminderText, isAbsoluteTime, isRelativeTime]
    except Exception as e:
        printErr(f"Failed to get reminder time: \n{e}")

async def newReminder(args, message):
    # called directly from command
    thisReminder = {
        "userIDs": [message.author.id]
    }

    timeAndReminderText = ["0", "default"]
    timeAndReminderText[0], timeAndReminderText[1], isAbsoluteTime, isRelativeTime = getTimeAndReminderText(message, args)

    if timeAndReminderText[0] is None:
        message.channel.send("No valid time format found")
        printErr("No valid time format found")
        return

    try:
        timeDiff = cinIO.getOrCreateUserData(str(message.author.id))["timezone"] * 3600 - time.timezone

        totalReminderTime = timeAndReminderText[0]# + timeDiff

        if isAbsoluteTime:
            # is unix timestamp
            thisTime = int(totalReminderTime)
        elif isRelativeTime:
            # is relative time - seconds from now
            thisTime = timeDiff + int(totalReminderTime)
        else:
            printErr("No valid time format found")
            return

        thisReminder.update({ # this is beautiful
            "text": timeAndReminderText[1] or "default text :3",
            "channelID": message.channel.id
        })

        messageText = (
            f"Set a reminder at <t:{thisTime}> (<t:{thisTime}:R>) for \n"
            f"> {timeAndReminderText[1]}\n\n"
            f"-# react to this message to also be pinged"
        )

        reminders[str(thisTime)] = thisReminder
        overwriteCache("reminders.json", reminders)

        reminderMessage = await message.channel.send(messageText)

        await reminderMessage.add_reaction("👍") # we don't care if this works, but it goes in the try/catch anyway
    except Exception as e:
        printErr(f"Failed to set reminder: {e}")




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


def getUserReminders(userID, requireAuthor = False):
    theseReminders = {
        key: reminder
        for key, reminder in reminders.items()
        if isinstance(reminder.get("userIDs"), list) and ( # if is list and
                reminder["userIDs"][0] == userID or # is author or
                (userID in reminder["userIDs"] and not requireAuthor) # is in reminder and not requireAuthor
        )
    }
    return theseReminders


async def reminderMenu(message: discord.message):
    userID = message.author.id
    myReminders = getUserReminders(userID, True)

    # Sort reminders by time (assuming 'reminderTime' is a timestamp)
    sortedReminders = sorted(myReminders.items(), key=lambda x: x[0])

    menuText = f"<@{userID}>'s reminders:"
    i = 0 # ima be honest ik there's a better way to do both of these at once but I'm writing this in python and this is faster than trying to find the right way
    for reminderTime, reminderData in sortedReminders:
        emoji_letter = f":regional_indicator_{chr(97 + i)}:"
        reminderText = reminderData.get("text")
        durationSeconds = int(reminderTime) - time.time()

        durationWeeks = 0
        durationDays = 0
        durationHours = 0
        durationMinutes = 0

        if durationSeconds >= 60 * 60 * 24 * 7:
            durationWeeks = math.floor(durationSeconds / (60 * 60 * 24 * 7))
            durationSeconds -= durationWeeks * (60 * 60 * 24 * 7)

        if durationSeconds >= 60 * 60 * 24:
            durationDays = math.floor(durationSeconds / (60 * 60 * 24))
            durationSeconds -= durationDays * (60 * 60 * 24)

        if durationSeconds >= 60 * 60:
            durationHours = math.floor(durationSeconds / (60 * 60))
            durationSeconds -= durationHours * (60 * 60)

        if durationSeconds >= 60:
            durationMinutes = math.floor(durationSeconds / 60)
            durationSeconds -= durationMinutes * 60

        durationStr = ""
        if durationWeeks > 0:
            durationStr += f"{durationWeeks} weeks " # todo: handle week
        if durationDays > 0:
            durationStr += f"{durationDays} days, " # todo: handle day
        if durationHours > 0:
            durationStr += f"{durationHours}h"
        if durationMinutes > 0:
            durationStr += f"{durationMinutes}m"
        durationStr += f"{round(durationSeconds)}s"
        menuText += f"\nReminder at <t:{reminderTime}> (<t:{reminderTime}:R>) for:\n> {emoji_letter}`    ` {reminderText}"
        i += 1
    menuText += "\n\nto delete a reminder, click below:"

    myMessage = await message.channel.send(menuText)

    for i in range(len(sortedReminders)): # code that breaks if it contains any
        emoji_letter = chr(127462 + i)
        print(emoji_letter)
        await myMessage.add_reaction(emoji_letter)

async def handleReminderMenuReaction(reaction, user):
    i = ord(reaction.emoji) - ord('🇦')  # 0-25 for a-z regional indicators
    staleMessageTimeDelta = timedelta(seconds=60)  # todo: move to config

    messageTimezone = reaction.message.created_at.tzinfo
    nowButAware = datetime.now(messageTimezone)

    if reaction.message.created_at < nowButAware - staleMessageTimeDelta:
        await reaction.message.edit(content="> old reminder menu, `!>reminders` to re-open")
        return

    if reaction.message.mentions[0].id != user.id:
        await reaction.message.channel.send(f"<@{user.id}> not only would that not work, but if it did, it would delete your own reminder without telling you what it was")
        return

    # Get the corresponding reminder data
    userID = user.id
    myReminders = getUserReminders(userID)


    if len(myReminders) < i + 1:
        await reaction.message.channel.send(
            f"Don't add your own emoji- \n`OOB err on index {i} for reminders of length {len(myReminders)}`")

    # todo: understand this line
    sortedReminders = sorted(myReminders.items(), key=lambda x: x[0])
    reminderTime, reminderData = sortedReminders[i]


    if len(reminderData["userIDs"]) == 1:
        delReminderByTimestamp(reminderTime)
        await reaction.message.channel.send(f"Deleted reminder at <t:{reminderTime}:F> \nTo restore the reminder, use this command: \n`!>reminder <t:{reminderTime}:F> {reminderData['text']}`")

    else:
        reminderData["userIDs"].remove(userID)
        reminders[reminderTime] = reminderData
        overwriteCache("reminders.json", reminders)

        await reaction.message.channel.send(f"Removed you from a reminder at <t:{reminderTime}:F> \nTo restore the reminder, use this command: \n`!>reminder <t:{reminderTime}:F> {reminderData['text']}`")

    await reaction.message.edit(content="> old reminder menu, `!>reminders` to re-open")



async def checkForReminders(client):
    closestReminderTime, lateReminders = getReminderStatus()

    for reminder in lateReminders:
        if not (isinstance(reminder["userIDs"], list) and len(reminder["userIDs"]) > 0): # todo: flag for deletion
            print("wher users for this one?")
            continue

        channel = client.get_channel(reminder["channelID"])
        author = client.get_user(reminder["userIDs"][0])

        # Format the base message
        if reminder["text"] != "":
            messageText = f'{author.mention} reminder: \n> {reminder["text"]}'
        else:
            messageText = f'{author.mention} reminder: \n> {"default text :3"}'

        # Send the message to the channel or direct to the author
        if channel:
            # Mention all non-author users
            mentions = [f"<@{userID}>" for userID in reminder["userIDs"][1:]]  # Skip the author (first user)
            if len(mentions) > 0:
                if len(mentions) > 50: mentions = mentions[:49]  # todo: fix magic 50 user cap for this. Shouldn't be hit, but like, magic.
                messageText += "\n\n-# " + " ".join(mentions)  # Append non-author mentions

            await channel.send(messageText)
        else:
            await author.send(messageText)

async def handleReminderReaction(reaction, user):
    if not (reaction and reaction.message): return
    message = reaction.message

    if (not user) or user.bot: return
    if not message.author.bot: return
    lowerContent = message.content.lower()

    if not ("reminder" in lowerContent): return

    if ">'s reminders:" in lowerContent:  # on user reaction to a reminder menu message sent by a bot
        if len(reaction.emoji) == 1 and '🇦' <= reaction.emoji[0] <= '🇿':  # with an alpha regional indicator emoji
            await handleReminderMenuReaction(reaction, user)
    elif "-# react to this message to also be pinged" in lowerContent:
        # Extract the reminder timestamp from the message content
        # Example format in message: "<t:timestamp>"
        start = message.content.find("<t:") + 3
        end = message.content.find(">", start)
        if start == -1 or end == -1:
            return  # Invalid or malformed message

        try:
            reminderTimeStr = message.content[start:end]
        except ValueError:
            return  # Invalid timestamp

        # Ensure the reminder exists
        if reminderTimeStr not in reminders:
            await message.channel.send("Error: Could not find the associated reminder.")
            return

        if user.id in reminders[reminderTimeStr]["userIDs"]:
            addedOrRemoved = "removed"
            reminders[reminderTimeStr]["userIDs"].remove(user.id)
        else:
            addedOrRemoved = "added"
            reminders[reminderTimeStr]["userIDs"].append(user.id)

        await message.channel.send(f"{user.mention}, you've been {addedOrRemoved} from the reminder!")
        overwriteCache("reminders.json", reminders)