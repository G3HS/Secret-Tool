@echo off&setlocal
PING 1.1.1.1 -n 1 -w 5000 >NUL
SET CurrDIR=%CD%
SET ChildDIR="%CurrDIR%/tmp"
DEL "%CurrDIR%\Gen_III_Suite.exe"
MOVE "%ChildDIR%\Gen_III_Suite.exe" "%CurrDIR%"
start "" "%CurrDIR%\Gen_III_Suite.exe"
rd %ChildDIR% /s/q
EXIT 0


