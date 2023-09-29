code2flow bot.py --output .//graphs//botCFG.png
code2flow cinIO.py --output .//graphs//cinIOCFG.png
code2flow cinSolve.py --output .//graphs//cinSolve.png
code2flow cinLogging.py --output .//graphs//cinLogging.png

cd graphs

IF EXIST botCFG.gv (
    del botCFG.gv
)
IF EXIST cinIOCFG.gv (
    del cinIOCFG.gv
)
IF EXIST cinSolve.gv (
    del cinSolve.gv
)
IF EXIST cinLogging.gv (
    del cinLogging.gv
)

pause