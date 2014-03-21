@echo off&setlocal
PING 1.1.1.1 -n 1 -w 5000 >NUL
SET CurrDIR=%CD%
for %%i in ("%~dp0..") do set "ParDIR=%%~fi"
DEL "%ParDIR%\Gen_III_Suite.exe"
MOVE "%CurrDIR%\Gen_III_Suite.exe" "%ParDIR%"
start "" "%ParDIR%\Gen_III_Suite.exe"
rd /s/q "%CurrDIR%"
EXIT 0


