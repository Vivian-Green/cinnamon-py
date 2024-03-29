# tokenizer, validateAgainstWhitelist and secureEval functions in this module written by https://github.com/Koenig-Heinrich-der-4te

import math
# this floods the namespace, I know, but this is intentional to allow expressions in /solve to not explicitly specify math.whatever()
from math import *

from cinIO import config, strings
from cinLogging import printHighlighted
from cinPalette import *
from cinShared import *

badParenthesisRegex = r"\(([ \t\n])*(-)*([ \t\n\d])*\)" # catches parenthesis that are empty, or contain only a number, including negative numbers

adminGuild = config["adminGuild"]
solveBlacklist = config["solveBlacklist"]
solveWhitelist = config["solveWhitelist"]
secureSolve = config["secureSolve"]

if secureSolve:
    printHighlighted(f"{highlightedColor}using whitelist for /solve")
else:
    printHighlighted(f"{highlightedColor}using (insecure) blacklist for /solve (ADMIN GUILD ONLY)")



def formatEvalResult(value):
    return f"{value:,}"
    
    

tokenizer = re.compile("[\.,\(\)\*\/\+\-% ]|\d+|\w+")
def validateAgainstWhitelist(expression):
    i = 0
    while i < len(expression):
        match = tokenizer.match(expression, i)
        if match is None:
            return False
        token = match.group()
        if token[0].isalpha() and token not in solveWhitelist:
            return False
        i = match.end()
    return True

def secureEval(expression):
    if validateAgainstWhitelist(expression):
        try:
            return formatEvalResult(eval(expression, globals(), vars(math)))
        except Exception:
            return strings['errors']['failedToResolveEval']
    else:
        return "Bad Math expression"

def validateAgainstBlacklist(expression):
    # check if eval contains bad words OR parenthesis with only whitespace
    containsBadParenthesis = re.findall(badParenthesisRegex, expression)
    containsBadWords = containsAny(expression, solveBlacklist)
    containsBadWords = containsBadWords or containsBadParenthesis
    return not containsBadWords

def insecureEval(expression):
    if validateAgainstBlacklist(expression):
        try:
            evalResult = formatEvalResult(eval(expression))
        except Exception:
            evalResult = strings['errors']['failedToResolveEval']
    else:
        evalResult = "fuck you. (noticed bad keywords in eval)"
    return evalResult
  

async def solve(message, messageContent):
    # default offsets are for /solve
    myCharOffset = [7, 0]
    if "cinnamon, eval(" in messageContent.lower():
        myCharOffset = [15, 1]

    textToEval = messageContent[myCharOffset[0]:len(messageContent) - myCharOffset[1]]

    if secureSolve:
        response = secureEval(textToEval)
    else:
        if adminGuild == message.guild.id:
            response = insecureEval(textToEval)
        else:
            response = strings['errors']['guildIsNotAdminGuildMsg']
    
    await message.channel.send(response)