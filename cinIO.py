# handles IO, except for logging & reminders

import json
import os

cachePath = os.path.join(os.path.dirname(__file__), str("cache\\"))
configsPath = os.path.join(os.path.dirname(__file__), str("configs\\"))

def loadConfig(fileName: str):
    return json.load(open(os.path.join(configsPath + fileName)))

def loadCache(fileName: str):
    return json.load(open(os.path.join(cachePath + fileName)))

def overwriteCache(fileName: str, newData):
    thisCachePath = os.path.join(cachePath + fileName)
    os.remove(thisCachePath)
    with open(thisCachePath, 'w') as f:
        json.dump(newData, f, indent=4)



def joinWithGlobalVars(textsToJoin):
    # todo: unsure if you can modify v directly in `for v in table:` in python, figure that out & apply here if relevant
    for i in range(len(textsToJoin)):
        if textsToJoin[i] in globals():
            textsToJoin[i] = globals()[textsToJoin[i]]
    return "".join(textsToJoin)



token = loadConfig("token.json")["token"]
config = loadConfig("config.json")
strings = loadConfig("strings.json")
simpleResponses = loadConfig("simpleResponses.json")
minecraftConfig = loadConfig("minecraft.json")
reminders = loadCache("reminders.json")

with open(os.path.join(os.path.dirname(__file__), str("assets\\conversation starters.txt")), "r") as file:
    conversationStarters = file.readlines()



#pre-processes any relevant configs
def processConfigs():
    strings['errors']['guildIsNotAdminGuildMsg'] = joinWithGlobalVars(strings['errors']['guildIsNotAdminGuildMsg'])
processConfigs()