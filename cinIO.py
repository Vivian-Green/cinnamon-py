# handles IO, except for logging & reminders

import json
import os
import yaml
import time

cachePath = os.path.join(os.path.dirname(__file__), str("cache\\"))
configsPath = os.path.join(os.path.dirname(__file__), str("configs\\"))

def ensureDirs(dirs):
    for directory in dirs:
        if not os.path.isdir(directory):
            os.makedirs(directory, exist_ok=True)

ensureDirs([cachePath, configsPath])


def writeConfig(fileName: str, configData: dict):
    filePath = os.path.join(configsPath, fileName)

    # Determine file format based on the file extension
    if fileName.endswith(".json"):
        with open(filePath, 'w') as configFile:
            json.dump(configData, configFile, indent=2)
    elif fileName.endswith(".yaml") or fileName.endswith(".yml"):
        with open(filePath, 'w') as configFile:
            yaml.dump(configData, configFile, default_flow_style=False)
    else:
        # todo: logging
        print(f"Invalid file format for config {filePath}")

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

def loadCache(fileName: str, default_value=None):
    filePath = os.path.join(cachePath, fileName)
    
    # Check if the file exists
    parentDir = os.path.dirname(filePath)
    os.makedirs(parentDir, exist_ok=True)
    
    if os.path.isfile(filePath):
        with open(filePath, 'r') as f:
            return json.load(f)
    else:
        # Use the provided default value or an empty dictionary
        if default_value is None:
            default_value = {}
        
        # Write the default value to the cache and return it
        overwriteCache(fileName, default_value)
        return default_value

def overwriteCache(fileName: str, newData):
    thisCachePath = os.path.join(cachePath, fileName)
    
    # Ensure parent directories exist
    parentDir = os.path.dirname(thisCachePath)
    os.makedirs(parentDir, exist_ok=True)
    
    # Remove existing file if it exists
    if os.path.isfile(thisCachePath):
        os.remove(thisCachePath)
    
    # Write new data to the cache file
    with open(thisCachePath, 'w') as f:
        json.dump(newData, f, indent=4)

def joinWithGlobalVars(textsToJoin):
    result = []
    for text in textsToJoin:
        if text in globals():
            result.append(globals()[text])
        else:
            result.append(text)
    return "".join(result)

token = loadConfig("token.yaml")["token"]
config = loadConfig("config.yaml")
strings = loadConfig("strings.yaml")

simpleResponses = loadConfig("simpleResponses.json")
reminders = loadCache("reminders.json")
userData = loadCache("userData.json")

with open(os.path.join(os.path.dirname(__file__), str("assets\\conversation starters.txt")), "r") as file:
    conversationStarters = file.readlines()

defaultLoggingHtmlPath = os.path.join(os.path.dirname(__file__), config["defaultLoggingHtml"])
with open(defaultLoggingHtmlPath, "r") as defaultLoggingHtmlFile:
    defaultLoggingHtml = defaultLoggingHtmlFile.readlines()

#pre-processes any relevant configs
def processConfigs():
    strings['errors']['guildIsNotAdminGuildMsg'] = joinWithGlobalVars(strings['errors']['guildIsNotAdminGuildMsg'])

'''
userData should look like:
{
    "1077404176876838922": {  <- that number is a userID
        timezone: 4
    }
}
'''

# todo: function to add a user to userData

def newUserData(userID: str):
    # use cinnamon's timezone as default- get hyucked people that actually use cinmin
    userData[userID] = {"timezone": time.timezone/3600} # todo: put default userData somewhere in a config
    overwriteCache("userData.json", userData)
    return userData[userID]

def getOrCreateUserData(userID: str):
    # Check if userID is in userData dict
    thisUserData = userData.get(userID)

    # If it is, return their data
    if thisUserData is not None:
        overwriteCache("userData.json", userData)
        return thisUserData
    else:
        # If it isn't, add it with default values
        return newUserData(userID)

processConfigs()