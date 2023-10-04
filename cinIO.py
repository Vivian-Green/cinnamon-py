# handles IO, except for logging & reminders

import json
import os
import yaml

cachePath = os.path.join(os.path.dirname(__file__), str("cache\\"))
configsPath = os.path.join(os.path.dirname(__file__), str("configs\\"))

def loadConfig(fileName: str):
    filePath = os.path.join(configsPath + fileName)
    with open(filePath, 'r') as thisConfigFile:
        if "json" in fileName:
            return json.load(thisConfigFile)
        elif "yaml" in fileName:
            return yaml.safe_load(thisConfigFile)
        else:
            # todo: logging
            print(f"invalid file format for config {filePath}")

def loadCache(fileName: str):
    filePath = os.path.join(cachePath + fileName)
    if os.path.isfile(filePath):
        return json.load(open(filePath))
    else:
        overwriteCache(fileName, {})

def overwriteCache(fileName: str, newData):
    thisCachePath = os.path.join(cachePath + fileName)
    if os.path.isfile(thisCachePath):
        os.remove(thisCachePath)
    with open(thisCachePath, 'w') as f:
        json.dump(newData, f, indent=4)



def joinWithGlobalVars(textsToJoin):
    # todo: unsure if you can modify v directly in `for v in table:` in python, figure that out & apply here if relevant
    for i in range(len(textsToJoin)):
        if textsToJoin[i] in globals():
            textsToJoin[i] = globals()[textsToJoin[i]]
    return "".join(textsToJoin)



token = loadConfig("token.yaml")["token"]
config = loadConfig("config.yaml")
strings = loadConfig("strings.yaml")
minecraftConfig = loadConfig("minecraft.yaml")

simpleResponses = loadConfig("simpleResponses.json")

reminders = loadCache("reminders.json")

with open(os.path.join(os.path.dirname(__file__), str("assets\\conversation starters.txt")), "r") as file:
    conversationStarters = file.readlines()



#pre-processes any relevant configs
def processConfigs():
    strings['errors']['guildIsNotAdminGuildMsg'] = joinWithGlobalVars(strings['errors']['guildIsNotAdminGuildMsg'])
processConfigs()