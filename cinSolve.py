from cinIO import config, strings
from cinShared import *

badParenthesisRegex = r"\(([ \t\n])*(-)*([ \t\n\d])*\)" #catches parenthesis that are empty, or contain only a number, including negative numbers

adminGuild = config["adminGuild"]
badEvalWords = config["badEvalWords"]
async def solve(message, messageContent):
    isFromAdminGuild = adminGuild == message.guild.id
    if isFromAdminGuild:
        # default offsets are for /solve
        myCharOffset = [7, 0]
        if "cinnamon, eval(" in messageContent.lower():
            myCharOffset = [15, 1]

        textToEval = messageContent[myCharOffset[0]:len(messageContent) - myCharOffset[1]]

        # check if eval contains bad words OR parenthesis with only whitespace
        containsBadParenthesis = re.findall(badParenthesisRegex, textToEval)
        containsBadWords = containsAny(textToEval, badEvalWords)
        containsBadWords = containsBadWords or containsBadParenthesis

        if containsBadWords:
            await message.channel.send("fuck you. (noticed bad keywords in eval)")
        else:
            try:
                evalResult = eval(textToEval)
            except Exception:
                evalResult = "snake said no (python couldn't resolve eval)"

            await message.channel.send(evalResult)
    else:
        await message.channel.send(strings['errors']['guildIsNotAdminGuildMsg'])