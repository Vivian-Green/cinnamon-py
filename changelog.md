# cinnamon-py changelog
version numbers here are from local dev branch, and not all are reflected on github history.
</br></br></br>

# changes in 2.8.2:
- added option to delete (and restore) reminders through the
- !>reminders menu, which actually has one use now, through reactions

- absolute times absolutely do NOT work-

# changes in 2.8.1:
- new message on cinnamon startup & reboot
- `!>cinloggingchannel` to set this channel (globally for a given bot instance- also editable in config.yaml)
- fixed some problems with reminders- should be much more consistent now!

# changes in 2.8.0:
- reminders can now use absolute times, for example, `!>remindme @today @1pm it is now 1pm`
- reminder text cannot contain an @ that is not followed by a valid absolute time
- reminders can use !>reminder AND !>remindme instead of just !>remindme
- relative times (eg: !>remindme 1h) seem to be borked rn?
- datetimes are relative to the host for now
</br></br></br>

# changes in 2.7.4:
- empty caches are now generated if they do not exist on startup
- config & cache dirs are now ensured on startup
- cleaned up cinLogging

# changes in 2.7.3:
- add feature to slap prompt to specifically slap gh's bot by spoofing a face
- reworked prompts to be cleaner, making better use of containsAny()

# changes in 2.7.2:
- move configs to yaml

# changes in 2.7.1:
- changed colors for logging
- /solve results are now formatted to use comma separators for thousands

# changes in 2.7.0:
- cinLogging rewrite
- print statements now use cinLogging
- removed unnecessary debug print statements
- added launcher (cinLauncher.py) launch with cinStart.bat
- added !>reboot command
- removed unnecessary class usage in bot.py (why did that need to be its own class)

</br></br></br>

# changes in 2.6.0:
- implemented whitelist /solve code provided by https://github.com/Koenig-Heinrich-der-4te
- removed redundant runtime prompt (now only !>runtime works)
- "next reminder is in..." message timestamp now includes hours, and won't display if there are no reminders
- control flow graphs properly added

</br></br></br>

# changes in 2.5.4:
- bug fixes:
  - handleSimpleResponses no longer forms a response for every possible simple prompt, for every message, regardless of whether it contains a prompt. Whoops.
  - conversation starters no longer read their file every time one is chosen. Whoops.
  - pinging cinnamon now works with discord.py rewrite syntax. This has been broken for several years.
  - messageContent is no longer global, to prevent race conditions
- getting cinnamon's ping is now bound to !>ping
- cinnamon now updates its status to its last online time
- removed unused code:
  - youtube crawler
  - cat prompt (literally did not function)
  - test command (overlap with !>ping)
- minecraft related code temporarily disabled for stability
- way more refactoring

# changes in 2.5.3:
- moved all regex definitions to the header
- another hotfix to make /solve slightly less insecure

# changes in 2.5.2:
- hotfix to make /solve slightly less insecure

# changes in 2.5.1:
- hotfix to actually let "cinnamon, eval" function (eval keyword was blocked)
- hotfix to lock /solve behind admin guild

# changes in 2.5.0:
things here aren't fully implemented. This version is being pushed for history's sake & is not stable
- strings can no longer be injected into \/solve. seriously do not run this bot on a public server lol.
- new feature: Admin guild. certain things are locked behind whether a server is manually set as the admin guild for this instance of cinnamon in the config.
  - added !>dox, which sends the bot's public IP address. if the command is sent in the admin guild.
- some support for launching a minecraft server remotely added. This is still very rough.
  - !>minecraft help
  - !>minecraft start
  - !>minecraft command <command> (still unfinished)
- added reminders with relative time syntax (eg: !>remindme 4h20m check oven for burnt pizza)
- added version command
- edited logging palette, added dict for palette
- even more more refactoring

</br></br></br>

# changes in 2.4.1:
- added strings.json config
- more refactoring for readibility & some pep8 stuff

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
- added changelog
