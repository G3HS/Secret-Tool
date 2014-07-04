START pyinstaller E:\Secret-Tool\mainWIN.spec
rd E:\Secret-Tool\mainWIN.spec /s/q
COPY "E:\Secret-Tool\G3HS_Documentation.pdf" "E:\Secret-Tool\mainWIN.spec\dist"
COPY "E:\Secret-Tool\PokeRoms.ini" "E:\Secret-Tool\mainWIN.spec\dist"
COPY "E:\Secret-Tool\Finish.bat" "E:\Secret-Tool\mainWIN.spec\dist"
XCOPY "E:\Secret-Tool\Resources" "E:\Secret-Tool\mainWIN.spec\dist" /D /E /C /R /I /K /Y 