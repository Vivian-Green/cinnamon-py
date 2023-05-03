Last edited on Apr 30 2023
Last edited before conversion, on Dec 25, 2017

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The contained files are for a discord bot entitled "cinnamon", which has features such as moderation, creating logs for channels, and basic fun stuff

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

SETUP:
- Once you somehow gotten this file and invited the bot to your server, if for some reason it is not nicknamed "cinnamon", fix that, as some commands are otherwise recursive
- run bot.py for a console window, or bot.pyw for... not that

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

check out "Cinnamon Bot Help.html" in ./assets/ for more loose documentation and better formatting than raw txt, but still garbage, viv from 5 years ago












Changelog:

changes in 2.1.0:
	removed chatmod feature, no one will ever use it
	removed whatever "cinnamon, drop the nuke" did... wth? Something speficic to an oooold chat I am no longer in
	made ytPlaylist command - does ytCrawl() with the first URL in the command, and spits out the result. This is useless, but the code isn't, so I cleaned it up real nice. Renamed shit too. ew.
	massive refactor of simple commands
	removed muting feature, just use discord's built in shit
	removed inDev, nsfw, chatmod, config
	removed background task
	removed many unused variables

changes in 2.1.1:
	documented simpleResponses
	cleaned up message response section further
	added containsAny(str textToCheck, array texts) function, to simplify some if statements
	changed most usages of "A.startswith(B)" to "B in A"
	minor edits for consistency
	removed polling feature, reaction polls are objectively better in every way
	removed !>sscstest command, whatever that abbreviation was for
	removed add_cog() comments, as they do nothing, and are ugly
	reformatted on_ready() print statements
	remembered with an "OR" is
	added handlePrompts() function, making handleRegularMessage() much more readable
	added tryToLog() function, after appendToLog() function, making handleRegularMessage() much more readable
	made messageContent global
	lot of debugging

changes in 2.1.2:
	changed "changes from" in changelog to "changes in" bc shit confusin
	removed rolling from gr0ss list, using insane methods like string.find()
	rewrote ALL of rolling, bc jfc
	removed unnecessary commented imports
	re-added random import
	added multi-dice support for rolling in rewrite
	added patchy bit to make gh's lewdie bot shut
	fixed custom statuses
	moved changelog from bot.py to README.txt
	moved simpleResponses to config/simpleResponses.json
	edited logging function for cleanliness (in console)
	renamed remaining uses of tempVar and tempVar2
	cleaned up random print statements & comments
	finally removed gr0ss section of code that kept checking through the same text, one letter at a time, for different prompts. reworked.
	removed unnecessary reconnectTime, fileBackup, and CTX variables

changes in 2.2.0:
    threw appendToLog() function through openAI's new chatgpt 4, because dammit, I don't want to do that myself. It's much more readable now.
    edited appendToLog() function to be more clean, after chatgpt took a crack at it

changes in 2.2.1:
    some quick tweaks to comments to be more github-friendly
    removed some unnecessary debug statements, most of them "BALLS2" or something similar.