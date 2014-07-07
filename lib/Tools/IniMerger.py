import wx,os
import ConfigParser
from GLOBALS import *
from lib.OverLoad.Button import *
from textwrap import fill

class MergerPrompt(wx.Dialog):
    def __init__(self, parent, *args, **kw):
        wx.Dialog.__init__(self, parent=None, id=wx.ID_ANY,size=(600,300))
        self.SetWindowStyle( self.GetWindowStyle() | wx.RESIZE_BORDER )
        self.Caller = parent
        self.InitUI()
        self.SetTitle("Ini Merger")
        self.ShowModal()
        
    def InitUI(self):
        pnl = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        txt = wx.StaticText(pnl, -1, fill("Please choose the two ini's you want to merge. The old and new inis will be indexed and searched. Anything not in the old ini that is found in the new ini will be added to the old ini. Remember to back-up your ini!!!",100))
        vbox.Add(txt, 0, wx.EXPAND | wx.ALL, 5)
        
        OldHBox = wx.BoxSizer(wx.HORIZONTAL)
        vbox.Add(OldHBox, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 5)
        Oldtxt = wx.StaticText(pnl, -1, "Old ini: ")
        OldHBox.Add(Oldtxt, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 5)
        self.Old = wx.FilePickerCtrl(pnl,wildcard = "Ini files (*.ini)|*.ini")
        OldHBox.Add(self.Old, 10, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 5)
        
        NewHBox = wx.BoxSizer(wx.HORIZONTAL)
        vbox.Add(NewHBox, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 5)
        Newtxt = wx.StaticText(pnl, -1, "New ini: ")
        NewHBox.Add(Newtxt, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 5)
        self.New = wx.FilePickerCtrl(pnl,wildcard = "Ini files (*.ini)|*.ini")
        NewHBox.Add(self.New, 10, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 5)
        
        SUBMIT = Button(pnl, 2, "Submit")
        self.Bind(wx.EVT_BUTTON, self.Submit, id=2)
        vbox.Add(SUBMIT, 0, wx.EXPAND | wx.ALL, 5)
        
        pnl.SetSizerAndFit(vbox)
        self.Fit()
        self.SetMinSize(self.GetEffectiveMinSize())
    
    def Submit(self, event=None):
        iniloc = self.New.GetPath()
        orginiloc = self.Old.GetPath()
        if iniloc == "" or orginiloc == "":
            return
        #Backup ini
        BackUpIni = os.path.join(os.getcwd(),"PokeRoms.ini.bak")
        with open(BackUpIni, "w+") as backup:
            with open (orginiloc, "r+") as org:
                backup.write(org.read())
        #Load up our new config file for parsing.
        NewIni = ConfigParser.ConfigParser()
        NewIni.read(iniloc)
        NewRomSections = NewIni.sections()
        #Check if all sections are present:
        OldRomSections = Globals.INI.sections()
        #Get any new sections I may have added and 
        #update any current base sections.
        for section in NewRomSections:
            NewOptions = NewIni.options(section)
            NewOptsValues = []
            OldOptions = Globals.INI.options(section)
            for opt in NewOptions:
                NewOptsValues.append((opt, NewIni.get(section, opt)))
            if section not in OldRomSections:
                Globals.INI.add_section(section)
                for opt, value in NewOptsValues:
                    Globals.INI.set(section, opt, value)
            else:
                for opt in NewOptions:
                    if opt not in OldOptions:
                        Globals.INI.set(section, opt, 
                                        NewIni.get(section, opt))
        #Now, go through every section of the old ini and make sure it
        #has every singe option the new ini has.
        for section in OldRomSections:
            #The custom sections of the old ini are not found in the 
            #new ini. So, the new options are copied from their base
            #sections found in the new ini.
            if section != "ALL":
                gamecode = Globals.INI.get(section, "gamecode")
            else: continue
            UpdateOpts = NewIni.options(gamecode)
            NewUpdateOptsValues = []
            #Get all of the options from the new ini for the section.
            for opt in UpdateOpts:
                NewUpdateOptsValues.append((opt, 
                                    NewIni.get(gamecode, opt)))
            #If option is not found, add it.
            OldOpts = Globals.INI.options(section)
            for opt, value in NewUpdateOptsValues:
                if opt not in OldOpts:
                    Globals.INI.set(section, opt, value)
        #Write the new changes.
        with open(orginiloc, "w") as PokeRomsIni:
            Globals.INI.write(PokeRomsIni)
        self.Destroy()