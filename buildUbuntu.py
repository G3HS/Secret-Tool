from os import system
from shutil import copy,copytree,rmtree

system("pyinstaller mainUbuntu.spec")
rmtree("/media/Storage/Secret-Tool/build")
copy("/media/Storage/Secret-Tool/G3HS_Documentation.pdf","/media/Storage/Secret-Tool/dist/")
copy("/media/Storage/Secret-Tool/PokeRoms.ini","/media/Storage/Secret-Tool/dist/")
copy("/media/Storage/Secret-Tool/Finish.bat","/media/Storage/Secret-Tool/dist/")
copytree("/media/Storage/Secret-Tool/Resources","/media/Storage/Secret-Tool/dist/Resources")
