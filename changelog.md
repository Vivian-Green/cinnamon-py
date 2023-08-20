# cinnamon-py changelog
version numbers here are from local dev branch, and not all are reflected on github history.
</br></br></br>

# changes in 2.4.0:
- moved dice and logging related functions to cinDice.py and cinLogging.py respectively
- slight refactor on top of that

</br></br></br>

# changes in 2.3.3:
- overhauled Cinnamon Bot Help.html
- certain prompts can now be used with or without a space
- removed a very old meme & an equally old reference.

# changes in 2.3.2:
- renamed !>superhelp to !>help
- !> help now shares a direct link to a preview of Cinnamon Bot Help.html instead of sharing the file

# changes in 2.3.1:
- moved changelog from readme.txt to changelog.md, also tweaked gitignore to actually work

# changes in 2.3.0:
- added new shorthand for "cinnamon, eval(<expression>)" command: /solve <expression>. This matches SQ's (likely CMI's) /solve syntax, but accepts python expressions
- fixed a few typos
- removed already finished todos
- FINALLY moved token to its own config
- added runtime prompts ("cinnamon, runtime" and "!>runtime")

</br></br></br>

# changes in 2.2.2:
- webp attachments will now be recognized as images by the appendToLog function
- cleaned up appendToLog and tryToLog to be more readable

# changes in 2.2.1:
- some quick tweaks to comments to be more github-friendly
- removed some unnecessary debug statements, most of them "BALLS2" or something similar.

# changes in 2.2.0:
- threw appendToLog() function through openAI's new chatgpt 4, because dammit, I don't want to do that myself. It's much more readable now.
- edited appendToLog() function to be more clean, after chatgpt took a crack at it

</br></br></br>

# changes in 2.1.2:
- changed "changes from" in changelog to "changes in" bc shit confusin
- removed rolling from gr0ss list, using insane methods like string.find()
- rewrote ALL of rolling, bc jfc
- removed unnecessary commented imports
- re-added random import
- added multi-dice support for rolling in rewrite
- added patchy bit to make gh's lewdie bot shut
- fixed custom statuses
- moved changelog from bot.py to README.txt
- moved simpleResponses to config/simpleResponses.json
- edited logging function for cleanliness (in console)
- renamed remaining uses of tempVar and tempVar2
- cleaned up random print statements & comments
- finally removed gr0ss section of code that kept checking through the same text, one letter at a time, for different prompts. reworked.
- removed unnecessary reconnectTime, fileBackup, and CTX variables

# changes in 2.1.1:
- documented simpleResponses
- cleaned up message response section further
- added containsAny(str textToCheck, array texts) function, to simplify some if statements
- changed most usages of "A.startswith(B)" to "B in A"
- minor edits for consistency
- removed polling feature, reaction polls are objectively better in every way
- removed !>sscstest command, whatever that abbreviation was for
- removed add_cog() comments, as they do nothing, and are ugly
- reformatted on_ready() print statements
- remembered with an "OR" is
- added handlePrompts() function, making handleRegularMessage() much more readable
- added tryToLog() function, after appendToLog() function, making handleRegularMessage() much more readable
- made messageContent global
- lot of debugging

# changes in 2.1.0:
- removed chatmod feature, no one will ever use it
- removed whatever "cinnamon, drop the nuke" did... wth? Something speficic to an oooold chat I am no longer in
- made ytPlaylist command - does ytCrawl() with the first URL in the command, and spits out the result. This is useless, but the code isn't, so I cleaned it up real nice. Renamed shit too. ew.
- massive refactor of simple commands
- removed muting feature, just use discord's built in shit
- removed inDev, nsfw, chatmod, config
- removed background task
- removed many unused variables