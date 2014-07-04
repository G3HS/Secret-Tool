from os import system,remove
from shutil import copyfile,copytree

system("pyinstaller","E:\Secret-Tool\mainWIN.spec")
remove("E:\Secret-Tool\build")
copyfile("E:\Secret-Tool\G3HS_Documentation.pdf","E:\Secret-Tool\mainWIN.spec\dist")
copyfile("E:\Secret-Tool\PokeRoms.ini","E:\Secret-Tool\mainWIN.spec\dist")
copyfile("E:\Secret-Tool\Finish.bat","E:\Secret-Tool\mainWIN.spec\dist")
copytree("E:\Secret-Tool\Resources","E:\Secret-Tool\mainWIN.spec\dist")
