#Cinnamon bot v1.0.0 for discord, written by Brandon Corbett, last update March 2, 2018 (almost complete re-write to force sfw defaults, and a simplified way to modify a channel's config)

#a fair amount of code is heavily based on sources other than my own brain, also I have no idea what code came from what source at this point
#most of it's mine, and some of it isn't. some of it is also based on someone else's code, and modified a lot
#also, I don't think I credited any images, so, yeah, none of those are mine unless otherwise noted

#and I'm self taught... don't kill me

#default command prefix: !>
#get image: [image]

token = 'token'

import discord
import discord.ext
import time
from random import randint
import random
import sys
import re
import os.path
import os
from discord.voice_client import VoiceClient
from discord.ext import commands
import asyncio
import urllib.request
import urllib.error

description = "Multi-purpose bot that does basicallly anything I could think of"
bot_prefix = "!>"
#commands.when_mentioned_or('!>')
inDev = 0 #don't ser this to 1 unless you are a dev, aka me.
client = commands.Bot(description=description, command_prefix=bot_prefix)
bot = client
tempVar = 0
tempVar2 = 0
Nope = 0
annoy = ""
annoyTime = time.strftime("%H:%M:%S", time.gmtime())
attachments = ""
chatMod = 1 #don't change it here, it will do literally nothing, the value just needs to be defined here. Go to your channel's config file
queue = []
songLength = 0
playing = 0
CTX = 0
all_url = []
playlistURLs = []
fileBackup = []
muted = []
nsfw = 0
nsfwCheck = 0
reconnectTime = 5

def ytCrawl(url):#http://pantuts.com/2013/02/16/youparse-extract-urls-from-youtube/
    global playlistURLs
    sTUBE = ''
    cPL = ''
    amp = 0
    final_url = []
    
    if 'list=' in url:
        eq = url.rfind('=') + 1
        cPL = url[eq:]
            
    else:
        print('Incorrect Playlist.')
        exit(1)
    
    try:
        yTUBE = urllib.request.urlopen(url).read()
        sTUBE = str(yTUBE)
    except urllib.error.URLError as e:
        print(e.reason)
    
    tmp_mat = re.compile(r'watch\?v=\S+?list=' + cPL)
    mat = re.findall(tmp_mat, sTUBE)
 
    if mat:
        playlistURLs = []
        for PL in mat:
            yPL = str(PL)
            if '&' in yPL:
                yPL_amp = yPL.index('&')
            final_url.append('https://www.youtube.com/' + yPL[:yPL_amp])
            if not str('https://www.youtube.com/' + yPL[:yPL_amp]) in playlistURLs:
                playlistURLs.append(str('https://www.youtube.com/' + yPL[:yPL_amp]))
            
        all_url = list(set(final_url))
 
##        i = 0
##        while i < len(all_url):
##            sys.stdout.write(all_url[i] + '\n')
##            time.sleep(0.04)
##            i = i + 1
        
    else:
        print('No videos found.')
        exit(1)
    return all_url
    
class Main:
    def getURLs(self, string):
        return re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', string)

    def hexToRGBA(self, hexValue, alpha):
        h = tuple(int(hexValue.lstrip('#')[i:i+2], 16) for i in (0, 2 ,4))
        return ("rgba("+str(h[0])+", "+str(h[1])+", "+str(h[2])+", "+str(alpha)+")")

    async def createConfig(self, tempVar, message):
        global chatMod
        global nsfw
        
        if not message.author.display_name.lower() == "cinnamon":
            try:
                os.makedirs(os.path.join(os.path.dirname(__file__), str("configs\\"+str(message.server))))
                with open(str(os.path.join(os.path.dirname(__file__), str("configs\\"+str(message.server)+"\\"))+str(message.channel)+'.config'), 'a') as file:
                    file.write("chatMod = 1")
                    file.write("nsfw = 0")
                await client.send_message(message.channel, "Config file created for this channel! type !>settings (if you are a chatmod/admin/owner) to edit, or !>superhelp for detailed info!")

            except:
                with open(str(os.path.join(os.path.dirname(__file__), str("configs\\"+str(message.server)+"\\"))+str(message.channel)+'.config'), 'w') as file:
                    file.write("")

                with open(str(os.path.join(os.path.dirname(__file__), str("configs\\"+str(message.server)+"\\"))+str(message.channel)+'.config'), 'a') as file:
                    if chatMod == 1:
                        file.write("chatMod = 1\n")
                    else:
                        file.write("chatMod = 0\n")
                    if nsfw == 1:
                        file.write("nsfw = 1")
                    else:
                        file.write("nsfw = 0")
                await client.send_message(message.channel, "Config file created for this channel! type !>settings (if you are a chatmod/admin/owner) to edit, or !>superhelp for detailed info!\n\n(and if this is the discord bot list server, hi! I attempted to make this bot fit the rules, but I may have messed up a bit because this is my first discord bot (that I've been writing for months...), please inform me if this is the case, as it's certainly not intentional behavior)")

    async def roll(self, num, tempVar, message):#You want comments on this thing? DO IT YOURSELF!  (rolls D&D die based on input, "num" being the die (4, 6, 8, 10, 12, 20, 100), tempVar being the string (when it gets to this function, "<adv/dis> <+/- modifier>"), and message is the original, inputted message
        tempVar = tempVar[len(str(num))+1:len(tempVar)]

        if num == 10:
            startnum = 0
        else:
            startnum = 1
            
        if (len(tempVar) > 1):
            tempVar2 = 0

            
            if (tempVar.lower()[tempVar2] == "-"):
                for i in range(len(tempVar)-1):
                    if (tempVar.lower()[tempVar2+1] != " "):
                        tempVar2 += 1
                        print(tempVar[1:tempVar2])
                await client.send_message(message.channel, "D"+str(num)+": "+str(randint(startnum,startnum+num-1)-int(tempVar[1:tempVar2+1])))
                tempVar = tempVar[tempVar2:len(tempVar)]
                print(tempVar)

                
            elif (tempVar.lower()[tempVar2] == "+"):
                for i in range(len(tempVar)-1):
                    if (tempVar.lower()[tempVar2+1] != " "):
                        tempVar2 += 1
                        print(tempVar[1:tempVar2])
                await client.send_message(message.channel, "D"+str(num)+": "+str(randint(startnum,startnum+num-1)+int(tempVar[1:tempVar2+1])))
                tempVar = tempVar[tempVar2:len(tempVar)]
                print(tempVar)
                
                
            elif (tempVar.lower().startswith("dis")):
                tempVar = tempVar[4:len(tempVar)]

                if(len(tempVar) < 1):
                    tempVar2 = randint(startnum,startnum+num-1)
                    tempVar3 = randint(startnum,startnum+num-1)
                    await client.send_message(message.channel, "D"+str(num)+": "+str(tempVar2))
                    await client.send_message(message.channel, "D"+str(num)+": "+str(tempVar3)+"\n")
                    if (tempVar2 > tempVar3):
                        await client.send_message(message.channel, "Result: "+str(tempVar3))
                    else:
                        await client.send_message(message.channel, "Result: "+str(tempVar2))

                else:
                    tempVar2 = 1
                    if (tempVar.lower()[0] == "-"):
                        for i in range(len(tempVar)-1):
                            if (tempVar.lower()[tempVar2] != " "):
                                tempVar2 += 1
                        tempVar4 = randint(int(tempVar[1:tempVar2])+startnum, num+int(tempVar[1:len(tempVar)])+startnum-1)
                        tempVar3 = randint(int(tempVar[1:tempVar2])+startnum, num+int(tempVar[1:len(tempVar)])+startnum-1)
                        await client.send_message(message.channel, "D"+str(num)+": "+str(tempVar4))
                        await client.send_message(message.channel, "D"+str(num)+": "+str(tempVar3)+"\n")
                        if (tempVar4 > tempVar3):
                            await client.send_message(message.channel, "Result: "+str(tempVar3))
                        else:
                            await client.send_message(message.channel, "Result: "+str(tempVar4))
                    elif (tempVar.lower()[0] == "+"):
                        for i in range(len(tempVar)-1):
                            if (tempVar.lower()[tempVar2] != " "):
                                tempVar2 += 1
                        tempVar4 = randint(int(tempVar[1:tempVar2])+startnum, num+int(tempVar[1:len(tempVar)])+startnum-1)
                        tempVar3 = randint(int(tempVar[1:tempVar2])+startnum, num+int(tempVar[1:len(tempVar)])+startnum-1)
                        await client.send_message(message.channel, "D"+str(num)+": "+str(tempVar4))
                        await client.send_message(message.channel, "D"+str(num)+": "+str(tempVar3)+"\n")
                        if (tempVar4 > tempVar3):
                            await client.send_message(message.channel, "Result: "+str(tempVar3))
                        else:
                            await client.send_message(message.channel, "Result: "+str(tempVar4))

                            
            elif (tempVar.lower().startswith("adv")):
                tempVar = tempVar[4:len(tempVar)]

                if(len(tempVar) < 1):
                    tempVar2 = randint(startnum,startnum+num-1)
                    tempVar3 = randint(startnum,startnum+num-1)
                    await client.send_message(message.channel, "D"+str(num)+": "+str(tempVar2))
                    await client.send_message(message.channel, "D"+str(num)+": "+str(tempVar3)+"\n")
                    if (tempVar2 > tempVar3):
                        await client.send_message(message.channel, "Result: "+str(tempVar2))
                    else:
                        await client.send_message(message.channel, "Result: "+str(tempVar3))

                else:
                    tempVar2 = 1
                    if (tempVar.lower()[0] == "-"):
                        for i in range(len(tempVar)-1):
                            if (tempVar.lower()[tempVar2] != " "):
                                tempVar2 += 1
                        tempVar4 = randint(int(tempVar[1:tempVar2])+startnum, num+int(tempVar[1:len(tempVar)])+startnum-1)
                        tempVar3 = randint(int(tempVar[1:tempVar2])+startnum, num+int(tempVar[1:len(tempVar)])+startnum-1)
                        await client.send_message(message.channel, "D"+str(num)+": "+str(tempVar4))
                        await client.send_message(message.channel, "D"+str(num)+": "+str(tempVar3)+"\n")
                        if (tempVar4 < tempVar3):
                            await client.send_message(message.channel, "Result: "+str(tempVar3))
                        else:
                            await client.send_message(message.channel, "Result: "+str(tempVar4))
                    elif (tempVar.lower()[0] == "+"):
                        for i in range(len(tempVar)-1):
                            if (tempVar.lower()[tempVar2] != " "):
                                tempVar2 += 1
                        tempVar4 = randint(int(tempVar[startnum:tempVar2])+startnum, num+int(tempVar[1:len(tempVar)])+startnum-1)
                        tempVar3 = randint(int(tempVar[startnum:tempVar2])+startnum, num+int(tempVar[1:len(tempVar)])+startnum-1)
                        await client.send_message(message.channel, "D"+str(num)+": "+str(tempVar4))
                        await client.send_message(message.channel, "D"+str(num)+": "+str(tempVar3)+"\n")
                        if (tempVar4 < tempVar3):
                            await client.send_message(message.channel, "Result: "+str(tempVar3))
                        else:
                            await client.send_message(message.channel, "Result: "+str(tempVar4))

                            
        else:
            await client.send_message(message.channel, "D"+str(num)+": "+str(randint(startnum,num+startnum-1)))

    async def appendToLog(self, message, tempVar):
        with open(str(os.path.join(os.path.dirname(__file__), str("logs\\"+str(message.server)+"\\"))+str(message.channel)+'.html'), 'a') as file:#open correct log file
            if message.author.bot:#If cinnamon (or another bot))
                print(">>>CINNAMON"+": "+tempVar+"\n"+r"\n")#custom display type for cinnamon
                try:#attempt to log raw message
                    file.write('<p style="padding-left: 20px; margin-left: 5px; padding-top: 8px; padding-bottom: 8px; background-color: '+hexToRGBA(str(message.author.color), 0.5)+'">'+" \n\n    "+str(time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()))+"<br /><br /> CINNAMON (bot): "+str(tempVar)+"\n"+r"</p>")#Log time, username, and reply to the open file, and format with css3, but that's unimportant
                except:#If there is any unicode
                    file.write('<p style="padding-left: 20px; margin-left: 5px; padding-top: 8px; padding-bottom: 8px; background-color: #d9b6d9;">'+" \n\n    "+str(time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()))+"<br /><br /> CINNAMON (bot): "+"MESSAGE CONTAINS UNICODE CHARACTERS THAT I DON'T WANT TO FIX AT THIS TIME")#Display error in log if there are any unicode characters
            else:#If human
                try:#attempt to log raw message
                    file.write('<p style="padding-left: 20px; margin-left: 20px; padding-top: 8px; padding-bottom: 8px; background-color: '+hexToRGBA(str(message.author.color), 0.5)+'">'+" \n\n    "+str(time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()))+"<br /><br />"+message.author.display_name+": "+str(tempVar)+"\n"+r"</p>")#Log time, username, and reply to the open file, and format with css3, but that's unimportant
                except:#If there is any unicode
                    file.write('<p style="padding-left: 20px; margin-left: 20px; padding-top: 8px; padding-bottom: 8px; background-color: rgba(200, 200, 200, 0.5);">'+" \n\n    "+str(time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()))+"<br /><br />"+message.author.display_name+": "+"MESSAGE CONTAINS UNICODE CHARACTERS THAT I DON'T WANT TO FIX AT THIS TIME")#Display error in log if there are any unicode characters
                print("  "+message.author.display_name+": "+tempVar+"\n")#Log message to SHELL
            for i in range(len(self.getURLs(tempVar))):#For every URL in raw text
                file.write(r'<a href="'+(self.getURLs(tempVar)[i])+r'" style="background-color: rgba(150, 200, 255, 0.2);">'+getURLs(tempVar)[i]+'</a>')#log clickable URL to file
            embeds = str(message.embeds)#get message.embeds, as it's finnickey for some reason
            attachments = str(message.attachments)#see above comment, but for message.attatchments
            for i in range(len(self.getURLs(attachments))):#for every attatched file
                print(self.getURLs(attachments)[i][0:-2])#print file URL to shell
                if ".jpg" in self.getURLs(attachments)[i][0:-2] or ".png" in self.getURLs(attachments)[i][0:-2] or ".gif" in self.getURLs(attachments)[i][0:-2]:#if attatched file is an image
                    if "media.discordapp" in self.getURLs(attachments)[i][0:-2]:#If the image is from the discord media server
                        file.write('<p>Attatchment:: <p><img src="'+self.getURLs(attachments)[i][0:-2]+'" alr="'+self.getURLs(attachments)[i][0:-2]+'">')#embed image into log
                else:#if not an image
                    file.write(r'<a href="'+(self.getURLs(attachments)[i])+r'" style="background-color: rgba(150, 200, 255, 0.2);">'+self.getURLs(attachments)[i]+'</a>')#embed clickable link into log
            for i in range(len(self.getURLs(embeds))):#for every embedded file
                print(self.getURLs(embeds)[i][0:-2])#print file URL to shell
                if ".jpg" in self.getURLs(embeds)[i][0:-2] or ".png" in self.getURLs(embeds)[i][0:-2] or ".gif" in self.getURLs(embeds)[i][0:-2]:#if embedded file is an image
                    if "discordapp" in self.getURLs(embeds)[i][0:-2]:#if file is from a discord server
                        file.write('<p>Discord embed: <p><img src="'+self.getURLs(embeds)[i][0:-2]+'" alr="'+self.getURLs(embeds)[i][0:-2]+'">')#embed image into log
                else:#if embedded file is not an image
                    file.write(r'<a href="'+(self.getURLs(embeds)[i])+r'" style="background-color: rgba(150, 200, 255, 0.2);">'+self.getURLs(embeds)[i]+'</a>')#log raw link to file
            file.close()#close the file 

    @client.event
    async def on_ready(self):
        global annoy
        global annoyTime
        global reconnectTime
        print("\n\n\n\n\n")
        print("Login Successful!")
        print("Name:", client.user.name)
        print("ID:", client.user.id)
        print("Version:", discord.__version__)
        await client.change_presence(game=discord.Game(Name="Call me Cinnamon!"))
        print("\n\n\n\n\n")
        reconnectTime = 5

    @client.event
    async def on_server_join(self, server):
        await client.send_message(server, "Hiya! you seem to have added me to your server! Thanks for that! ~<3")
        await client.send_message(server, "try typing !>superhelp for an in depth list of all the things I can do!")
                
    @client.event
    async def on_error(self, event):
        print(event)

        
    @client.event
    async def on_message(self, message):

#~~~~~~~~ define some global stuffs
        
        global prevMessage#previous message get!
        global Nope#"Sleep" bool get!
        global annoy#This is dated, but breaks the program if deleted, so, "annoy" get!
        global annoyTime#see above!
        global moderator#"Moderator" bool get!
        global attachments#I don't know why I made this global, but it doesn't really matter because this is the only function that uses it! ("attatchments" get!)
        global chatMod
        global inDev
        global muted
        global nsfwCheck
        global nsfw
        prevMessage = message#archive this message if I ever have any function that requires the use of 2 messages back
        tempVar = message.content#I don't want to type message.content 5000 times
        #TEMPORARY! VERY TEMPORARY!
        if tempVar.lower() == "cinnamon, drop the nuke":
            await client.send_message(message.channel, "LAUNCHING...")
            time.sleep(10)
            await client.send_message(message.channel, "5 SECONDS TO IMPACT")
            time.sleep(1)
            await client.send_message(message.channel, "4 SECONDS TO IMPACT")
            time.sleep(1)
            await client.send_message(message.channel, "3 SECONDS TO IMPACT")
            time.sleep(1)
            await client.send_message(message.channel, "2 SECONDS TO IMPACT")
            time.sleep(1)
            await client.send_message(message.channel, "1 SECONDS TO IMPACT")
            time.sleep(1)
            await client.send_message(message.channel, "NUKE DROPPED")
            time.sleep(2)
            with open(str(os.path.join(os.path.dirname(__file__), str("logs\\"+"killerPenguino0"+"\\"))+"main"+'.html'), "r") as file:
                tempVar2 = file.readlines()
                tempVar3 = 0
                for i in range(len(tempVar2)):
                    if tempVar2[tempVar3].startswith("</p><p style=") or len(tempVar2[tempVar3]) < 5:
                        del tempVar2[tempVar3]
                    else:
                        if tempVar2[tempVar3].startswith("</p>"):
                            tempVar2[tempVar3] = (tempVar2[tempVar3][4: len(tempVar2[tempVar3])-4])
                            if tempVar2[tempVar3].startswith("<a href"):
                                while not tempVar2[tempVar3].startswith(">"):
                                    tempVar2[tempVar3] = tempVar2[tempVar3][1: len(tempVar2[tempVar3])]
                                tempVar2[tempVar3] = tempVar2[tempVar3][1: len(tempVar2[tempVar3])]
                                tempVar4 = 0
                                while not tempVar2[tempVar3][tempVar4] == "<":
                                    tempVar4 += 1
                                await client.send_message(message.channel, "OLD LOG: "+tempVar2[tempVar3][0:tempVar4])
                        else:
                            await client.send_message(message.channel, "OLD LOG: "+tempVar2[tempVar3][47: len(tempVar2[tempVar3])])
                        tempVar3 += 1


#~~~~~~~ get config file
        
        try:
            with open(str(os.path.join(os.path.dirname(__file__), str("configs\\"+str(message.server)+"\\"))+str(message.channel)+'.config'), 'r') as file:
                tempVar2 = (file.readlines())
                if len(tempVar2) > 0:
                    print(tempVar2)
                    for i in range(len(tempVar2)):
                        exec(tempVar2[i], globals())
                        print(chatMod)
                else:
                    await self.createConfig(tempVar, message)
        except:
            await self.createConfig(tempVar, message)


#~~~~~~~~ check if the user is muted, if do, delete the message immediately
            
        if message.author.display_name.lower() in muted:
            await client.delete_message(message)


#~~~~~~~~ if not command (commands aren't really used anymore, but they are still supported)

        if not tempVar.startswith("!>"):
            print("    "+str(time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())))#print current time
            #os.path.join(os.path.dirname(__file__), str("logs\\"+str(message.server)+"\\"))#testing path
            try:
                await self.appendToLog(message, tempVar)
            except:
                if not os.path.exists(os.path.join(os.path.dirname(__file__), str("logs\\"+str(message.server)))):
                    os.makedirs(os.path.join(os.path.dirname(__file__), str("logs\\"+str(message.server))))
                open(str(os.path.join(os.path.dirname(__file__), str("logs\\"+str(message.server)+"\\"))+str(message.channel)+'.html'), "w+").close()
                #with open(str(os.path.join(os.path.dirname(__file__), str("logs\\"+str(message.server)+"\\"))+str(message.channel)+'.html'), 'w+') as file:
                    #file.close()
                await self.appendToLog(message, tempVar)
            if chatMod == 1:#If the moderator function is active
                if tempVar.lower().startswith("ass"):#also, I know I could have done this way easier, and able to be changed per-server by checking within a list, but...
                    await client.delete_message(message)#Delete the offensive message
                    await client.send_message(message.channel, "Lol butts")#Explain why the message was deleted, in global
                    return
                if tempVar.lower().startswith("arse"):
                    await client.delete_message(message)#See 2 up
                    await client.send_message(message.channel, "Lol butts")#See 2 up
                    return
                if tempVar.lower().startswith("bitch"):
                    await client.delete_message(message)#See 2 up
                    await client.send_message(message.channel, "Hehe... dogs are so adorable <3")#See 2 up
                    return
                if tempVar.lower().startswith("cunt"):
                    await client.delete_message(message)#See 2 up
                    await client.send_message(message.channel, "I have one of those!")#See 2 up
                    return
                if tempVar.lower().startswith("cock"):
                    await client.delete_message(message)
                    await client.send_message(message.channel, "*Cuckoo")
                    return
                if tempVar.lower().startswith("dick"):
                    await client.delete_message(message)
                    await client.send_message(message.channel, "Bad word!")
                    return
                if tempVar.lower().startswith("fuck you"):
                    await client.delete_message(message)
                    await client.send_message(message.channel, "Please do")
                    return
                elif tempVar.lower().startswith("fuck me"):
                    await client.delete_message(message)
                    await client.send_message(message.channel, "ok")
                    return
                elif tempVar.lower().startswith("fuck"):
                    await client.delete_message(message)
                    await client.send_message(message.channel, "Bad!")
                elif tempVar.lower().startswith("fuk"):
                    await client.delete_message(message)
                    await client.send_message(message.channel, "Bad!")
                    return
                if tempVar.lower().startswith("nigger"):
                    await client.delete_message(message)
                    await client.send_message(message.channel, "I know you are, but what am I?")
                    return
                if tempVar.lower().startswith("pussy"):
                    await client.delete_message(message)
                    await client.send_message(message.channel, "I have one of those!")
                    return
                if tempVar.lower().startswith("piss"):
                    await client.delete_message(message)
                    await client.send_message(message.channel, "No! Bad person!")
                    return
                if tempVar.lower().startswith("whore"):
                    await client.delete_message(message)
                    await client.send_message(message.channel, "*respectable woman")
                    return
                if tempVar.lower().startswith("slut"):
                    await client.delete_message(message)
                    await client.send_message(message.channel, "*respectable woman")
                    return
                if tempVar.lower().startswith("bastard"):
                    await client.delete_message(message)
                    await client.send_message(message.channel, "Hahaha you said the bad language word")
                    return
            if not (Nope > 0 or message.author.bot):#if cinnamon is in "awake" mode
                for i in range(len(tempVar)):#for every characyer in the message

#~~~~~~~~~~~~~~~~~~~~~~~~~~~muting
                    
                    if tempVar.lower().startswith("cinnamon mute "):
                        if message.author.permissions_in(message.channel).manage_messages:
                            muted.append(tempVar[14:len(tempVar)])
                            await client.send_message(message.channel, tempVar[14:len(tempVar)]+" muted! The mute will last until you unmute them, or I am disabled. You will have to manually reinstate the mute if I am restarted")
                        else:
                            await client.send_message(message.channel, "You must be of chatmod rank (able to delete messages) to toggle a mute! Don't worry, they're temporary")
                        break
                    if tempVar.lower().startswith("cinnamon, mute "):
                        if message.author.permissions_in(message.channel).manage_messages:
                            muted.append(tempVar[15:len(tempVar)])
                            await client.send_message(message.channel, tempVar[15:len(tempVar)]+" muted! The mute will last until you unmute them, or I am disabled. You will have to manually reinstate the mute if I am restarted")
                        else:
                            await client.send_message(message.channel, "You must be of chatmod rank (able to delete messages) to toggle a mute! Don't worry, they're temporary")
                        break
                    if tempVar.lower().startswith("cinnamon unmute "):
                        if message.author.permissions_in(message.channel).manage_messages:
                            muted.remove(tempVar[16:len(tempVar)])
                            await client.send_message(message.channel, "unmuted "+tempVar[16:len(tempVar)])
                        else:
                            await client.send_message(message.channel, "You must be of chatmod rank (able to delete messages) to toggle a mute! Don't worry, they're temporary")
                        break
                    if tempVar.lower().startswith("cinnamon unmute "):
                        if message.author.permissions_in(message.channel).manage_messages:
                            muted.remove(tempVar[17:len(tempVar)])
                            await client.send_message(message.channel, "unmuted "+tempVar[17:len(tempVar)])
                        else:
                            await client.send_message(message.channel, "You must be of chatmod rank (able to delete messages) to toggle a mute! Don't worry, they're temporary")
                        break

#~~~~~~~~~~~~~~~~~~~~~~~~~~~back and fourth
                    
                    if tempVar.lower() == ("arise, cinnamon"):#
                        if nsfw == 1:
                            await client.send_message(message.channel, "Ufufu... To be woken up by a guy after having no idea what happened before you fell asleep... how mysterious <3")
                        else:
                            await client.send_message(message.channel, "Ohayogozaimasu!!!")
                    if tempVar.lower() == ("cinnamon, you are dismissed"):
                        await client.send_message(message.channel, "***bows***")
                    if (tempVar.lower().startswith("hype")) and (message.author.display_name.lower() != "cinnamon"):
                        await client.send_message(message.channel, "HYPE!!!!!!!!!")
                        break
                    if tempVar.lower().startswith("can't you, cinnamon"):
                        await client.send_message(message.channel, "I can")
                    if tempVar.lower().startswith("hello, cinnamon"):
                        await client.send_message(message.channel, "Ohayo, "+message.author.display_name+"! =D")
                    if tempVar.lower().startswith("right, cinnamon"):
                        await client.send_message(message.channel, "Correct")
                    if tempVar.lower().startswith("slaps cinnamon "):
                        await client.send_message(message.channel, ";-;")
                    if tempVar.lower().startswith("spanks cinnamon "):
                        if nsfw == 1:
                            await client.send_message(message.channel, "Ufufu~ <3")
                    if tempVar.lower().startswith("slaps cinnamon*"):
                        await client.send_message(message.channel, ";-;")
                    if tempVar.lower().startswith("spanks cinnamon*"):
                        if nsfw == 1:
                            await client.send_message(message.channel, "Ufufu~ <3")
                    if tempVar.lower().startswith("cinnamon, summon"):
                        await client.send_message(message.channel, "***summons***")
                    if tempVar.lower().startswith("*applauds*"):
                        await client.send_message(message.channel, "***also applauds***")
                    if tempVar.lower().startswith("good cinnamon"):
                        await client.send_message(message.channel, ("Arigatogozaimasu, "+message.author.display_name+"-sama! ***blushes***   >.<"))
                    if tempVar.lower().startswith("good job, cinnamon"):
                        await client.send_message(message.channel, ("Arigatogozaimasu!"))
                    if tempVar.lower().startswith("good job cinnamon"):
                        await client.send_message(message.channel, ("Arigatogozaimasu!"))
                    if tempVar.lower().startswith("cinnamon, be silenced"):
                        await client.send_message(message.channel, "Hai!")
                        Nope = 5
                    if tempVar.lower() ==("thank you, cinnamon"):
                        await client.send_message(message.channel, "***purrs***")
                    if tempVar.lower() ==("thank you cinnamon"):
                        await client.send_message(message.channel, "***purrs***")
                    if tempVar.lower().startswith("cinnamon!"):
                        await client.send_message(message.channel, "I heard my name, have I been called? ***Nya~***")
                    if tempVar.lower().startswith("shinnamon"):
                        await client.send_message(message.channel, "Watashi wa kiku ashita no namae. Watashi wa yoba rete imasuka? ***Nya~***")
                    if tempVar.lower().startswith("*pets cinnamon*") or tempVar.lower().startswith("*pets cinnamon"):
                        await client.send_message(message.channel, "***Nyaaaaa~***")
                    if tempVar.lower().startswith("*head pats cinnamon"):
                        await client.send_message(message.channel, "***purr~***")
                    if tempVar.lower().startswith("*strokes*") or tempVar.lower().startswith("*strokes cinnamon*"):
                        if nsfw == 1:
                            await client.send_message(message.channel, "*Ufufu* ***~<3***")
                        else:
                            await client.send_message(message.channel, "nyaaa***~<3***")
                    if tempVar.lower().startswith("cinnamon, slap"):
                        await client.send_message(message.channel, "***slaps***")
                    if tempVar.lower().startswith("cinnamon slap"):
                        await client.send_message(message.channel, "***slaps***")
                    if tempVar.lower().startswith("good night, cinnamon"):
                        await client.send_message(message.channel, "Jyaa ne!! ***bows***")
                        Nope = 50
                    if tempVar.lower().startswith("good night cinnamon"):
                        await client.send_message(message.channel, "Jyaa ne!! ***bows***")
                        Nope = 50
                    if tempVar.lower() == ("good morning, cinnamon"):
                        await client.send_message(message.channel, "***Cat yawn noise***")
                        await client.send_message(message.channel, "Ohayo, "+message.author.display_name+"-san")
                    if tempVar.lower() == ("good morning cinnamon"):
                        await client.send_message(message.channel, "***Cat yawn noise***")
                        await client.send_message(message.channel, "Ohayo, "+message.author.display_name+"-san")
                    if (tempVar.lower().startswith("xd")) and (message.author.display_name.lower() != "cinnamon"):
                        await client.send_message(message.channel, "xD")
                    if (tempVar.lower().startswith("nya")) and (message.author.display_name.lower() != "cinnamon"):#Nyaa!
                        tempVar2 = randint(1,10)
                        if tempVar2 == 1:
                            await client.send_message(message.channel, "Nyaaa~")
                        elif tempVar2 == 2:
                            await client.send_message(message.channel, "Nya")
                        elif tempVar2 == 3:
                            await client.send_message(message.channel, "Nyan")
                        elif tempVar2 == 4:
                            await client.send_message(message.channel, "Nya nyan?")
                        elif tempVar2 == 5:
                            await client.send_message(message.channel, "Nyaaaan~")
                        elif tempVar2 == 6:
                            await client.send_message(message.channel, "Nyan na")
                        elif tempVar2 == 7:
                            await client.send_message(message.channel, "Nya?")
                        elif tempVar2 == 8:
                            await client.send_message(message.channel, "Nyaaa?")
                        elif tempVar2 == 9:
                            await client.send_message(message.channel, "Nyan nya")
                        elif tempVar2 == 10:
                            await client.send_message(message.channel, "Nyan nyaaan?")
                    if tempVar.lower().startswith("sinnamon"):#Bittersweer candy bowl
                        await client.send_message(message.channel, ("Paulo, ruler of all cat *playas* is not here"))
                    if tempVar.lower().startswith("glomps cinnamon"):
                        if nsfw == 1:
                            await client.send_message(message.channel, ("***I fly back from the impact into the wall, my shocked face turning red as your-***"))
                            await client.send_message(message.channel, ("Sorry, wrong chat! XD"))
                        else:
                            await client.send_message(message.channel, ("***Gets glomped***"))
                    if tempVar.lower().startswith("kawaii"):
                        await client.send_message(message.channel, ("***projectile vomits sparkles***"))
                    if tempVar.lower().startswith("kemonomimi"):
                        if nsfw == 1:
                            await client.send_message(message.channel, ("Somebody talking about japanese not-quite-furry trash?"))
                    if tempVar.lower().startswith("nekomimi"):
                        if nsfw == 1:
                            await client.send_message(message.channel, ("Somebody talking about me?"))
                    if tempVar.lower().startswith("eroge") and message.author.display_name.lower() != "cinnamon":
                        if nsfw == 1:
                            await client.send_message(message.channel, ("I heard eroge; I'm all cat ears"))#see below red text
                    if tempVar.lower().startswith("hentei") or tempVar.lower().startswith("chinese cartoon") or tempVar.lower().startswith("futanari"):
                        if nsfw == 1:
                            await client.send_message(message.channel, ("it's called hentai, and it's art"))#haha funny joke
                    if tempVar.lower().startswith("cashew"):
                        await client.send_message(message.channel, ("*Kashou"))
                        break
                    if nsfw == 1:
                        if tempVar.lower().startswith("fuck you, cinnamon"):
                            await client.send_message(message.channel, ("Your wish is my command, "+message.author.display_name+"-sama"))
                        if tempVar.lower().startswith("fuck you cinnamon"):
                            await client.send_message(message.channel, ("Your wish is my command, "+message.author.display_name+"-sama"))
                        if tempVar.lower().startswith("fuck me cinnamon"):
                            await client.send_message(message.channel, ("私は自分の猫を食べながら私のお尻で犯されている〜"))#I don't know much vulgar japanese; yes, I did use google translate for this, also, it's "I'm gettign fucked in the ass while eating my own pussy" as quoted by Daniel (the sexbang) (non-baby penis) (the sexbang) Avidan
                        if tempVar.lower().startswith("fuck me, cinnamon"):
                            await client.send_message(message.channel, ("私は自分の猫を食べながら私のお尻で犯されている〜"))
                    if tempVar.lower().startswith("winks at cinnamon"):
                        await client.send_message(message.channel, (";)"))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~semi-complex
                            
                    if tempVar.lower().startswith("cinnamon, become the "):#Homestuck reference
                        await client.send_message(message.channel, ("***"+tempVar[21:len(tempVar)]+" noises***"))
                    if tempVar.lower().startswith("cinnamon, become a "):
                        await client.send_message(message.channel, ("***"+tempVar[19:len(tempVar)]+" noises***"))
                    if tempVar.lower().startswith("cinnamon, become an "):
                        await client.send_message(message.channel, ("***"+tempVar[20:len(tempVar)]+" noises***"))
                    if (tempVar.lower().startswith("cinnamon, become ")) and not (tempVar.lower().startswith("cinnamon, become a ")) and not (tempVar.lower().startswith("cinnamon, become an ")) and not (tempVar.lower().startswith("cinnamon, become the")):
                        await client.send_message(message.channel, ("***"+tempVar[17:len(tempVar)]+" noises***"))
                    if tempVar.lower().startswith("hugs cinnamon"):#back to the futu- back-and-fourth
                        await client.send_message(message.channel, ("***hugs "+message.author.display_name+" back***"))
                    if tempVar.lower().startswith("cinnamon, hug "):#El gonish shive, tedd to grace about girl eliot
                        await client.send_message(message.channel, ("***hugs "+tempVar[14:len(tempVar)]+"***"))
                    if tempVar.lower().startswith("cinnamon hug "):#El gonish shive, tedd to grace about girl eliot
                        await client.send_message(message.channel, ("***hugs "+tempVar[13:len(tempVar)]+"***"))
                    if tempVar.lower().startswith("cinnamon, attack "):
                        await client.send_message(message.channel, ("***nibbles at "+tempVar[17:len(tempVar)]+"'s ankles***"))
                    if tempVar.lower().startswith("cinnamon attack "):
                        await client.send_message(message.channel, ("***nibbles at "+tempVar[16:len(tempVar)]+"***"))
                    if tempVar.lower().startswith("*throws "):
                        await client.send_message(message.channel, ("***catches "+tempVar[7:len(tempVar)]+"**"))
                    if tempVar.lower().startswith("*drops "):
                        await client.send_message(message.channel, ("***catches "+tempVar[6:len(tempVar)]+"**"))
                    if tempVar.lower().startswith("cinnamon, kys"):#Friendly stuff
                        await client.send_message(message.channel, ("a'k!"))#Sequential art, scarlet
                        Nope = 1000
                    if tempVar.lower().startswith("cinnamon kys"):#varient spelling
                        await client.send_message(message.channel, ("a'k!"))
                        Nope = 1000
                    if tempVar.lower().startswith("kys cinnamon"):#varient spelling
                        await client.send_message(message.channel, ("a'k!"))
                        Nope = 1000
                    if tempVar.lower().startswith("cinnamon, say"):#Cause of several role play sessions...
                        await client.delete_message(message)
                        await client.send_message(message.channel, (tempVar[14:len(tempVar)]))
                    if tempVar.lower().startswith("cinnamon say"):#Cause of several role play sessions...
                        await client.delete_message(message)
                        await client.send_message(message.channel, (tempVar[13:len(tempVar)]))
                    if tempVar.lower().startswith("cinnamon, distraction"):
                        if nsfw == 1:
                            await client.send_message(message.channel, ["https://hentaihaven.org", "https://pornhub.com", "https://e621.net/", "https://www.redtube.com/", "https://rule34.xxx", "https://www.xvideos.com/", "https://rule34.paheal.net", "http://leekspin.com/", "http://www.staggeringbeauty.com/", "http://www.theuselessweb.com/", "http://ehentai.org/"][randint(0, 10)])
                        else:
                            await client.send_message(message.channel, "I am being distracting! pay no attention to whatever "+message.author.display_name+" is doing!")
                    if tempVar.lower().startswith("cinnamon, conversation starter"):
                        with open(os.path.join(os.path.dirname(__file__), str("assets\\conversation starters.txt")), "r") as file:
                            tempVar2 = file.readlines()
                            await client.send_message(message.channel, (tempVar2[randint(0, len(tempVar2)-1)]))
                    if tempVar.lower().startswith("cinnamon, cat"):
                        await client.send_message(message.channel, "I can't find a good image scraper for 100's of cat pictures ;-;")
                        #os.listdir(os.path.join(os.path.dirname(__file__), str("assets\\cats")))
                        #await client.send_file(message.channel, os.path.join(os.path.dirname(__file__), str("assets\\cats\\"))+os.listdir(os.path.join(os.path.dirname(__file__), str("assets\\cats")))[randint(0, len(os.listdir(os.path.join(os.path.dirname(__file__), str("assets\\cats")))))]);
                    if tempVar.lower().startswith("cinnamon, rick roll"):#Never gonna give you up!
                        await client.send_message(message.channel, ("""We're no strangers to love \nYou know the rules and so do I \nA full commitment's what I'm thinking of \nYou wouldn't get this from any other guy"""))
                        await client.send_message(message.channel, ("""I just want to tell you how I'm feeling \nGotta make you understand"""))
                        await client.send_message(message.channel, ("""Never gonna give you up, never gonna let you down \nNever gonna run around and desert you \nNever gonna make you cry, never gonna say goodbye \nNever gonna tell a lie and hurt you"""))
                        await client.send_message(message.channel, ("""We've known each other for so long \nYour heart's been aching but you're too shy to say it \nInside we both know what's been going on \nWe know the game and we're gonna play it"""))
                        await client.send_message(message.channel, ("""And if you ask me how I'm feeling \nDon't tell me you're too blind to see"""))
                        await client.send_message(message.channel, ("""Never gonna give you up, never gonna let you down \nNever gonna run around and desert you \nNever gonna make you cry, never gonna say goodbye \nNever gonna tell a lie and hurt you"""))
                        await client.send_message(message.channel, ("""Never gonna give you up, never gonna let you down \nNever gonna run around and desert you \nNever gonna make you cry, never gonna say goodbye \nNever gonna tell a lie and hurt you"""))
                        await client.send_message(message.channel, ("""We've known each other for so long \nYour heart's been aching but you're too shy to say it \nInside we both know what's been going on \nWe know the game and we're gonna play it"""))
                        await client.send_message(message.channel, ("""I just want to tell you how I'm feeling \nGotta make you understand"""))
                        await client.send_message(message.channel, ("""Never gonna give you up, never gonna let you down \nNever gonna run around and desert you \nNever gonna make you cry, never gonna say goodbye \nNever gonna tell a lie and hurt you"""))
                        await client.send_message(message.channel, ("""https://www.youtube.com/watch?v=dQw4w9WgXcQ"""))
                    if tempVar.lower().startswith("cinnamon, body check"):
                        if nsfw == 1:
                            await client.send_message(message.channel, ("*glances down* (checking crap)"))
                            await client.send_message(message.channel, ("test *test* **test** ***test*** <3"))
                            time.sleep(0.5)
                            await client.send_message(message.channel, ("Chat functions: close enough"))
                            await client.send_message(message.channel, ("q-q https https://68.media.tumblr.com/4a08436fcc3b506a0cf4bccffa00019c/tumblr_okpobdtKfC1twgfw0o2_r1_500.gif"))
                            time.sleep(1)                 
                            if message.content.lower().startswith("q-q https"):
                                await client.send_message(message.channel, ("Meh, gifs aren't important anyway"))
                            else:
                                await client.send_message(message.channel, ("gif test: close enough"))
                        await client.send_message(message.channel, ("my body is ready"))
                    if tempVar.lower().startswith("cinnamon, google ") and not tempVar.lower().startswith("cinnamon, google images "):
                        tempVar = tempVar[17:len(tempVar)].replace(" ",'+')
                        await client.send_message(message.channel, ("https://www.google.com/search?q="+tempVar))
                        break
                    if tempVar.lower().startswith("cinnamon, google images "):
                        tempVar = tempVar[24:len(tempVar)].replace(" ",'+')
                        await client.send_message(message.channel, ("https://www.google.com/search?tbm=isch&q="+tempVar))
                        break
                    if tempVar.lower().startswith("cinnamon, search ") and not tempVar.lower().startswith("cinnamon, google images "):
                        tempVar = tempVar[17:len(tempVar)].replace(" ",'+')
                        await client.send_message(message.channel, ("https://www.google.com/search?q="+tempVar))
                        break
                    if tempVar.lower().startswith("cinnamon, image search "):
                        tempVar = tempVar[23:len(tempVar)].replace(" ",'+')
                        await client.send_message(message.channel, ("https://www.google.com/search?tbm=isch&q="+tempVar))
                        break
                    if tempVar.lower().startswith("cinnamon, lovecalc"):
                        embed=discord.Embed(title="**:heart: Love calculation for "+tempVar.split(" ")[2]+" and "+tempVar.split(" ")[3]+"**:", description="Percentage: {}%".format(((int((str(re.sub('[^0123456789abcdefghijklmnopqrstuvwxyz ]', '', tempVar, 36))).split(" ")[2], 36) + int((str(re.sub('[^0123456789abcdefghijklmnopqrstuvwxyz ]', '', tempVar, 36))).split(" ")[3], 36))%101)), color=0xff7979)
                        embed.set_footer(text="(don't take this seriously, you can bang anyone (with consent))")
                        await client.send_message(message.channel, embed=embed)
                    if tempVar.lower().startswith("cinnamon, ping"):
                        t1 = time.perf_counter()
                        await client.send_typing(message.channel)
                        t2 = time.perf_counter()
                        embed=discord.Embed(title=None, description='Ping: {}ms'.format(round((t2-t1)*1000)), color=0x2874A6)
                        await client.send_message(message.channel, embed=embed)
                    if tempVar.lower().startswith("put up"):#:)
                        for i in range(len(tempVar)):
                            tempVar = tempVar[1:len(tempVar)]
                            if tempVar.lower().startswith("wolfjob"):
                                await client.send_file(message.channel, str(os.path.join(os.path.dirname(__file__), str("assets\\misc\\wolfjob.jpg"))))
                    if tempVar.lower().startswith("cinnamon, eval("):#:)
                        eval(tempVar[15:len(tempVar)-1])
                    if tempVar.lower().startswith("flip a coin"):
                        if randint(0, 1) == 1:
                            await client.send_message(message.channel, ("heads!"))
                        else:
                            await client.send_message(message.channel, ("tails!"))

#!!!~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~[~~~START IMAGE GET SECTION!!!]
                            
                    if tempVar.lower().startswith("for shame"):
                        await client.send_file(message.channel, str(os.path.join(os.path.dirname(__file__), str("assets\\misc\\flandersShame.png"))))
                    if nsfw == 1:#note to self: edit in a sfw version of this, because its original purpose is to *call out* nsfw things
                        if tempVar.lower().startswith(":lewdsign:") or tempVar.startswith("lewdSign") or tempVar.lower().startswith(":lewd sign:") or tempVar.lower().startswith(":lewd_sign:"):
                            await client.send_file(message.channel, str(os.path.join(os.path.dirname(__file__), str("assets\\lewdSign\\")+str(randint(0, 13))+".png")))
                            tempVar = tempVar[1:len(tempVar)]
                        
#!!!---------------------------------------------------------------------------------------------------------------[!!!START D&D SECTION!!!]

                    if tempVar.lower().startswith("roll d"):
                        tempVar = tempVar[6:len(tempVar)]
                        if tempVar.lower().startswith("4"):
                            await self.roll(4, tempVar, message)
                        if tempVar.lower().startswith("6"):
                            await self.roll(6, tempVar, message)
                        if tempVar.lower().startswith("8"):
                            await self.roll(8, tempVar, message)
                        if tempVar.lower().startswith("10"):
                            await self.roll(10, tempVar, message)
                        if tempVar.lower().startswith("12"):
                            await self.roll(12, tempVar, message)
                        if tempVar.lower().startswith("20"):
                            await self.roll(20, tempVar, message)
                        if tempVar.lower().startswith("100"):
                            await self.roll(100, tempVar, message)

                            
                    tempVar = tempVar[1:len(tempVar)]
                    
            else:#If asleep:
                for i in range(len(tempVar)):#scan message
                    if tempVar.lower() == ("good morning, cinnamon"):#If message contains command to wake up
                        await client.send_message(message.channel, "Ohayogozaimasu...")
                        Nope = 0#release the kraken
                    if tempVar.lower() == ("good morning cinnamon"):#If message contains command to wake up
                        await client.send_message(message.channel, "Ohayogozaimasu...")
                        Nope = 0#release the kraken
                    tempVar = tempVar[1:len(tempVar)]
                Nope -= 1#I forget what this is for, but it's *probably* important
        
        #
        #                           commands that I don't know how to process in the actual discord commands api! aka all of them!
        #
    
        else:#If command (still within on_message
            print("    "+str(time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())))
            print("!!>"+message.author.display_name+": "+tempVar+"\n")

            #commands that can't be processed by discord's command api, because it is crap. Oh, wait, it's all the commands. huh.
            if tempVar.lower().startswith("!>vote"):
                with open(str(os.path.join(os.path.dirname(__file__), str("polls\\"+str(message.server)+"."))+str(message.channel)+'.CinnPoll'), 'r') as file:
                    fileBackup = file.readlines()
                with open(str(os.path.join(os.path.dirname(__file__), str("polls\\"+str(message.server)+"."))+str(message.channel)+'.CinnPoll'), 'a') as file:
                    tempVar3 = 0
                    for i in range(len(fileBackup)):
                        if fileBackup[i].lower().startswith(tempVar.lower()[7:len(tempVar)]):
                            tempVar3 = 1
                            tempVar2 = 0
                            while fileBackup[i][tempVar2] != ":":
                                tempVar2 += 1
                            print(fileBackup[i])
                            fileBackup[i] = fileBackup[i][0:tempVar2]+": "+str(int(fileBackup[i][tempVar2+1:len(fileBackup[i])])+1)
                    if tempVar3 == 0:
                        fileBackup.append("\n"+tempVar[7:len(tempVar)]+": 1")
                with open(str(os.path.join(os.path.dirname(__file__), str("polls\\"+str(message.server)+"."))+str(message.channel)+'.CinnPoll'), 'w') as file:
                    for i in range(len(fileBackup)):
                        file.write(fileBackup[i])
            if tempVar.lower().startswith("!>new_poll"):
                with open(str(os.path.join(os.path.dirname(__file__), str("polls\\"+str(message.server)+"."))+str(message.channel)+'.CinnPoll'), 'w') as file:
                            file.write("poll: "+tempVar[11:len(tempVar)])
            if tempVar.lower().startswith("!>get_poll"):
                with open(str(os.path.join(os.path.dirname(__file__), str("polls\\"+str(message.server)+"."))+str(message.channel)+'.CinnPoll'), 'r') as file:
                    fileBackup = file.readlines()
                    tempVar2 = ""
                    for i in range(len(fileBackup)):
                        if i != 0:
                            tempVar2 = tempVar2+"- "+str(fileBackup[i])[0:len(fileBackup[i])]
                    embed=discord.Embed(title=(str("------***"+str(fileBackup[0])[0:len(fileBackup[0])]+":***")+"------"), description=str(tempVar2), color=0xffaaff)
                    await client.send_message(message.channel, embed=embed)
            if tempVar.lower().startswith("!>superhelp"):
                await client.send_file(message.channel, str(os.path.join(os.path.dirname(__file__), str("assets\\Cinnamon Bot Help.html"))))
            if tempVar.lower() == ("!>toggle_indev"):
                if message.author.permissions_in(message.channel).manage_messages:
                    if inDev == 0:
                        #there are currently no in-dev features, lol
                        await client.send_message(message.channel, "Boop boop be doop! Enabling in-dev features! This may break some formatting and/or reference files that don't yet exist. If you enable these features, things may break. You have been warned.")
                        inDev = 1
                    else:
                        await client.send_message(message.channel, "Disabling in dev features, good choice. (certain residual effects may percist, such as muting. this toggle only enables/disabhles access to commands.)")
                        inDev = 0
                else:
                    await client.send_message(message.channel, "You have to be chatmod+ (have the ability to delete messages) in order to toggle the indev features, dummy!")
            if tempVar.lower().startswith("!>mute"):
                if message.author.permissions_in(message.channel).manage_messages:
                    muted.append(tempVar[7:len(tempVar)].lower())
                    await client.send_message(message.channel, tempVar[7:len(tempVar)]+" muted! The mute will last until you unmute them, or I am disabled. You will have to manually reinstate the mute if I am restarted")
                else:
                    await client.send_message(message.channel, "You must be of chatmod rank (able to delete messages) to toggle a mute! Don't worry, they're temporary")
            if tempVar.lower().startswith("!>unmute"):
                if message.author.permissions_in(message.channel).manage_messages:
                    try:
                        muted.remove(tempVar[9:len(tempVar)].lower())
                        await client.send_message(message.channel, "unmuted "+tempVar[9:len(tempVar)])
                    except:
                        await client.send_message(message.channel, "That person either doesn't exist or isn't muted")
                else:
                    await client.send_message(message.channel, "You must be of chatmod rank (able to delete messages) to toggle a mute! Don't worry, they're temporary")
            if tempVar.lower().startswith("!>settings"):
                if message.author.permissions_in(message.channel).manage_messages:#this command is for chat moderator rank or higher
                    with open(str(os.path.join(os.path.dirname(__file__), str("configs\\"+str(message.server)+"\\"))+str(message.channel)+'.config'), 'r') as file:
                        tempVar2 = file.readlines()
                        tempVar3 = ""
                        for i in range(len(tempVar2)):
                            tempVar3 = str(tempVar3+tempVar2[i]+"\n")
                    await client.send_message(message.channel, "Current settings for this channel:\n\n"+tempVar3)
                else:
                    await client.send_message(message.channel, "You don't have a high enough rank to use this command!")
            if tempVar.lower().startswith("!>getlog"):
                if True: #message.author.permissions_in(message.channel).manage_messages:#this command is for chat moderator rank or higher
                    await client.send_file(message.author, str(os.path.join(os.path.dirname(__file__), str("logs\\"+str(message.server)+"\\"))+str(message.channel)+'.html'));
                    await client.send_message(message.channel, "Check your DM's!")
                else:
                    await client.send_message(message.channel, "You don't have a high enough rank to use this command!")
            if tempVar.lower().startswith("!>enable_nsfw"):
                if message.author.permissions_in(message.channel).manage_messages:
                    if nsfwCheck == 0:
                        await client.send_message(message.channel, "Endble NSFW for thic channel? this action is irreversable! (enter command again to confirm)")
                        nsfwCheck = 1
                    else:
                        await client.send_message(message.channel, "enabling...")
                        nsfw = 1
                        await self.createConfig(tempVar, message)
                else:
                    await client.send_message(message.channel, "You don't have a high enough rank to use this command!")
            if tempVar.lower().startswith("!>chatmod"):
                tempVar = message.content
                if message.author.permissions_in(message.channel).manage_messages:#this command is for chat moderator rank or higher
                    if(len(tempVar) > 10):
                        chatMod = int(tempVar[10])
                        await self.createConfig(tempVar, message)
                    else:
                        with open(str(os.path.join(os.path.dirname(__file__), str("configs\\"+str(message.server)+"\\"))+str(message.channel)+'.config'), 'r') as file:
                            tempVar2 = file.readlines()
                            await client.send_message(message.channel, (tempVar2[0]))
                else:
                    await client.send_message(message.channel, "You don't have a high enough rank to use this command!")
            if tempVar.lower().startswith("!>test"):
                await client.send_message(message.channel, "Hey, you're not a doofus! Good job, you!")
            if tempVar.lower().startswith("!>sscstest"):
                await client.send_message(message.channel, "Yep, not a doofus in the slightest ^_^")
            if tempVar.lower().startswith("!>goodbot"):
                await client.send_message(message.channel, ("Arigatogozaimasu, "+message.author.display_name+"-sama! >.<"))
            if tempVar.lower().startswith("!>get_muted"):
                await client.send_message(message.channel, str(muted))

class Commands:#There's probably "pass_message" or whatever. I didn't find it
    """The majority of cinnamon commands"""

    def __init__(self, client):
        self.client = client
    
    @commands.command(pass_context=True, no_pm=True)
    async def test(self, ctx):
        print("can't even get a ping & pong to work")
    
    @commands.command(pass_context=True, no_pm=True)
    async def SSCSTest(self, ctx):
        print("pass message you incompetant fish!")
    
    @commands.command(pass_context=True, no_pm=True)
    async def GoodBot(self, ctx):
        print("you are an butt")
    
    @commands.command(pass_context=True, no_pm=True)
    async def chatmod(self, ctx):
        print("the command api sucks")

    @commands.command(pass_context=True, no_pm=True)
    async def settings(self, ctx):
        print("discord, pass message into commands, not ctx. this is literal child's play. I *need* message.channel, message.author, etc. But I have to pass everything through on_message for that. It's not that hard of a fix")
            
    @commands.command(pass_context=True, no_pm=True)
    async def getLog(self, ctx):
        print("can't even get this to work")

    @commands.command(pass_context=True, no_pm=True)
    async def superHelp(self, ctx):
        """----- this page is horribly formatted; get a better one with this!"""
        print("this command is processed in the main message handler")

    @commands.command(pass_context=True, no_pm=True)
    async def enable_indev(self, ctx):
        "don't"
        print("take a wild guess where this command is processed")

    @commands.command(pass_context=True, no_pm=True)
    async def mute(self, ctx):
        print("this command is processed in the main message handler")

    @commands.command(pass_context=True, no_pm=True)
    async def unmute(self, ctx):
        print("this command is processed in the main message handler")

    @commands.command(pass_context=True, no_pm=True)
    async def get_muted(self, ctx):
        print("guess what? command can't be processed here, because there's no message passed!")

class Polling:#polling commands start here! don't put normal ones in hereor you are a doofus!
    """see name"""
    
    def __init__(self, client):
        self.client = client
    
    @commands.command(pass_context=True, no_pm=True)
    async def get_poll(self, ctx):
        print("this command is processed in the main message handler")
        
    @commands.command(pass_context=True, no_pm=True)
    async def new_poll(self, ctx):
        print("this command is processed in the main message handler")
        
    @commands.command(pass_context=True, no_pm=True)
    async def vote(self, ctx):
        print("this command is processed in the main message handler")

#START BACKGROUND SECTION

async def background():
    counter = 1
    await client.wait_until_ready()
    while not client.is_closed:
        await asyncio.sleep(300)
        print("Still alive! "+str(counter))
        counter += 1
                
#END BACKGROUND SECTION

client = commands.Bot(command_prefix=commands.when_mentioned_or('!>'), description='A very trustworthy bot')
client.add_cog(Commands(client))
client.add_cog(Polling(client))
client.add_cog(Main())


client.loop.create_task(background())

while True:
    try:
        client.loop.run_until_complete(client.start(token))
    except BaseException:
        reconnectTime += 5
        print("FAILED TO RUN CLIENT, RETRYING IN "+str(reconnectTime)+"...")
        time.sleep(reconnectTime)
