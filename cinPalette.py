# import * from here just to ensure values are consistent
# todo: import these values from a configuration file, though ig this kind of is the configuration file

esc = "\033"
clearFormatting = f"{esc}[0m"
clrEsc = f"{clearFormatting}{esc}"

defaultColor = f"{esc}[37m" #[38:5:182m"
labelColor = f"{esc}[36m" #[38:5:170m"
errorColor = f"{clrEsc}[91m"
miscColor = f"{clrEsc}[37m"
highlightedColor = f"{esc}[36m" #[38:5:39m"
debugColor = f"{clrEsc}[92m"
fiveLines = "\n\n\n\n\n"
indent = "  "