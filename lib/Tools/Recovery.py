from lib.Tools.RecoveryINI import *
from GLOBALS import *

class Recovery:
    def __init__()):
        with open(GLOBALS.OpenRomName, "r+b") as rom:
            rom.seek(0xAC)
            self.gamecode = rom.read(4)
            if self.gamecode not in RecoveryIni.INI:
                self.NoRecovery = True
                return
            else:
                self.NoRecovery = False
                self.INI = RecoveryIni.INI[self.gamecode]
                self.Recover(rom)
            
    def Recover(rom):
        for name, offset in self.INI.iteritems():
            pass
