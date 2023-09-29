import time

from cinLogging import printErr, printDefault, printDebug
from cinShared import *

from cinIO import config, reminders, overwriteCache

bigNumber = config["bigNumber"]
relativeTimeRegex = r"([\d]+[hdmsMyY])"



def relativeTimeToSeconds(relativeTimes):
    printDebug(relativeTimes)
    minuteInSeconds = 60
    hourInSeconds = minuteInSeconds*60
    dayInSeconds = hourInSeconds*24
    weekInSeconds = dayInSeconds*7
    yearInSeconds = dayInSeconds*365

    totalRelativeTime = 0
    for v in relativeTimes:
        timeFlavor = v[-1]#the letter specifying which type of time unit is being specified
        timeUnitsStr = v[0:-1]
        timeUnits = int(timeUnitsStr)
        if timeFlavor == "s":
            totalRelativeTime += timeUnits
        elif timeFlavor == "m":
            totalRelativeTime += timeUnits * minuteInSeconds
        elif timeFlavor == "h":
            totalRelativeTime += timeUnits * hourInSeconds
        elif timeFlavor == "d":
            totalRelativeTime += timeUnits * dayInSeconds
        elif timeFlavor == "w":
            totalRelativeTime += timeUnits * weekInSeconds
        elif timeFlavor == "y":
            totalRelativeTime += timeUnits * yearInSeconds

    return totalRelativeTime

def getTimeAndReminderText(args):
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

    return [totalRelativeTime, reminderText]

def newReminder(args, message):
    thisReminder = {
        "userID": message.author.id
    }
    timeAndReminderText = getTimeAndReminderText(args)

    thisTime = int(time.time() + timeAndReminderText[0])
    thisReminder["text"] = timeAndReminderText[1]
    thisReminder["channelID"] = message.channel.id

    reminders[str(thisTime)] = thisReminder
    overwriteCache("reminders.json", reminders)


def getReminderStatus():
    checkingTime = time.time() + 1  # check 1 second ahead bc ping
    closestReminderTime = bigNumber

    keysToRemove = []
    lateReminders = []

    for key in reminders:
        thisReminderTime = int(key)
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