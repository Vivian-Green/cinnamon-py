# prompt response functions that don't really affect much

import time
import discord
from requests import get #used in dox function to get public IP

from cinIO import strings, config
from cinShared import containsAny

adminGuild = config["adminGuild"]

async def rickRoll(message: discord.message):
    for i in range(6):
        await message.channel.send(strings["rickroll"]["texts"][i])


async def lovecalc(message, messageContent):
    words = messageContent.split(" ")
    embedTitle = f"**:heart: Love calculation for {words[2]} and {words[3]}**:"

    # trim <@> from tags before XORing their ID's
    firstUserID = int(words[2][2:-1])
    secondUserID = int(words[3][2:-1])
    embedDesc = f"Percentage: {(firstUserID + secondUserID) % 101}%"

    embed = discord.Embed(
        title=embedTitle,
        description=embedDesc,
        color=0xff7979
    )
    embed.set_footer(text="(don't take this seriously, you can bang anyone (with consent))")

    await message.channel.send(embed=embed)

async def dox(message: discord.message):
    isFromAdminGuild = adminGuild == message.guild.id
    if isFromAdminGuild:
        try:
            ip = get('https://api.ipify.org').content.decode('utf8')
            await message.channel.send(f"My public IP address is: {ip}")
        except Exception:
            print(Exception)
            await message.channel.send(strings['errors']['failedToGetIPErr'])
    else:
        await message.channel.send(strings['errors']['guildIsNotAdminGuildMsg'])

async def ping(message):
    t1 = time.perf_counter()
    await message.channel.typing()
    t2 = time.perf_counter()

    embed = discord.Embed(
        title=None,
        description=f'Ping: {round((t2 - t1) * 1000)}ms',
        color=0x2874A6
    )
    await message.channel.send(embed=embed)


async def sleepPrompts(message, messageContent, Nope):
    # prompts that make cinnamon go away
    # returns the current value of Nope if none of the prompts are in the message
    if "cinnamon, be silenced" in messageContent.lower():
        await message.channel.send("Hai!")
        Nope = 5
    if containsAny(messageContent, strings["sleepTexts"]["goodNight"]):
        await message.channel.send("Jyaa ne!! ***bows***")
        Nope = 50
    if containsAny(messageContent, strings["sleepTexts"]["kys"]):
        await message.channel.send("a'k!")  # Sequential art, scarlet
        Nope = 5000
    return Nope