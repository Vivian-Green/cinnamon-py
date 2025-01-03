import os
import json
import difflib
import time
import subprocess
from cinIO import loadCache
from cinLogging import printLabelWithInfo
from pytube import Playlist

clip_file_names = {}
lastVideoIndex = 0

get_links_memo = {}
trust_links_memo_timestamp = 0

def getDefaultCache():
    return {
        "targets.json_path": os.path.expanduser("~\\Documents\\Yoinkyt\\targets.json"),
        "yoinkyt.py_path": os.path.expanduser("~\\Documents\\Yoinkyt\\yoinkyt.py"),
        "trust_cache_time_seconds": 3600,
        
    }

# Variables
default_cache = getDefaultCache()  # Populate default cache
yoinkyt_config = loadCache("yoinkyt/yoinkys_config.json", default_cache)

targets_json_path = yoinkyt_config["targets.json_path"]
yoinkyt_py_path = yoinkyt_config["yoinkyt.py_path"]
trust_cache_time_seconds = yoinkyt_config["trust_cache_time_seconds"]

def get_links(url): # todo: this is already in yoinkyt's common.py and has just been accidentally reengineered lmao, use whichever is better for both
    global get_links_memo
    global trust_links_memo_timestamp
    global trust_cache_time_seconds
    
    if trust_links_memo_timestamp > time.time() and url in get_links_memo:
        return get_links_memo[url]

    playlist = Playlist(url)
    links = list(playlist.video_urls)
    get_links_memo[url] = links
    trust_links_memo_timestamp = time.time() + trust_cache_time_seconds
    return links

def timestamp_to_sec(timestamp):
    parts = list(map(int, timestamp.split(':')))
    if len(parts) == 3:
        h, m, s = parts
    elif len(parts) == 2:
        h = 0
        m, s = parts
    else:
        raise ValueError("Invalid timestamp format")
    return h * 3600 + m * 60 + s

def load_clip_file(message):
    global clip_file_names
    try:
        with open(clip_file_names[message.channel.name], 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"Error: File '{clip_file_names[message.channel.name]}' not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Failed to parse JSON from '{clip_file_names[message.channel.name]}'. The file might be corrupted or improperly formatted.")
        return None
    except Exception as e:
        print(f"Unexpected error occurred while accessing '{clip_file_names[message.channel.name]}': {str(e)}")
        return None













async def setclipfile(words, message): 
    global clip_file_names
    print(words)

    if len(words) < 2:  # Only filename is required
        await message.channel.send("Usage: !>setclipfile <filename.json> [url]")
        return False

    filename = words[1]

    # Define the cache directory based on guild_id
    guild_id = message.guild.id  # Assuming `guild_id` is available from the message object
    cache_dir = os.path.join(".", "cache", "yoinkyt", str(guild_id))

    # Ensure the cache directory exists
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir, exist_ok=True)

    # Construct the full path for the file
    filepath = os.path.join(cache_dir, filename)

    # Check if the file already exists in the cache directory
    if os.path.exists(filepath):
        await message.channel.send(f"Loading clip configuration from {filepath}.")
    else:
        # Search for a close match within the cache directory
        json_files = [f for f in os.listdir(cache_dir) if f.endswith('.json')]
        closest_match = difflib.get_close_matches(f"targets_{filename}", json_files, n=1, cutoff=0.75)

        if closest_match:
            filename = closest_match[0]
            filepath = os.path.join(cache_dir, filename)
            await message.channel.send(f"Found a close match for the alias: {filename}")
        else:
            # On 404, require URL to build the file
            if len(words) < 3:
                await message.channel.send("Usage: !>setclipfile <filename.json> <url>")
                return False

            url = words[2]
            links = get_links(url)

            data = {url: []}
            data[url].append({"prefix": "ep "})
            for i in range(len(links)):  # Pad to length of playlist
                data[url].append({})

            await message.channel.send(f"New clip configuration created for {url}.")

            # Save the new configuration file in the cache directory
            with open(filepath, 'w') as file:
                json.dump(data, file, indent=4)

    # Update the global clip_file_names dictionary with the channel name and filepath
    clip_file_names[message.channel.name] = filepath

    await message.channel.send(f"Clip configuration saved to {filepath}.")
    return True


clipping_mode = {}
async def clipToggle(words, message):
    global clipping_mode

    channel_id = str(message.channel.id)
    if channel_id in clipping_mode:
        clipping_mode[channel_id] = False
        await message.channel.send("Clipping mode disabled.")
    else:
        clipping_mode[channel_id] = True
        await message.channel.send("Clipping mode enabled.")
    return


async def renderClips(words, message):
    if message.channel.name not in clip_file_names:
        if not await setclipfile(["!>setclipfile", message.channel.name], message):
            return

    # Ensure valid clip configuration
    if message.channel.name not in clip_file_names or not os.path.exists(clip_file_names[message.channel.name]):
        await message.channel.send("No clip configuration found. Use !>setclipfile to initialize.")
        return

    data = load_clip_file(message)
    if data is None:
        await message.channel.send("Json says no?")
        return

    # Write data to the targets JSON file
    try:
        with open(targets_json_path, 'w') as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        await message.channel.send(f"Error writing to targets.json: {e}")
        return

    # Build command
    command = ['python', yoinkyt_py_path]
    arg1 = words[1] if len(words) > 1 else None
    arg2 = words[2] if len(words) > 2 else None
    message_errs = True and arg1

    try:
        # Process arg1
        arg1 = str(int(arg1)) if arg1 else "1"
    except Exception as e:
        printLabelWithInfo("!>renderClips", f"Error on arg 1: {e}. Using default: 1")
        arg1 = "1"
        if message_errs:
            message.channel.send(f"Error on arg 1: {e}. Using default: 1")
    command.append(arg1)

    try:
        # Process arg2
        if arg2:
            arg2 = str(int(arg2) + 1)
        else:
            message_errs = False
            playlist_length = 999
            arg2 = str(playlist_length)  # Default to the playlist length
    except Exception as e:
        playlist_length = 999
        printLabelWithInfo("!>renderClips", f"Error on arg 2: {e}. Using default: {999}")
        arg2 = str(playlist_length)
        if message_errs:
            message.channel.send(f"Error on arg 2: {e}. Using default: {999}")
    command.append(arg2)

    try:
        # Open the new process in a separate window without waiting for it to finish
        script_directory = os.path.dirname(yoinkyt_py_path)
        subprocess.Popen(
            command,
            cwd=script_directory,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        await message.channel.send(f"trying `{' '.join(command)}` o7")
    except Exception as e:
        await message.channel.send(f"Error executing render command: {e}")



    
async def clip(words, message):
    global clipping_mode
    global lastVideoIndex
    global clip_file_names

    if message.channel.name not in clip_file_names:
        if not await setclipfile(["!>setclipfile", message.channel.name], message):
            return

    # prepend clip to words on first word is timestamp if clipping mode enabled
    channel_id = str(message.channel.id)
    if channel_id in clipping_mode:
        if len(words) > 1 and ":" in words[0]:
            # If in clipping mode and first word is a timestamp, add "clip" to the beginning
            words.insert(0, "clip")
    

    if "clip" not in words[0]:
        return

    #       Handle clipping mode toggle
    if len(words) > 1 and "toggle" in words[1]:
        await clipToggle(words, message)
        return

    # fail cases
    if len(words) < 3:
        await message.channel.send("Usage: [clip] [index] <timestamp> <duration>")
        return
        
    if message.channel.name not in clip_file_names or not os.path.exists(clip_file_names[message.channel.name]):
        await message.channel.send("No clip configuration found. Use !>setclipfile to initialize.")
        return

    data = load_clip_file(message)
    if data is None:
        await message.channel.send("Json says no?")
        return

    #       check valid timestamp
    if ":" in words[1]:
        timestamp = words[1]
        index = lastVideoIndex  # Use the last used index
    else:
        try:
            index = int(words[1])
            if index < 1:
                raise ValueError("Index must be greater than 0.")
            timestamp = words[2]
        except ValueError as e:
            await message.channel.send(f"Invalid index: {e}")
            return

    try:
        duration = int(words[-1])
    except ValueError:
        await message.channel.send("Duration must be an integer.")
        return

    # actually clip

    url = list(data.keys())[0]
    links = list(Playlist(url))
    videos = data[url]

    removed = False
    if index > len(links):
        await message.channel.send(f"Index {index} is out of bounds. Maximum index is {len(videos)}.")
        return
    elif index == len(videos) - 1 or index >= len(videos):
        videos.append({timestamp: duration})
    else:
        video_segment = videos[index]
        if isinstance(video_segment, dict):
            video_segment[timestamp] = duration
            if duration == 0:
                video_segment.pop(timestamp)
                removed = True
        else:
            await message.channel.send(f"Unexpected format in the clip file at index {index}.")
            return

    data[url] = videos
    with open(clip_file_names[message.channel.name], 'w') as file:
        json.dump(data, file, indent=4)

    lastVideoIndex = index

    if removed:
        await message.channel.send(f"Clip deleted at index {index} with timestamp {timestamp}")
    else:
        link = get_links(url)[index-1]
        await message.channel.send(f"Clip added/updated at index {index} with timestamp {timestamp} and duration {duration}s.\n{link}&t={timestamp_to_sec(timestamp)}")


async def getClips(words, message):
    global clip_file_names
    if len(words) < 2:
        await message.channel.send("Usage: !>getclips <index>")
        return

    try:
        index = int(words[1])
        if index < 1:
            raise ValueError("Index must be greater than 0.")
    except ValueError as e:
        await message.channel.send(f"Invalid index: {e}")
        return


    if message.channel.name not in clip_file_names or not os.path.exists(clip_file_names[message.channel.name]):
        await message.channel.send("No clip configuration found. Use !>setclipfile to initialize.")
        return

    data = load_clip_file(message)
    if data is None:
        await message.channel.send("Json says no?")
        return

    url = list(data.keys())[0]
    videos = data[url]

    if index > len(videos):
        await message.channel.send(f"Index {index} is out of bounds. Maximum index is {len(videos)}.")
        return

    clips = videos[index]
    if not isinstance(clips, dict):
        await message.channel.send(f"Unexpected format in the clip file at index {index}.")
        return

    link = get_links(url)[index-1]

    # Format the clips for display
    clips_str = "\n".join([f"{link}&t={timestamp_to_sec(timestamp)}  {timestamp}: {duration}s" for timestamp, duration in clips.items()])
    response = f"```Clips for index {index}:```\n{clips_str}"

    await message.channel.send(response)

async def getAllClips(message):
    global clip_file_names

    if message.channel.name not in clip_file_names or not os.path.exists(clip_file_names[message.channel.name]):
        await message.channel.send("No clip configuration found. Use !>setclipfile to initialize.")
        return

    data = load_clip_file(message)
    if data is None:
        await message.channel.send("Json says no?")
        return

    url = list(data.keys())[0]
    videos = data[url]

    links = get_links(url)

    if not videos:
        await message.channel.send("No clips found.")
        return

    lines = 0
    for index, clips in enumerate(videos[1:], start=1):
        if isinstance(clips, dict):
            clip_lines = []
            for timestamp, duration in clips.items():
                seconds = timestamp
                if ":" in timestamp:
                    seconds = timestamp_to_sec(timestamp)
                clip_lines.append(f"{links[index - 1]}&t={seconds} {timestamp}: {duration}s")
                lines += 1

            clips_str = "\n".join(clip_lines)
            response = f"``` Clips for index {index}: ```\n{clips_str}"

            if lines > 0:
                lines = 0
                await message.channel.send(response)
                time.sleep(1)
        else:
            await message.channel.send(f"Unexpected format in the clip file at index {index}.")
