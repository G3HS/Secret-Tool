import wx
from lib.Tools.RecoveryINI import *
from GLOBALS import *
from lib.OverLoad.Button import *
from lib.Tools.rom_insertion_operations import *
try: from wx.lib.pubsub import Publisher as pub
except: 
    print "Changing pub mode"
    from wx.lib.pubsub import setuparg1
    from wx.lib.pubsub import pub
import os

class Recovery:
    def __init__(self):
        if Globals.OpenRomGameCode not in RecoveryIni.INI:
            self.NoRecovery = True
            return
        else:
            self.NoRecovery = False
            self.INI = RecoveryIni.INI[Globals.OpenRomGameCode]
            Prompt = wx.MessageDialog(None, 
                                "The error you just recieved could stem from an issue with a malformed ini. There is a recovery feature built into G3HS that may be able to recover your ini by searching the rom for the pointers to all of the tables. Would you like to attempt this?", 
                                'Attempt recovery?', 
                                wx.YES_NO | wx.ICON_ERROR)
            if Prompt.ShowModal() == wx.ID_YES:
                RecoveryPrompt(self)
            
    def Recover(self,numbersini):
        with open(Globals.OpenRomName, "r+b") as rom:
            rom_id_offset = int(Globals.INI.get("ALL", "OffsetThatContainsSecondRomID"),0)
            rom.seek(rom_id_offset)
            x = "0000"
            y = None
            all_possible_rom_ids = Globals.INI.sections()
            ini = os.path.join("PokeRoms.ini")
            while True:
                if x in all_possible_rom_ids:
                    x = str(int(x) + 1).zfill(4)
                    continue
                else:
                    Globals.OpenRomID = x
                    #Write new rom_id to rom.
                    byte_rom_id = get_hex_from_string(Globals.OpenRomID)
                    rom.write(byte_rom_id)
                    
                    Globals.INI.add_section(Globals.OpenRomID)
                    options = Globals.INI.options(Globals.OpenRomGameCode)
                    tmp_ini = []
                    for opt in options:
                        tmp_ini.append((opt, Globals.INI.get(Globals.OpenRomGameCode, opt)))
                    for opt, value in tmp_ini:
                        Globals.INI.set(Globals.OpenRomID, opt, value)
                    break
            for name, offset in self.INI.iteritems():
                rom.seek(offset)
                NewOffset = hex(read_pointer(rom.read(4))).rstrip("L")
                Globals.INI.set(Globals.OpenRomID, name, NewOffset)
                
            for name, number in numbersini.iteritems():
                Globals.INI.set(Globals.OpenRomID, name, number)
        
        with open(ini, "w") as PokeRomsIni:
            Globals.INI.write(PokeRomsIni)
        wx.CallAfter(pub.sendMessage,"ReloadRom",data=None)
            
class RecoveryPrompt(wx.Dialog):
    def __init__(self, parent, *args, **kw):
        wx.Dialog.__init__(self, parent=None, id=wx.ID_ANY)
        self.SetWindowStyle( self.GetWindowStyle() | wx.RESIZE_BORDER )
        self.Caller = parent
        self.InitUI()
        self.SetTitle("Ini Recovery")
        self.ShowModal()
        
    def InitUI(self):
        pnl = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        txt = wx.StaticText(pnl, -1, "An ini that has been corrupted can often be recovered \nby reading the offsets of each table from the pointers \nto said tables. This function will attempt to do just that.")
        vbox.Add(txt, 0, wx.EXPAND | wx.ALL, 5)
        
        txt2 = wx.StaticText(pnl, -1, "\nBefore I recover the tables, I need some info on how \nbig they were... All of these numbers can be changed \nlater in the ini if need be and the original values \nfor your rom are provided.\n")
        vbox.Add(txt2, 0, wx.EXPAND | wx.ALL, 5)
        
        PokeHBox = wx.BoxSizer(wx.HORIZONTAL)
        vbox.Add(PokeHBox, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5)
        Poketxt = wx.StaticText(pnl, -1, "TOTAL Number of 'mons: ")
        PokeHBox.Add(Poketxt, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 5)
        self.Pokemon = wx.SpinCtrl(pnl, -1,style=wx.TE_CENTRE, size=(100,-1))
        self.Pokemon.SetRange(0,1020)
        self.Pokemon.SetValue(412)
        PokeHBox.Add(self.Pokemon, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 5)
        
        MoveHBox = wx.BoxSizer(wx.HORIZONTAL)
        vbox.Add(MoveHBox, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5)
        Movetxt = wx.StaticText(pnl, -1, "Number of Moves: ")
        MoveHBox.Add(Movetxt, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 5)
        self.Move = wx.SpinCtrl(pnl, -1,style=wx.TE_CENTRE, size=(100,-1))
        self.Move.SetRange(0,0xFFFF)
        self.Move.SetValue(int(Globals.INI.get(Globals.OpenRomGameCode, "numberofattacks"),0))
        MoveHBox.Add(self.Move, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 5)
        
        ItemHBox = wx.BoxSizer(wx.HORIZONTAL)
        vbox.Add(ItemHBox, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5)
        Itemtxt = wx.StaticText(pnl, -1, "Number of Items: ")
        ItemHBox.Add(Itemtxt, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 5)
        self.Item = wx.SpinCtrl(pnl, -1,style=wx.TE_CENTRE, size=(100,-1))
        self.Item.SetRange(0,0xFFFF)
        self.Item.SetValue(int(Globals.INI.get(Globals.OpenRomGameCode, "numberofitems"),0))
        ItemHBox.Add(self.Item, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 5)
        
        TypeHBox = wx.BoxSizer(wx.HORIZONTAL)
        vbox.Add(TypeHBox, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5)
        Typetxt = wx.StaticText(pnl, -1, "Number of Types: ")
        TypeHBox.Add(Typetxt, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 5)
        self.Type = wx.SpinCtrl(pnl, -1,style=wx.TE_CENTRE, size=(100,-1))
        self.Type.SetRange(0,0xFFFF)
        self.Type.SetValue(int(Globals.INI.get(Globals.OpenRomGameCode, "numberoftypes"),0))
        TypeHBox.Add(self.Type, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 5)
        
        AbilityHBox = wx.BoxSizer(wx.HORIZONTAL)
        vbox.Add(AbilityHBox, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5)
        Abilitytxt = wx.StaticText(pnl, -1, "Number of Abilities: ")
        AbilityHBox.Add(Abilitytxt, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 5)
        self.Ability = wx.SpinCtrl(pnl, -1,style=wx.TE_CENTRE, size=(100,-1))
        self.Ability.SetRange(0,0xFFFF)
        self.Ability.SetValue(int(Globals.INI.get(Globals.OpenRomGameCode, "numberofabilities"),0))
        AbilityHBox.Add(self.Ability, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 5)
        
        SUBMIT = Button(pnl, 2, "Submit")
        self.Bind(wx.EVT_BUTTON, self.Submit, id=2)
        vbox.Add(SUBMIT, 0, wx.EXPAND | wx.ALL, 5)
        
        pnl.SetSizerAndFit(vbox)
        self.Fit()
        self.SetMinSize(self.GetEffectiveMinSize())
    
    def Submit(self, event=None):
        ini = {"numberofpokes":str(self.Pokemon.GetValue()),
               "numberofattacks":str(self.Move.GetValue()),
               "numberofitems":str(self.Item.GetValue()),
               "numberoftypes":str(self.Type.GetValue()),
               "numberofabilities":str(self.Ability.GetValue())}
        wx.CallAfter(self.Destroy)
        self.Caller.Recover(ini)
