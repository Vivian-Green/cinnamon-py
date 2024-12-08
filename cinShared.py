import re

urlRegex = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'



def containsAny(textToCheck: str, texts):
    # if textToCheck contains any of texts, return the length of the matching text, which is truthy unless text is ""
    # else, return false
    for text in texts:
        if text in textToCheck.lower():
            return len(text)
    return False

def getURLs(string):
    return re.findall(urlRegex, string)


def stripUnicode(input_string: str) -> str:
    return ''.join(char for char in input_string if ord(char) < 128)


def hexToRGBA(hexValue, alpha):
    # todo: what the fuck is this doing
    h = tuple(int(hexValue.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))
    return "rgba(" + str(h[0]) + ", " + str(h[1]) + ", " + str(h[2]) + ", " + str(alpha) + ")"


