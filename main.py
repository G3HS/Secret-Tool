#!/usr/lib/python
# -*- coding: utf-8 -*- 
#venv pyi-env-name
from __future__ import division
import wx, os, ConfigParser, sys, textwrap, platform
from lib.Tools.rom_insertion_operations import *
from lib.OverLoad.CheckListCtrl import *
from lib.OverLoad.Button import *
from lib.PokeDataEdit.PokeSpriteTab import *
from lib.PokeDataEdit.ExpandPokes import *
from lib.CustomDialogs.BaseRepointer import *
from cStringIO import StringIO
from lib.CustomDialogs.EmailError import *
import json
import traceback
import urllib2
from lib.HexEditor.hexeditor import *
from lib.PokeDataEdit.HabitatTab import *
from lib.OverLoad.UpdateDialog import *
from binascii import hexlify, unhexlify
from lib.Tools.Recovery import *

try: from wx.lib.pubsub import Publisher as pub
except: 
    print "Changing pub mode"
    from wx.lib.pubsub import setuparg1
    from wx.lib.pubsub import pub

from GLOBALS import *

OPEN = 1
poke_num = 0
MOVES_LIST = None
ITEM_NAMES = None
returned_offset = None

description = textwrap.fill("POK\xe9MON Gen III Hacking Suite was developed to enable better cross-platform POK\xe9MON Rom Hacking by removing the need for the .NET framework.  It was also created in order to be more adaptable to more advanced hacking techniques that change some boundaries, like the number of POK\xe9MON. In the past, these changes rendered some very necessary tools useless and which made using these new limits difficult.", 110)

description = encode_per_platform(description)

licence = textwrap.fill("The MIT License (MIT)",90)+"\n\n\n"+textwrap.fill("Copyright (c) 2014 karatekid552",90)+"\n\n\n"+textwrap.fill("Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the 'Software'), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:",90)+"\n\n"+textwrap.fill("The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.",90)+"\n\n"+textwrap.fill("THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.",70)

licence = encode_per_platform(licence)

class MainWindow(wx.Frame, wx.FileDropTarget):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(800,625))
        wx.FileDropTarget.__init__(self)
        
        self.SetDropTarget(self)
        self.open_rom = None
        #self.path = module_path()
        self.open_rom_ini = {}
        
        self.timer = None
        
        self.panel = wx.Panel(self)
        self.tabbed_area = TabbedEditorArea(self.panel)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.tabbed_area, 1, wx.ALL|wx.EXPAND, 5)
        self.panel.SetSizer(self.sizer)
        self.Layout()
        
        self.CreateStatusBar() # A Statusbar in the bottom of the window
        # Setting up the menu.
        filemenu = wx.Menu()
        helpmenu = wx.Menu()
        # wx.ID_ABOUT and wx.ID_EXIT are standard IDs provided by wxWidgets.
        filemenu.Append(wx.ID_OPEN, "&Open"," Open a ROM.")
        help_ID = wx.NewId()
        ContactID = wx.NewId()
        helpmenu.Append(help_ID, "&Documentation"," Open documentation. Requires a pdf reader.")
        helpmenu.AppendSeparator()
        helpmenu.Append(ContactID, "&Contact"," Contact the developer.")
        helpmenu.Append(wx.ID_ABOUT, "&About"," Information about this program")
        self.Bind(wx.EVT_MENU, self.open_file, id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.Help, id=help_ID)
        self.Bind(wx.EVT_MENU, self.Contact, id=ContactID)
        self.Bind(wx.EVT_MENU, self.ABOUT, id=wx.ID_ABOUT)
        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
        menuBar.Append(helpmenu,"&Help")
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.
        p = platform.system()
        if p == "Windows":
            iconImage = os.path.join("Resources","IconTiny.png")
        else:
            iconImage = os.path.join("Resources","Icon.png")
        image = wx.Image(iconImage, wx.BITMAP_TYPE_PNG).ConvertToBitmap() 
        icon = wx.EmptyIcon() 
        icon.CopyFromBitmap(image) 
        self.SetIcon(icon)
        
        Globals.INI = ConfigParser.ConfigParser()
        ini = os.path.join("PokeRoms.ini") #self.path,
        Globals.INI.read(ini)
        pub.subscribe(self.EXIT, "CloseG3HS")
        pub.subscribe(self.ReloadRom, "ReloadRom")
        self.panel.Layout()
        self.Layout()
        self.Show(True)
    
    def EXIT(self, data=None):
        wx.CallAfter(self.Destroy)
        wx.CallAfter(sys.exit)

    def Contact(self, event):
        emailer = ContactDialog(self)
        if emailer.ShowModal() == wx.ID_OK:
            if emailer.Entry.GetValue() == "":
                ERROR = wx.MessageDialog(None, 
                        "Message was not be sent because there was no message.", 
                        'Send Error', 
                        wx.OK | wx.ICON_ERROR)
                ERROR.ShowModal()
                return
            try: emailer.Send()
            except: 
                ERROR = wx.MessageDialog(None, 
                        "Message could not be sent.", 
                        'Connection Error', 
                        wx.OK | wx.ICON_ERROR)
                ERROR.ShowModal()
                return
            Finally = wx.MessageDialog(None, 
                        "Message sent successfully. Thank you and have a great day.\n\nThe exact message that was sent was:\n------------------\n"+emailer.Report+"\n------------------", 
                        'Message Sent!', 
                        wx.OK | wx.ICON_INFORMATION)
            Finally.ShowModal()
    
    def Help(self, event):
        try:
            import subprocess
            docs = os.path.join(os.getcwd(),"G3HS_Documentation.pdf")
            if sys.platform == 'linux2':
                subprocess.call(["xdg-open", docs])
            elif sys.platform.startswith('darwin'):
                subprocess.call(["open", docs])
            else:
                os.startfile(docs)
        except:
            ERROR = wx.MessageDialog(self, 
                            "G3HS_Documentation.pdf could not be opened in {0}. Please make sure the file exists.".format(os.getcwd()), 
                            'Documentation Error', 
                            wx.OK | wx.ICON_ERROR)
            ERROR.ShowModal()
        
        
    def OnDropFiles(self, x, y, filenames):
        filename = filenames[0]
        p = platform.system()
        self.open_rom = open(filename, "r+b")
        Globals.OpenRomName = filename
        pathfile = open("LastOpenedRom.txt", "w+")
        pathfile.write(filename+"\n"+p+"\n")
        pathfile.close()
        self.work_with_ini()
            
    def on_timer(self, event):
        read = sys.stderr.getvalue()
        if read != "":
            print read
            sys.stderr.close()
            sys.stderr = StringIO()
            if "Permission denied" in read:
                error = read.split("\n")[-2]
                
                ERROR = wx.MessageDialog(None, 
                                    textwrap.fill("Hey, look, I gave it my best, but I was denied permission to access that file.  Check and make sure there aren't any crazy characters in the path, that it is not marked as 'read only', and that it is not open in another program.", 100)+"\n\nError:\n"+textwrap.fill(error, 100), 
                                    'Permission Denied', 
                                    wx.OK | wx.ICON_ERROR)
                ERROR.ShowModal()
                return
            ERROR = wx.MessageDialog(None, 
                                "ERROR:\n\n"+read, 
                                'Piped error from sys.stderr: PLEASE REPORT', 
                                wx.OK | wx.ICON_ERROR)
            ERROR.ShowModal()
            
            """
            ERROR = wx.MessageDialog(None, 
                                "ERROR:\n\n"+read+"\n\nWould you like to report this error?", 
                                'Piped error from sys.stderr: PLEASE REPORT', 
                                wx.YES_NO | wx.ICON_ERROR)
            if ERROR.ShowModal() == wx.ID_YES:
                try:
                    Finally = None
                    if "ConfigParser.NoOptionError" in read:
                        errors = read.split("\n")
                        sections = errors[-2].split("'")
                        missingoption = sections[1]
                        section = sections[3]
                        Finally = wx.MessageDialog(None, 
                                    textwrap.fill('This message does not need to be sent. The last line of that error simply means that the specified option was not found in the ini. Please correct this. In section "{0}", the option "{1}" is missing. This is required for loading.'.format(section,missingoption),100), 
                                    'I already know this error....', 
                                    wx.OK | wx.ICON_INFORMATION)
                        Finally.ShowModal()
                    if "ConfigParser.NoSectionError" in read:
                        errors = read.split("\n")
                        sections = errors[-2].split("'")
                        section = sections[1]
                        Finally = wx.MessageDialog(None, 
                                    textwrap.fill('This message does not need to be sent. The last line of that error simply means that the specified section was not found in the ini. Please correct this. This program attempted to load data for {0} which was loaded from 0xAC in your rom. It could not find this section.'.format(section),100), 
                                    'I already know this error....', 
                                    wx.OK | wx.ICON_INFORMATION)
                        Finally.ShowModal()
                    if "load_evos_into_list" in read and "IndexError: list index out of range" in read:
                        Finally = wx.MessageDialog(None, 
                                    textwrap.fill('This message does not need to be sent. This error occurs when a bad offset is loaded from the ini for the evolution table. It attempted to load data for an evolution type that does not exist. Please check your offset in the ini for "evolutiontable".',100), 
                                    'I already know this error....', 
                                    wx.OK | wx.ICON_INFORMATION)
                        Finally.ShowModal()
                    if "IndexError: list index out of range" in read and "get_move_data" in read:
                        Finally = wx.MessageDialog(None, 
                                    textwrap.fill('This message does not need to be sent. The only time this error happens is when a pointer for learned move data is not in the rom. Most commonly, this is solely due to the pointer being FFFFFF caused by repointing the move table and filling it with FF. So, in basic terms, you have the wrong learned moves offset in the ini. (Maybe you loaded this rom with the ini for an expanded rom or vice versa?)',110), 
                                    'I already know this error....', 
                                         wx.OK | wx.ICON_INFORMATION)
                        Finally.ShowModal()
                    if "load_stats_into_boxes" in read and "SetSelectedItem(): Inavlid item index" in read:
                        Finally = wx.MessageDialog(None, 
                                    textwrap.fill('This message does not need to be sent. This error occurs when loading an item number that is too high. 90% of the time, your rom is expanded and using a section of ini for the unexpanded rom, or vice versa. Please check your ini.',110), 
                                    'I already know this error....', 
                                    wx.OK | wx.ICON_INFORMATION)
                        Finally.ShowModal()
                    Recovery()
                    if Finally:
                        return
                except:
                    ERROR = wx.MessageDialog(None, 
                                "Error report could not be sent.", 
                                'Failed Error Report', 
                                wx.OK | wx.ICON_ERROR)
                    ERROR.ShowModal()
                    return
                emailer = EmailError(self, read, Globals.VersionNumber)
                if emailer.ShowModal() == wx.ID_OK:
                    try: emailer.SendCrashReport()
                    except: 
                        ERROR = wx.MessageDialog(None, 
                                "Report could not be sent.", 
                                'Connection Error', 
                                wx.OK | wx.ICON_ERROR)
                        ERROR.ShowModal()
                        return
                    Finally = wx.MessageDialog(None, 
                                "Report sent successfully. Thank you and have a great day.\n\nThe exact report that was sent was:\n------------------\n"+emailer.Report+"\n------------------", 
                                'Report Sent!', 
                                wx.OK | wx.ICON_INFORMATION)
                    Finally.ShowModal()"""
            #else:
            Recovery()
    
    def set_timer(self):
        TIMER_ID = 10  # pick a number
        self.timer = wx.Timer(self, TIMER_ID)  # message will be sent to the panel
        self.timer.Start(500)  # x500 milliseconds
        wx.EVT_TIMER(self, TIMER_ID, self.on_timer)  # call the on_timer function

    def ABOUT(self, *args):
        iconImage = os.path.join("Resources","Icon.png")
        image = wx.Image(iconImage, wx.BITMAP_TYPE_PNG).ConvertToBitmap() 
        icon = wx.EmptyIcon() 
        icon.CopyFromBitmap(image) 
        
        global description
        
        try:
            r = urllib2.Request('https://api.github.com/repos/thekaratekid552/Secret-Tool/releases')
            response = urllib2.urlopen(r)
            obj = response.read()
            obj = json.loads(obj)
            downloads = None
            for x in obj:
                if x["tag_name"] == Globals.VersionNumber:
                    downloads = 0
                    for asset in x['assets']: downloads += asset['download_count']
            if downloads != None:
                D = description + "\n\nThis version has been downloaded {0} times around the world.".format(downloads)
            else:
                D = description
        except:
            D = description
            
        info = wx.AboutDialogInfo()
        global licence
        name = 'POK\xe9MON Gen III Hacking Suite'
        name = encode_per_platform(name)
        info.SetName(name)
        info.SetIcon(icon)
        info.SetVersion(Globals.Version)
        info.SetDescription(D)
        info.SetCopyright('(C) 2014 karatekid552')
        info.SetArtists(["MrDollSteak"])
        info.SetWebSite('http://thekaratekid552.github.io/Secret-Tool/')
        info.SetLicence(licence)

        wx.AboutBox(info)
        
    def open_file(self, *args):
        p = platform.system()
        if self.open_rom:
            directory = os.path.dirname(self.open_rom.name)
        else:
            try:
                with open("LastOpenedRom.txt", "r+") as pathfile:
                    pathfile = open("LastOpenedRom.txt", "r+")
                    directory = os.path.dirname(pathfile.readline().rstrip("\n"))
                    plat = pathfile.readline().rstrip("\n")
                    if plat != p:
                        raise AttributeError("Path is for a different system.")
            except:
                directory = os.getcwd()
        open_dialog = wx.FileDialog(None, message="Open a rom...", 
                                    defaultDir=directory, 
                                    wildcard = "Rom files (*.gba,*.bin)|*.gba;*.bin|All files (*.*)|*.*",
                                    style=wx.FD_OPEN)
        if open_dialog.ShowModal() == wx.ID_OK:
            filename = open_dialog.GetPath()
            Globals.OpenRomName = filename
            self.open_rom = open(filename, "r+b")
            try:
                with open("LastOpenedRom.txt", "w+") as pathfile:
                    path = filename+"\n"+p+"\n"
                    pathfile.write(path)
            except: pass
            wx.CallAfter(open_dialog.Destroy)
            wx.CallAfter(self.work_with_ini)
            
    def ReloadRom(self, *args):
        self.open_rom = open(Globals.OpenRomName, "r+b")
        wx.CallAfter(self.work_with_ini)

    def work_with_ini(self):
        #Here we are going to check if the game has been opened before.
        #If yes, load it's custom ini. If no, create its ini.
        Globals.INI = ConfigParser.ConfigParser()
        ini = os.path.join("PokeRoms.ini") #self.path,
        Globals.INI.read(ini)
        self.open_rom.seek(0xAC)
        Globals.OpenRomGameCode = self.open_rom.read(4)
        if str(Globals.INI.get("ALL", "JustUseStandardIni")) == "True":
            Globals.OpenRomID = Globals.OpenRomGameCode
        
        else:
            rom_id_offset = int(Globals.INI.get("ALL", "OffsetThatContainsSecondRomID"),0)
            
            self.open_rom.seek(rom_id_offset) #Seek to last 2 bytes in rom
            Globals.OpenRomID = str(hexlify(self.open_rom.read(2))) 

            all_possible_rom_ids = Globals.INI.sections()
            
            if Globals.OpenRomID != "ffff":
                if Globals.OpenRomID not in all_possible_rom_ids:
                    ERROR = wx.MessageDialog(None,
                        "At rom offset %s there is an unknown rom id. This "\
                        "means that your rom has a number at the offset of the "\
                        "rom id that is not in the ini. Would you like to "\
                        "overwrite this number with a new one? Please note that "\
                        "this could result in data loss, if, for example, there "\
                        "was an image at that location causing this issue. If "\
                        "no, this program will close." % hex(rom_id_offset), 
                        'Error', 
                        wx.YES_NO | wx.ICON_ERROR)
                    
                    if ERROR.ShowModal() == wx.ID_YES:
                        self.open_rom.seek(rom_id_offset)
                        self.open_rom.write("\xff\xff")
                        self.work_with_ini()
                    else:
                        wx.CallAfter(ERROR.Destroy)
                        wx.CallAfter(self.Destroy)
                else:
                    game_code = Globals.OpenRomGameCode
                    ini_gamecode = Globals.INI.get(Globals.OpenRomID, "gamecode")
                    if ini_gamecode != game_code:
                        ERROR = wx.MessageDialog(None,
                            "The game code of this rom is {0} however its rom id, {1}, tells me that the I should load a section of ini with gamecode {2}. Logically, if these don't match, I will be trying to load from the wrong offsets. Would you like to continue loading? Click 'yes' if you know that the gamecode should be different since you changed it yourself. Click 'no' to reset the rom id and create a new ini section for this rom.".format(game_code,Globals.OpenRomID,ini_gamecode), 
                            'Error', 
                            wx.YES_NO | wx.ICON_ERROR)
                        code = ERROR.ShowModal()
                        if code == wx.ID_NO:
                            self.open_rom.seek(rom_id_offset)
                            self.open_rom.write("\xff\xff")
                            self.work_with_ini()
                        else:
                            wx.CallAfter(ERROR.Destroy)
            else:
                game_code = Globals.OpenRomGameCode
                if game_code not in all_possible_rom_ids:
                    ERROR = wx.MessageDialog(self,
                            "Section '{0}' was not found in the ini. How am I supposed to load data if I don't have it? This game code was loaded from 0xAC in your rom. Please check it.".format(game_code), 
                            'Error', 
                            wx.OK | wx.ICON_ERROR)
                    ERROR.ShowModal()
                    return
                self.open_rom.seek(rom_id_offset)
                x = "0000"
                y = None
                while y == None:
                    if x in all_possible_rom_ids:
                        x = str(int(x) + 1).zfill(4)
                        continue
                    else:
                        Globals.OpenRomID = x
                        #Write new rom_id to rom.
                        byte_rom_id = get_hex_from_string(Globals.OpenRomID)
                        self.open_rom.write(byte_rom_id)
                        
                        Globals.INI.add_section(Globals.OpenRomID)
                        options = Globals.INI.options(game_code)
                        tmp_ini = []
                        for opt in options:
                            tmp_ini.append((opt, Globals.INI.get(game_code, opt)))
                            
                        for opt, value in tmp_ini:
                            Globals.INI.set(Globals.OpenRomID, opt, value)
                            
                        with open(ini, "w") as PokeRomsIni:
                            Globals.INI.write(PokeRomsIni)
                        y = True
        self.open_rom.close()
        wx.CallAfter(self.reload_all_tabs)
        self.SetTitle("Gen III Hacking Suite"+" ~ "+Globals.INI.get(Globals.OpenRomID, "name")+" ~ "+self.open_rom.name)
        
    def reload_all_tabs(self):
        try: self.tabbed_area.Destroy()
        except: pass
        self.tabbed_area = TabbedEditorArea(self.panel) 
        self.tabbed_area.LoadHexEditor()
        
        self.sizer.Add(self.tabbed_area, 1, wx.ALL|wx.EXPAND, 5)
        self.panel.Layout()
        self.Layout()
        self.Show(True)
        self.Refresh()
        
#############################################################
#This class is what holds all of the main tabs.
#############################################################
class TabbedEditorArea(wx.Notebook):
    def __init__(self, parent):
        wx.Notebook.__init__(self, parent, id=wx.ID_ANY, style=wx.BK_DEFAULT)
        
        self.PokeDataTab = PokemonDataEditor(self)
        self.HexEditor = HexEditor(self)
        name = "POK\xe9MON Data Editor"
        name = encode_per_platform(name)
        self.AddPage(self.PokeDataTab, name)
        self.AddPage(self.HexEditor, "Hex Editor")
        
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.OnPageChanging)
        self.Layout()
		
    def OnPageChanged(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        event.Skip()

    def OnPageChanging(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        event.Skip()
    
    def LoadHexEditor(self):
        self.HexEditor.LoadFile(Globals.OpenRomName)
        
#############################################################
#This tab will allow editing of Pokemon Stats, moves, etc
#############################################################
class PokemonDataEditor(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        if 'frame' in globals():
            if frame.open_rom is not None:
                Globals.PokeNames = self.get_pokemon_names()
                nums = []
                for x in range(len(Globals.PokeNames)):
                    nums.append(hex(x).rstrip("L"))
                self.Nums = wx.ComboBox(self, -1, choices=nums, 
                                value="0x0",
                                style=wx.SUNKEN_BORDER|wx.TE_PROCESS_ENTER,
                                pos=(0, 0), size=(80, -1))
                self.Nums.Bind(wx.EVT_COMBOBOX, self.on_change_num)
                self.Nums.Bind(wx.EVT_TEXT_ENTER, self.ChangeNumOnEnter)
                
                self.Pokes = wx.ComboBox(self, -1, choices=Globals.PokeNames, 
                                value=Globals.PokeNames[0],
                                style=wx.SUNKEN_BORDER|wx.TE_PROCESS_ENTER,
                                pos=(0, 0), size=(150, -1))
                self.Pokes.Bind(wx.EVT_COMBOBOX, self.on_change_poke)
                self.Pokes.Bind(wx.EVT_CHAR, self.EvtChar)
                self.Pokes.Bind(wx.EVT_TEXT_ENTER, self.SearchOnEnter)
                self.Pokes.Bind(wx.EVT_TEXT, self.SearchWhileTyping)
                self.ignoreEvtText = False
                
                global poke_num
                poke_num = 0
                
                self.Poke_Name = wx.TextCtrl(self, -1,style=wx.TE_CENTRE, size=(150,-1))
                self.Poke_Name.SetValue(Globals.PokeNames[0])
                
                savetab = Button(self, 3, "Save Tab")
                self.Bind(wx.EVT_BUTTON, self.OnSaveTab, id=3)
                
                save = Button(self, 1, "Save All")
                self.Bind(wx.EVT_BUTTON, self.OnSave, id=1)
                self.sizer = wx.BoxSizer(wx.VERTICAL)
                self.sizer_top = wx.BoxSizer(wx.HORIZONTAL)
                
                self.sizer_top.Add(self.Nums, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
                self.sizer_top.Add(self.Pokes, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
                self.sizer_top.Add(self.Poke_Name, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
                self.sizer_top.Add(savetab, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
                self.sizer_top.Add(save, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
                
                gamecode = Globals.INI.get(Globals.OpenRomID, "gamecode")
                if gamecode == "BPRE":
                    if len(Globals.PokeNames) == 0x19C:
                        ExpandPokesTxt = "Expand POK\xe9MON"
                        ExpandPokesTxt = encode_per_platform(ExpandPokesTxt)
                        ExpandPokes = Button(self, 2, ExpandPokesTxt)
                        self.Bind(wx.EVT_BUTTON, self.OnExpandPokes, id=2)
                        self.sizer_top.Add(ExpandPokes, 0, 
                                           wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
                
                self.sizer.Add(self.sizer_top, 0, wx.ALL, 2)
                self.tabbed_area = DataEditingTabs(self)
                
                self.sizer.Add(self.tabbed_area, 1, wx.ALL|wx.EXPAND, 2)
                self.SetSizer(self.sizer)
        else:
            self.sizer = wx.BoxSizer(wx.VERTICAL)
            open = Button(self, 100, "Open Rom")
            self.Bind(wx.EVT_BUTTON, self.OnOpen, id=100)
            self.sizer.Add(open, 1, wx.EXPAND|wx.ALL, 200)
            self.SetSizer(self.sizer)
        self.Layout()
    
    def on_change_num(self, *args):
        currentNum = self.Nums.GetSelection()
        wx.CallAfter(self.Pokes.SetSelection,currentNum)
        wx.CallAfter(self.on_change_poke)
    
    def ChangeNumOnEnter(self, *args):
        index = self.Nums.FindString(self.Nums.GetValue())
        if index != -1:
            self.Nums.SetSelection(index)
        else:
            index = self.Nums.FindString(self.Nums.GetValue().upper())
            if index != -1:
                self.Nums.SetSelection(index)
            else:
                index = self.Nums.FindString(self.Nums.GetValue().lower())
                if index != -1:
                    self.Nums.SetSelection(index)
                else: return
        self.on_change_num()
    
    def OnSaveTab(self, event):
        current = self.tabbed_area.GetSelection()
        currentobj = self.tabbed_area.GetPage(current)
        currentobj.save()
        self.GetParent().HexEditor.LoadFile(Globals.OpenRomName)
    
    def EvtChar(self, event):
        if event.GetKeyCode() == 8:
            self.ignoreEvtText = True
        event.Skip()
        
    def SearchWhileTyping(self, event=None):
        if self.ignoreEvtText:
            self.ignoreEvtText = False
            return
        currentText = self.Pokes.GetValue()
        MarkRange = self.Pokes.GetMark()
        if MarkRange == (0,0): currentType = currentText
        else: currentType = currentText[:MarkRange[0]+1]
        items = self.Pokes.GetItems()
        if self.Pokes.FindString(currentType) != -1:
            index = self.Pokes.FindString(currentType)
            wx.CallAfter(self.Pokes.SetSelection,index)
            wx.CallAfter(self.Pokes.SetInsertionPoint,len(currentType))
            return
        Matches = []
        for item in items:
            if item.startswith(currentText) or item.upper().startswith(currentText.upper()) or item.lower().startswith(currentText.lower()):
                Matches.append(item)
        if Matches != []:
            shortestmatch = min(Matches, key=len)
            index = self.Pokes.FindString(shortestmatch)
            wx.CallAfter(self.Pokes.SetSelection,index)
            wx.CallAfter(self.Pokes.SetInsertionPoint,len(currentText))
            wx.CallAfter(self.Pokes.SetMark,len(currentText),len(shortestmatch))
        if event is not None:
            event.Skip()
            
    def SearchOnEnter(self, event=None):
        index = self.Pokes.FindString(self.Pokes.GetValue())
        if index != -1:
            self.Pokes.SetSelection(index)
        else:
            index = self.Pokes.FindString(self.Pokes.GetValue().upper())
            if index != -1:
                self.Pokes.SetSelection(index)
            else:
                index = self.Pokes.FindString(self.Pokes.GetValue().lower())
                if index != -1:
                    self.Pokes.SetSelection(index)
                else: return
        cmd = wx.CommandEvent(wx.EVT_COMBOBOX.evtType[0])
        cmd.SetEventObject(self.Pokes) 
        cmd.SetId(self.Pokes.GetId())
        self.Pokes.GetEventHandler().ProcessEvent(cmd) 
        if event is not None:
            event.Skip()
            
    def OnOpen(self, instance):
        frame.open_file()
        
    def OnExpandPokes(self, instance):
        Expander = PokemonExpander(Globals.OpenRomName)
        if Expander.ShowModal() == wx.ID_OK:
            if Expander.offset and Expander.NewNumOfPokes != 0:
                RepointPokes(Globals.OpenRomName, 
                                        Expander.NewNumOfPokes,
                                        Expander.NewNumOfDexEntries,
                                        Expander.RAM_offset,
                                        Expander.offset,
                                        Globals.OpenRomID,
                                        Globals.INI)
                wx.CallAfter(frame.reload_all_tabs)
            else:
                ERROR = wx.MessageDialog(None, 
                                "You failed to provide either an offset for repointing or a new number of 'MONs. Please try again.", 
                                'Data Error', 
                                wx.OK | wx.ICON_ERROR)
                ERROR.ShowModal()
    
    def get_pokemon_names(self):
        offset = int(Globals.INI.get(Globals.OpenRomID, "PokeNames"),0)
        with open(Globals.OpenRomName, "r+b") as rom:
            rom.seek(offset, 0)
            number = int(Globals.INI.get(Globals.OpenRomID, "NumberofPokes"), 0)
            name_length = int(Globals.INI.get(Globals.OpenRomID, "PokeNamesLength"), 0)
            names = [] 
            for num in range(number):
                tmp_name = rom.read(name_length)
                tmp_name = convert_ascii_and_poke(tmp_name, "to_poke")
                name = tmp_name.split("\\xFF", 1)
                names.append(name[0])
            return names
    
    def on_change_poke(self, *args):
        global poke_num
        tmp_num = self.Pokes.GetSelection()
        autosavepokeswhenswitching = Globals.INI.get("ALL", "autosavepokeswhenswitching")
        if autosavepokeswhenswitching == "True":
            self.OnSave()
        poke_num = tmp_num
        self.Poke_Name.SetValue(Globals.PokeNames[poke_num])
        self.Nums.SetSelection(tmp_num)
        self.tabbed_area.reload_tab_data()
        
    def OnSave(self, *args):
        gamecode = Globals.INI.get(Globals.OpenRomID, "gamecode")
        self.tabbed_area.stats.save()
        self.save_new_poke_name()
        Globals.PokeNames = self.get_pokemon_names()
        self.tabbed_area.evo.poke.Clear()
        self.tabbed_area.evo.poke.AppendItems(Globals.PokeNames)
        self.Pokes.Clear()
        self.Pokes.SetItems(Globals.PokeNames)
        global poke_num
        self.Pokes.SetSelection(poke_num)
        self.tabbed_area.moves.save()
        self.tabbed_area.egg_moves.save()
        self.tabbed_area.evo.save()
        if gamecode[:3] == "AXV" or gamecode[:3] == "AXP":  pass
        else:  self.tabbed_area.tutor.save()
        self.tabbed_area.dex.save()
        self.tabbed_area.sprites.save()
        if gamecode[:3] != "BPR": pass
        else: self.tabbed_area.habitats.save()
        self.GetParent().HexEditor.LoadFile(Globals.OpenRomName)
        
    def save_new_poke_name(self):
        name = self.Poke_Name.GetValue()
        name = convert_ascii_and_poke(name, "to_ascii")
        name += "\xff"
        max_length = int(Globals.INI.get(Globals.OpenRomID, "PokeNamesLength"), 0)
        need = max_length-len(name)
        if need < 0:
            m = max_length - 1
            name = name[:m]+"\xff"
            need = 0
        for n in range(need):
            name += "\x00"
        global poke_num
        offset = int(Globals.INI.get(Globals.OpenRomID, "PokeNames"),0)
        offset = max_length*poke_num + offset
        with open(Globals.OpenRomName, "r+b") as rom:
            rom.seek(offset,0)
            rom.write(name)
        
class DataEditingTabs(wx.Notebook):
    def __init__(self, parent):
        wx.Notebook.__init__(self, parent, id=wx.ID_ANY, style=wx.BK_DEFAULT)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.stats = StatsTab(self)
        self.moves = MovesTab(self)
        self.evo = EvoTab(self)
        self.dex = PokeDexTab(self)
        gamecode = Globals.INI.get(Globals.OpenRomID, "gamecode")
        if gamecode[:3] == "AXV" or gamecode[:3] == "AXP":  pass
        else:  self.tutor = MoveTutorTab(self)
        self.egg_moves = EggMoveTab(self)
        
        self.sprites = SpriteTab(self, rom=Globals.OpenRomName, 
                                 config=Globals.INI, rom_id=Globals.OpenRomID)
        
        if gamecode[:3] != "BPR": pass
        else: self.habitats = HABITAT(self)
        self.AddPage(self.stats, "Stats")
        self.AddPage(self.moves, "Moves")
        self.AddPage(self.evo, "Evolutions")
        dex_name = "POK\xe9Dex"
        dex_name = encode_per_platform(dex_name)
        self.AddPage(self.dex, dex_name)
        
        if gamecode[:3] == "AXV" or gamecode[:3] == "AXP":  pass
        else:   self.AddPage(self.tutor, "Move Tutor")
        self.AddPage(self.egg_moves, "Egg Moves")
        self.AddPage(self.sprites, "Sprites")
        if gamecode[:3] != "BPR": pass
        else:  self.AddPage(self.habitats, "Habitats")
        
        self.SetSizer(sizer)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.OnPageChanging)
        self.Layout()
		
    def OnPageChanged(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        event.Skip()

    def OnPageChanging(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        event.Skip()
        
    def reload_tab_data(self):
        self.stats.reload_stuff()
        self.moves.load_everything()
        self.evo.load_everything()
        self.dex.LoadEverything()
        gamecode = Globals.INI.get(Globals.OpenRomID, "gamecode")
        if gamecode[:3] == "AXV" or gamecode[:3] == "AXP":  pass
        else: self.tutor.load_everything()
        global poke_num
        self.sprites.load_everything(poke_num=poke_num)
        
class StatsTab(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.sizer = wx.GridBagSizer(3,3)
        self.base_stats_dict = {}
        self.generate_ui()
        
        self.SetSizer(self.sizer)
        self.Layout()
        
    def reload_stuff(self):
        basestatsoffset = int(Globals.INI.get(Globals.OpenRomID, "pokebasestats"), 0)
        basestatslength = int(Globals.INI.get(Globals.OpenRomID, "pokebasestatslength"), 0)
        global poke_num
        self.basestatsoffset = basestatslength*(poke_num) + basestatsoffset
        with open(Globals.OpenRomName, "r+b") as rom:
            rom.seek(self.basestatsoffset, 0)
            self.base_stats_dict = {}
            self.basestats = rom.read(basestatslength)
            self.sort_base_stats()
            self.load_stats_into_boxes()

    def generate_ui(self):
        #----------Set up a panel for the regular stats.----------#
        basic_stats = wx.Panel(self, -1, style=wx.RAISED_BORDER|wx.TAB_TRAVERSAL)
        basic_stats_sizer = wx.GridBagSizer(3,3)
        
        basic_stats_txt = wx.StaticText(basic_stats, -1,"Base Stats:")
        basic_stats_sizer.Add(basic_stats_txt, (0, 0), wx.DefaultSpan,  wx.ALL, 4)
        
        self.Total_txt = wx.StaticText(basic_stats, -1,"Total: XXX")
        basic_stats_sizer.Add(self.Total_txt, (0, 1),wx.DefaultSpan,  wx.ALL, 4)
        
        HP_txt = wx.StaticText(basic_stats, -1,"HP:")
        basic_stats_sizer.Add(HP_txt, (1, 0), wx.DefaultSpan,  wx.ALL, 6)
        self.HP = wx.TextCtrl(basic_stats, -1,style=wx.TE_CENTRE, size=(40,-1))
        self.HP.Bind(wx.EVT_TEXT, self.update_BST)
        basic_stats_sizer.Add(self.HP,(1, 1), wx.DefaultSpan,  wx.ALL, 4)
        
        ATK_txt = wx.StaticText(basic_stats, -1,"ATK:")
        basic_stats_sizer.Add(ATK_txt, (2, 0), wx.DefaultSpan,  wx.ALL, 6)
        self.ATK = wx.TextCtrl(basic_stats, -1,style=wx.TE_CENTRE, size=(40,-1))
        self.ATK.Bind(wx.EVT_TEXT, self.update_BST)
        basic_stats_sizer.Add(self.ATK,(2, 1), wx.DefaultSpan,  wx.ALL, 4)
        
        DEF_txt = wx.StaticText(basic_stats, -1,"DEF:")
        basic_stats_sizer.Add(DEF_txt, (3, 0), wx.DefaultSpan,  wx.ALL, 6)
        self.DEF = wx.TextCtrl(basic_stats, -1,style=wx.TE_CENTRE, size=(40,-1))
        self.DEF.Bind(wx.EVT_TEXT, self.update_BST)
        basic_stats_sizer.Add(self.DEF,(3, 1), wx.DefaultSpan,  wx.ALL, 4)
        
        SpATK_txt = wx.StaticText(basic_stats, -1,"Sp. ATK:")
        basic_stats_sizer.Add(SpATK_txt, (4, 0), wx.DefaultSpan,  wx.ALL, 6)
        self.SpATK = wx.TextCtrl(basic_stats, -1,style=wx.TE_CENTRE, size=(40,-1))
        self.SpATK.Bind(wx.EVT_TEXT, self.update_BST)
        basic_stats_sizer.Add(self.SpATK,(4, 1), wx.DefaultSpan,  wx.ALL, 4)
        
        SpDEF_txt = wx.StaticText(basic_stats, -1,"Sp. DEF:")
        basic_stats_sizer.Add(SpDEF_txt, (5, 0), wx.DefaultSpan,  wx.ALL, 6)
        self.SpDEF = wx.TextCtrl(basic_stats, -1,style=wx.TE_CENTRE, size=(40,-1))
        self.SpDEF.Bind(wx.EVT_TEXT, self.update_BST)
        basic_stats_sizer.Add(self.SpDEF,(5, 1), wx.DefaultSpan,  wx.ALL, 4)
        
        SPD_txt = wx.StaticText(basic_stats, -1,"SPD:")
        basic_stats_sizer.Add(SPD_txt, (6, 0), wx.DefaultSpan,  wx.ALL, 6)
        self.SPD = wx.TextCtrl(basic_stats, -1,style=wx.TE_CENTRE, size=(40,-1))
        self.SPD.Bind(wx.EVT_TEXT, self.update_BST)
        basic_stats_sizer.Add(self.SPD,(6, 1), wx.DefaultSpan,  wx.ALL, 4)
        
        basic_stats_sizer.SetFlexibleDirection(wx.BOTH)
        
        basic_stats.SetSizerAndFit(basic_stats_sizer)
        
         #----------Set up a panel for EVs----------#
        evs = wx.Panel(self, -1, style=wx.RAISED_BORDER|wx.TAB_TRAVERSAL)
        evs_sizer = wx.GridBagSizer(3,3)
        
        e_txt = wx.StaticText(evs, -1,"Effort Values:")
        evs_sizer.Add(e_txt, (0, 0), (1,2), wx.EXPAND, 5)
        
        e_HP_txt = wx.StaticText(evs, -1,"HP:")
        evs_sizer.Add(e_HP_txt, (1, 0), wx.DefaultSpan,  wx.ALL, 6)
        self.e_HP = wx.TextCtrl(evs, -1,style=wx.TE_CENTRE, size=(40,-1))
        evs_sizer.Add(self.e_HP,(1, 1), wx.DefaultSpan,  wx.ALL, 4)
        
        e_ATK_txt = wx.StaticText(evs, -1,"ATK:")
        evs_sizer.Add(e_ATK_txt, (2, 0), wx.DefaultSpan,  wx.ALL, 6)
        self.e_ATK = wx.TextCtrl(evs, -1,style=wx.TE_CENTRE, size=(40,-1))
        evs_sizer.Add(self.e_ATK,(2, 1), wx.DefaultSpan,  wx.ALL, 4)
        
        e_DEF_txt = wx.StaticText(evs, -1,"DEF:")
        evs_sizer.Add(e_DEF_txt, (3, 0), wx.DefaultSpan,  wx.ALL, 6)
        self.e_DEF = wx.TextCtrl(evs, -1,style=wx.TE_CENTRE, size=(40,-1))
        evs_sizer.Add(self.e_DEF,(3, 1), wx.DefaultSpan,  wx.ALL, 4)
        
        e_SpATK_txt = wx.StaticText(evs, -1,"Sp. ATK:")
        evs_sizer.Add(e_SpATK_txt, (4, 0), wx.DefaultSpan,  wx.ALL, 6)
        self.e_SpATK = wx.TextCtrl(evs, -1,style=wx.TE_CENTRE, size=(40,-1))
        evs_sizer.Add(self.e_SpATK,(4, 1), wx.DefaultSpan,  wx.ALL, 4)
        
        e_SpDEF_txt = wx.StaticText(evs, -1,"Sp. DEF:")
        evs_sizer.Add(e_SpDEF_txt, (5, 0), wx.DefaultSpan,  wx.ALL, 6)
        self.e_SpDEF = wx.TextCtrl(evs, -1,style=wx.TE_CENTRE, size=(40,-1))
        evs_sizer.Add(self.e_SpDEF,(5, 1), wx.DefaultSpan,  wx.ALL, 4)
        
        e_SPD_txt = wx.StaticText(evs, -1,"SPD:")
        evs_sizer.Add(e_SPD_txt, (6, 0), wx.DefaultSpan,  wx.ALL, 6)
        self.e_SPD = wx.TextCtrl(evs, -1,style=wx.TE_CENTRE, size=(40,-1))
        evs_sizer.Add(self.e_SPD,(6, 1), wx.DefaultSpan,  wx.ALL, 4)
        
        evs.SetSizerAndFit(evs_sizer)
        
        
        #----------Panel for Gender, Hatch Speed, Friendship, Level-up speed, and egg groups----------#
        assorted = wx.Panel(self, -1, style=wx.RAISED_BORDER|wx.TAB_TRAVERSAL)
        assorted_sizer = wx.GridBagSizer(3,3)
        
        GENDER_txt = wx.StaticText(assorted, -1,"Gender Ratio:")
        assorted_sizer.Add(GENDER_txt, (0, 0), wx.DefaultSpan,  wx.ALL, 6)
        self.GENDER = wx.TextCtrl(assorted, -1,style=wx.TE_CENTRE, size=(40,-1))
        self.gender_label = wx.StaticText(assorted, -1,"100.0% Female")
        gender_sizer = wx.BoxSizer(wx.HORIZONTAL)
        gender_sizer.Add(self.GENDER, 0, wx.ALL|wx.EXPAND, 0)
        gender_sizer.Add(self.gender_label, 0, wx.LEFT|wx.EXPAND, 3)
        assorted_sizer.Add(gender_sizer, (0, 1), wx.DefaultSpan,  wx.ALL, 4)
        
        self.GENDER.Bind(wx.EVT_TEXT, self.update_gender_ratio)
        
        HATCH_txt = wx.StaticText(assorted, -1,"Hatch Speed:")
        assorted_sizer.Add(HATCH_txt, (1, 0), wx.DefaultSpan,  wx.ALL, 6)
        self.HATCH = wx.TextCtrl(assorted, -1,style=wx.TE_CENTRE, size=(40,-1))
        self.HATCH_label = wx.StaticText(assorted, -1,"65280 Steps")
        HATCH_sizer = wx.BoxSizer(wx.HORIZONTAL)
        HATCH_sizer.Add(self.HATCH, 0, wx.ALL|wx.EXPAND, 0)
        HATCH_sizer.Add(self.HATCH_label, 0, wx.LEFT|wx.EXPAND, 3)
        assorted_sizer.Add(HATCH_sizer, (1, 1), wx.DefaultSpan,  wx.ALL, 4)
        
        self.HATCH.Bind(wx.EVT_TEXT, self.update_HATCH_steps)
        
        FRIEND_txt = wx.StaticText(assorted, -1,"Base Friendship:")
        assorted_sizer.Add(FRIEND_txt, (2, 0), wx.DefaultSpan,  wx.ALL, 6)
        self.FRIEND = wx.TextCtrl(assorted, -1,style=wx.TE_CENTRE, size=(40,-1))
        assorted_sizer.Add(self.FRIEND, (2, 1), wx.DefaultSpan,  wx.ALL, 4)
        
        level_up_tmp = Globals.INI.get(Globals.OpenRomID, "LevelUpTypes")
        level_up_list = level_up_tmp.split(",")
        LEVEL_txt = wx.StaticText(assorted, -1,"Level-Up Rate:")
        assorted_sizer.Add(LEVEL_txt, (3, 0), wx.DefaultSpan,  wx.ALL, 4)
        self.LEVEL = ComboBox(assorted, -1, choices=level_up_list,
                                style=wx.SUNKEN_BORDER, size=(100, -1))
        assorted_sizer.Add(self.LEVEL, (3, 1), wx.DefaultSpan,  wx.ALL, 4)
        
        egg_tmp = Globals.INI.get(Globals.OpenRomID, "EggGroups")
        egg_groups = egg_tmp.split(",")
        
        EGG1_txt = wx.StaticText(assorted, -1,"Egg Group 1:")
        assorted_sizer.Add(EGG1_txt, (4, 0), wx.DefaultSpan,  wx.ALL, 4)
        self.EGG1 = ComboBox(assorted, -1, choices=egg_groups,
                                style=wx.SUNKEN_BORDER, size=(100, -1))
        assorted_sizer.Add(self.EGG1, (4, 1), wx.DefaultSpan,  wx.ALL, 4)
        
        EGG2_txt = wx.StaticText(assorted, -1,"Egg Group 2:")
        assorted_sizer.Add(EGG2_txt, (5, 0), wx.DefaultSpan,  wx.ALL, 4)
        self.EGG2 = ComboBox(assorted, -1, choices=egg_groups,
                                style=wx.SUNKEN_BORDER, size=(100, -1))
        assorted_sizer.Add(self.EGG2, (5, 1), wx.DefaultSpan,  wx.ALL, 4)
        
        assorted.SetSizerAndFit(assorted_sizer)

        #---------Set up a panel for Types----------#
        types = wx.Panel(self, -1, style=wx.RAISED_BORDER|wx.TAB_TRAVERSAL)
        types_sizer = wx.GridBagSizer(3,3)
        
        #Get list of types:
        t_offset = int(Globals.INI.get(Globals.OpenRomID, "TypeNames"), 0)
        t_name_length = int(Globals.INI.get(Globals.OpenRomID, "TypeNamesLength"), 0)
        t_number = int(Globals.INI.get(Globals.OpenRomID, "NumberofTypes"), 0)
        list_of_types = []
        
        with open(Globals.OpenRomName, "r+b") as rom:
            rom.seek(t_offset, 0)
            for n in range(t_number):
                temp_type = rom.read(t_name_length)
                temp_type = convert_ascii_and_poke(temp_type, "to_poke")
                temp_type = temp_type.split("\\xFF")
                list_of_types.append(temp_type[0])
        
        TYPE1_txt = wx.StaticText(types, -1,"Type 1:")
        types_sizer.Add(TYPE1_txt, (0, 0), wx.DefaultSpan,  wx.ALL, 4)
        self.TYPE1 = ComboBox(types, -1, choices=list_of_types,
                                style=wx.SUNKEN_BORDER, size=(80, -1))
        types_sizer.Add(self.TYPE1, (0, 1), wx.DefaultSpan,  wx.ALL, 4)
        
        TYPE2_txt = wx.StaticText(types, -1,"Type 2:")
        types_sizer.Add(TYPE2_txt, (1, 0), wx.DefaultSpan,  wx.ALL, 4)
        self.TYPE2 = ComboBox(types, -1, choices=list_of_types,
                                style=wx.SUNKEN_BORDER, size=(80, -1))
        types_sizer.Add(self.TYPE2, (1, 1), wx.DefaultSpan,  wx.ALL, 4)
        
        types.SetSizerAndFit(types_sizer)
        
        #----------Panel for Abilities----------#
        abilities = wx.Panel(self, -1, style=wx.RAISED_BORDER|wx.TAB_TRAVERSAL)
        abilities_sizer = wx.GridBagSizer(3,3)
        
        abil_offset = int(Globals.INI.get(Globals.OpenRomID, "Abilities"), 0)
        abil_num = int(Globals.INI.get(Globals.OpenRomID, "NumberofAbilities"), 0)
        abil_len = int(Globals.INI.get(Globals.OpenRomID, "AbiltiesNameLength"), 0)
        
        with open(Globals.OpenRomName, "r+b") as rom:
            abilities_list = generate_list_of_names(abil_offset, abil_len, 
                                                                    "\xff", abil_num, rom)
        
        ABILITY1_txt = wx.StaticText(abilities, -1,"Ability 1:")
        abilities_sizer.Add(ABILITY1_txt, (0, 0), wx.DefaultSpan,  wx.ALL, 4)
        self.ABILITY1 = ComboBox(abilities, -1, choices=abilities_list,
                                style=wx.SUNKEN_BORDER, size=(150, -1))
        abilities_sizer.Add(self.ABILITY1, (0, 1), wx.DefaultSpan,  wx.ALL, 4)
        
        ABILITY2_txt = wx.StaticText(abilities, -1,"Ability 2:")
        abilities_sizer.Add(ABILITY2_txt, (1, 0), wx.DefaultSpan,  wx.ALL, 4)
        self.ABILITY2 = ComboBox(abilities, -1, choices=abilities_list,
                                style=wx.SUNKEN_BORDER, size=(150, -1))
        abilities_sizer.Add(self.ABILITY2, (1, 1), wx.DefaultSpan,  wx.ALL, 4)
        
        abilities.SetSizerAndFit(abilities_sizer)
        
        #----------Panel for items----------#
        items = wx.Panel(self, -1, style=wx.RAISED_BORDER|wx.TAB_TRAVERSAL)
        items_sizer = wx.GridBagSizer(3,3)
        
        items_offset = int(Globals.INI.get(Globals.OpenRomID, "Items"), 16)
        number_of_items = int(Globals.INI.get(Globals.OpenRomID, "NumberofItems"), 16)
        item_data_len = int(Globals.INI.get(Globals.OpenRomID, "ItemsDataLength"), 16)
        
        with open(Globals.OpenRomName, "r+b") as rom:
            items_list = generate_list_of_names(items_offset, item_data_len,"\xff", number_of_items, rom)
            
        global ITEM_NAMES
        ITEM_NAMES = items_list
        ITEM1_txt = wx.StaticText(items, -1,"Item 1:")
        items_sizer.Add(ITEM1_txt, (0, 0), wx.DefaultSpan,  wx.ALL, 4)
        self.ITEM1 = ComboBox(items, -1, choices=items_list,
                                 style=wx.SUNKEN_BORDER, size=(160, -1))
        items_sizer.Add(self.ITEM1, (0, 1), wx.DefaultSpan,  wx.ALL, 4)
        
        ITEM2_txt = wx.StaticText(items, -1,"Item 2:")
        items_sizer.Add(ITEM2_txt, (1, 0), wx.DefaultSpan,  wx.ALL, 4)
        self.ITEM2 = ComboBox(items, -1, choices=items_list,
                                style=wx.SUNKEN_BORDER, size=(160, -1))
        items_sizer.Add(self.ITEM2, (1, 1), wx.DefaultSpan,  wx.ALL, 4)
        
        items.SetSizerAndFit(items_sizer)
        
        #----------Set up a panel for Catch Rate and Base EXP----------#
        catch_rate_base_exp = wx.Panel(self, -1, style=wx.RAISED_BORDER|wx.TAB_TRAVERSAL)
        catch_rate_base_exp_sizer = wx.GridBagSizer(3,3)
        
        CATCHRATE_txt = wx.StaticText(catch_rate_base_exp, -1,"Catch Rate:")
        catch_rate_base_exp_sizer.Add(CATCHRATE_txt, (0, 0), wx.DefaultSpan,  wx.ALL, 6)
        self.CATCHRATE = wx.TextCtrl(catch_rate_base_exp, -1,style=wx.TE_CENTRE, size=(40,-1))
        catch_rate_base_exp_sizer.Add(self.CATCHRATE,(0, 1), wx.DefaultSpan,  wx.ALL, 4)
        
        BASEEXP_txt = wx.StaticText(catch_rate_base_exp, -1,"Base Exp:")
        catch_rate_base_exp_sizer.Add(BASEEXP_txt, (1, 0), wx.DefaultSpan,  wx.ALL, 6)
        self.BASEEXP = wx.TextCtrl(catch_rate_base_exp, -1,style=wx.TE_CENTRE, size=(40,-1))
        catch_rate_base_exp_sizer.Add(self.BASEEXP,(1, 1), wx.DefaultSpan,  wx.ALL, 4)
        
        catch_rate_base_exp.SetSizerAndFit(catch_rate_base_exp_sizer)
        
        #----------Panel for Run Rate and Color----------#
        run_rate_color = wx.Panel(self, -1, style=wx.RAISED_BORDER|wx.TAB_TRAVERSAL)
        run_rate_color_sizer = wx.GridBagSizer(3,3)

        RUNRATE_txt = wx.StaticText(run_rate_color, -1,"Run Rate:")
        run_rate_color_sizer.Add(RUNRATE_txt, (0, 0), wx.DefaultSpan,  wx.ALL, 6)
        self.RUNRATE = wx.TextCtrl(run_rate_color, -1,style=wx.TE_CENTRE, size=(40,-1))
        run_rate_color_sizer.Add(self.RUNRATE, (0, 1), wx.DefaultSpan,  wx.ALL, 4)
        
        colors_list = ["Red","Blue","Yellow","Green","Black",
                            "Brown","Purple","Gray","White","Pink"]

        COLOR_txt = wx.StaticText(run_rate_color, -1,"Color:")
        run_rate_color_sizer.Add(COLOR_txt, (1, 0), wx.DefaultSpan,  wx.ALL, 4)
        self.COLOR = ComboBox(run_rate_color, -1, choices=colors_list,
                                style=wx.SUNKEN_BORDER, size=(90, -1))
        run_rate_color_sizer.Add(self.COLOR, (1, 1), wx.DefaultSpan,  wx.ALL, 4)
        
        run_rate_color.SetSizerAndFit(run_rate_color_sizer)
        
        #----------Add everything to the SIZER----------#
        boxa = wx.BoxSizer(wx.HORIZONTAL)
        boxb = wx.BoxSizer(wx.HORIZONTAL)
        boxc = wx.BoxSizer(wx.HORIZONTAL)
        
        boxa.Add(basic_stats, 0, wx.ALL|wx.EXPAND, 5)
        boxa.Add(evs, 0, wx.ALL|wx.EXPAND, 5)
        boxa.Add(assorted, 0, wx.ALL|wx.EXPAND, 5)
        boxb.Add(types, 0, wx.ALL|wx.EXPAND, 5)
        boxb.Add(abilities, 0, wx.ALL|wx.EXPAND, 5)
        boxb.Add(items, 0, wx.ALL|wx.EXPAND, 5)
        boxc.Add(catch_rate_base_exp,  0, wx.ALL|wx.EXPAND, 5)
        boxc.Add(run_rate_color, 0, wx.ALL|wx.EXPAND, 5)
        
        self.sizer.Add(boxa, (0,0), wx.DefaultSpan,  wx.ALL, 0)
        self.sizer.Add(boxb, (1,0), wx.DefaultSpan,  wx.ALL, 0)
        self.sizer.Add(boxc, (2,0), wx.DefaultSpan,  wx.ALL, 0)

        #---------- ----------#
        self.reload_stuff()
        self.load_stats_into_boxes()
    
    def update_BST(self, instance):
        try:
            total = 0
            total += int(self.HP.GetValue(), 0)
            total += int(self.ATK.GetValue(), 0)
            total += int(self.DEF.GetValue(), 0)
            total += int(self.SPD.GetValue(), 0)
            total += int(self.SpATK.GetValue(), 0)
            total += int(self.SpDEF.GetValue(), 0)
            self.Total_txt.SetLabel("Total: "+str(total))
        
        except:
            self.Total_txt.SetLabel("BST: ???")
    
    def update_HATCH_steps(self, *args):
        txt = self.HATCH.GetValue()
        try: 
            if int(txt, 0) >= 255: self.HATCH_label.SetLabel("65025 Steps")
            elif int(txt, 0) == 0: self.HATCH_label.SetLabel("Instant")
            else:
                ratio = (int(txt, 0)+1)*255
                self.HATCH_label.SetLabel(str(ratio)+" Steps")
        except:
            self.HATCH_label.SetLabel("Bad Number")
        
    def update_gender_ratio(self, *args):
        txt = self.GENDER.GetValue()
        try: 
            if int(txt, 0) >= 255: self.gender_label.SetLabel("Genderless")
            elif int(txt, 0) == 254: self.gender_label.SetLabel("100% Female")
            else:
                ratio = (int(txt, 0)/256)*100
                self.gender_label.SetLabel("{0:.1f}% Female".format(ratio))
        except:
            self.gender_label.SetLabel("Bad Number")
            
    def load_stats_into_boxes(self):
        d = self.base_stats_dict
        self.HP.SetValue(str(d["HP"]))
        self.ATK.SetValue(str(d["ATK"]))
        self.DEF.SetValue(str(d["DEF"]))
        self.SPD.SetValue(str(d["SPD"]))
        self.SpATK.SetValue(str(d["SAT"]))
        self.SpDEF.SetValue(str(d["SDE"]))
        
        self.TYPE1.SetSelection(d["TYPE1"])
        self.TYPE2.SetSelection(d["TYPE2"])
        
        self.CATCHRATE.SetValue(str(d["CATCHRATE"]))
        self.BASEEXP.SetValue(str(d["BASEEXP"]))
        
        self.e_HP.SetValue(str(d["EVS"][3]))
        self.e_ATK.SetValue(str(d["EVS"][2]))
        self.e_DEF.SetValue(str(d["EVS"][1]))
        self.e_SPD.SetValue(str(d["EVS"][0]))
        self.e_SpATK.SetValue(str(d["EVS"][7]))
        self.e_SpDEF.SetValue(str(d["EVS"][6]))
        
        self.ITEM1.SetSelection(d["ITEM1"])
        self.ITEM2.SetSelection(d["ITEM2"])
        
        self.GENDER.SetValue(str(d["GENDER"]))
        self.HATCH.SetValue(str(d["HATCHINGSTEPS"]))
        self.FRIEND.SetValue(str(d["FRIENDSHIP"]))
        self.LEVEL.SetSelection(d["LEVELUPTYPE"])
        self.EGG1.SetSelection(d["EGGGROUP1"]-1)
        self.EGG2.SetSelection(d["EGGGROUP2"]-1)
        
        self.ABILITY1.SetSelection(d["ABILITY1"])
        self.ABILITY2.SetSelection(d["ABILITY2"])
        
        self.RUNRATE.SetValue(str(d["RUNRATE"]))
        self.COLOR.SetSelection(d["COLOR"])
        
    def create_string_of_hex_values_to_be_written(self):
        try:
            HP = hex(int(self.HP.GetValue(), 0))[2:].zfill(2)
            if len(HP) > 2:
                HP = "FF"
                
            ATK = hex(int(self.ATK.GetValue(), 0))[2:].zfill(2)
            if len(ATK) > 2:
                ATK = "FF"
                
            DEF = hex(int(self.DEF.GetValue(), 0))[2:].zfill(2)
            if len(DEF) > 2:
                DEF = "FF"
                 
            SPD = hex(int(self.SPD.GetValue(), 0))[2:].zfill(2)
            if len(SPD) > 2:
                SPD = "FF"
                 
            SpATK = hex(int(self.SpATK.GetValue(), 0))[2:].zfill(2)
            if len(SpATK) > 2:
                SpATK = "FF"
                 
            SpDEF = hex(int(self.SpDEF.GetValue(), 0))[2:].zfill(2)
            if len(SpDEF) > 2:
                SpDEF = "FF"
            
            tmp = self.TYPE1.GetSelection()
            if tmp == -1:
                tmp = 1
            TYPE1 = hex(int(tmp))[2:].zfill(2)
            
            tmp = self.TYPE2.GetSelection()
            if tmp == -1:
                tmp = 1
            TYPE2 = hex(int(tmp))[2:].zfill(2)
            
            CATCHRATE = hex(int(self.CATCHRATE.GetValue(), 0))[2:].zfill(2)
            if len(CATCHRATE) > 2:
                CATCHRATE = "FF"
                
            BASEEXP = hex(int(self.BASEEXP.GetValue(), 0))[2:].zfill(2)
            if len(BASEEXP) > 2:
                BASEEXP = "FF"
                
            evs_list = [str(self.e_SPD.GetValue()), str(self.e_DEF.GetValue()),
                            str(self.e_ATK.GetValue()), str(self.e_HP.GetValue()),
                            "0","0",str(self.e_SpDEF.GetValue()),str(self.e_SpATK.GetValue())]
            evs_bin = ""
            for i, value in enumerate(evs_list):
                if i == 4:
                    evs_bin = evs_bin+"00"
                elif i == 5:
                    evs_bin = evs_bin+"00"
                else:
                    if int(value, 0) > 3:
                        value = "3"
                    elif value == "":
                        value = "0"
                    ev = bin(int(value, 0))[2:].zfill(2)
                    evs_bin = evs_bin+ev
            evs_hex = hex(int(evs_bin, 2))[2:].zfill(4)
            
            tmp = self.ITEM1.GetSelection()
            if tmp == -1:
                tmp = 1
            ITEM1 = hex(int(tmp))[2:].zfill(4)
            
            ITEM1 = ITEM1[2:]+ITEM1[:2] #Flip the bytes around.

            tmp = self.ITEM2.GetSelection()
            if tmp == -1:
                tmp = 1
            ITEM2 = hex(int(tmp))[2:].zfill(4)
            
            ITEM2 = ITEM2[2:]+ITEM2[:2] #Flip the bytes around.
            
            GENDER = hex(int(self.GENDER.GetValue(), 0))[2:].zfill(2)
            if len(GENDER) > 2:
                GENDER = "FF"
                
            HATCH = hex(int(self.HATCH.GetValue(), 0))[2:].zfill(2)
            if len(HATCH) > 2:
                HATCH = "FF"
                
            FRIEND = hex(int(self.FRIEND.GetValue(), 0))[2:].zfill(2)
            if len(FRIEND) > 2:
                FRIEND = "FF"
            
            tmp = self.LEVEL.GetSelection()
            if tmp == -1:
                tmp = 1
            LEVEL = hex(int(tmp))[2:].zfill(2)        
            
            tmp = self.EGG1.GetSelection()
            if tmp == -1:
                tmp = 1
            EGG1 = hex(int(tmp)+1)[2:].zfill(2)
            
            tmp = self.EGG2.GetSelection()
            if tmp == -1:
                tmp = 1
            EGG2 = hex(int(tmp)+1)[2:].zfill(2)
            
            tmp = self.ABILITY1.GetSelection()
            if tmp == -1:
                tmp = 1
            ABILITY1 = hex(int(tmp))[2:].zfill(2)
            
            tmp = self.ABILITY2.GetSelection()
            if tmp == -1:
                tmp = 1
            ABILITY2 = hex(int(tmp))[2:].zfill(2)
                
            RUNRATE = hex(int(self.RUNRATE.GetValue(), 0))[2:].zfill(2)
            if len(RUNRATE) > 2:
                RUNRATE = "FF"
            
            tmp = self.COLOR.GetSelection()
            if tmp == -1:
                tmp = 1
            COLOR = hex(int(tmp))[2:].zfill(2)
                
            #Create a string off all of the stats to be written to the rom.
            base = HP+ATK+DEF+SPD+SpATK+SpDEF
            types = TYPE1+TYPE2
            rate_exp = CATCHRATE+BASEEXP
            evs = evs_hex
            items = ITEM1+ITEM2
            assort = GENDER+HATCH+FRIEND+LEVEL+EGG1+EGG2
            abilities = ABILITY1+ABILITY2
            runrate_color = RUNRATE+COLOR
            
            
            stats = base+types+rate_exp+evs+items+assort+abilities+runrate_color+"0000"
            return stats
            
        except:
            ERROR = wx.MessageDialog(None, 
                                'One of your entries contains in the stats tab contains bad data. No stats have been saved.', 
                                'Data Error', 
                                wx.OK | wx.ICON_ERROR)
            ERROR.ShowModal()
            return False
        
    def sort_base_stats(self):
        d = self.base_stats_dict
        s = self.basestats
        d["HP"] = int(get_bytes_string_from_hex_string(s[0]),16)
        d["ATK"] = int(get_bytes_string_from_hex_string(s[1]),16)
        d["DEF"] = int(get_bytes_string_from_hex_string(s[2]),16)
        d["SPD"] = int(get_bytes_string_from_hex_string(s[3]),16)
        d["SAT"] = int(get_bytes_string_from_hex_string(s[4]),16)
        d["SDE"] = int(get_bytes_string_from_hex_string(s[5]),16)
        d["TYPE1"] = int(get_bytes_string_from_hex_string(s[6]),16)
        d["TYPE2"] = int(get_bytes_string_from_hex_string(s[7]),16)
        d["CATCHRATE"] = int(get_bytes_string_from_hex_string(s[8]),16)
        d["BASEEXP"] = int(get_bytes_string_from_hex_string(s[9]),16)
        #Deal with EV bits:
        evs = get_bytes_string_from_hex_string(s[10]+s[11])
        scale = 16 ## equals to hexadecimal
        num_of_bits = 16
        evs = bin(int(evs, scale))[2:].zfill(num_of_bits)
        evs_list = split_string_into_bytes(evs)
        evs_list_ints = []
        for ev in evs_list:
            ev = int(ev,2)
            evs_list_ints.append(ev)
        d["EVS"] = evs_list_ints
        #Done with evs....
        d["ITEM1"] = int(get_bytes_string_from_hex_string(s[13]+s[12]),16)
        d["ITEM2"] = int(get_bytes_string_from_hex_string(s[15]+s[14]),16)
        d["GENDER"] = int(get_bytes_string_from_hex_string(s[16]),16)
        d["HATCHINGSTEPS"] = int(get_bytes_string_from_hex_string(s[17]),16)
        d["FRIENDSHIP"] = int(get_bytes_string_from_hex_string(s[18]),16)
        d["LEVELUPTYPE"] = int(get_bytes_string_from_hex_string(s[19]),16)
        d["EGGGROUP1"] = int(get_bytes_string_from_hex_string(s[20]),16)
        d["EGGGROUP2"] = int(get_bytes_string_from_hex_string(s[21]),16)
        d["ABILITY1"] = int(get_bytes_string_from_hex_string(s[22]),16)
        d["ABILITY2"] = int(get_bytes_string_from_hex_string(s[23]),16)
        d["RUNRATE"] = int(get_bytes_string_from_hex_string(s[24]),16)
        d["COLOR"] = int(get_bytes_string_from_hex_string(s[25]),16)
        
        self.base_stats_dict = d
        
    def save(self):
        string = self.create_string_of_hex_values_to_be_written()
        if not string: return
        with open(Globals.OpenRomName, "r+b") as rom:
            rom.seek(self.basestatsoffset, 0)
            string = unhexlify(string)
            rom.write(string)
        
class MovesTab(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.sizer = wx.GridBagSizer(3,3)
        self.generate_ui()
        self.SetSizer(self.sizer)

        self.Layout()
        
    def generate_ui(self):
        moves_offset = int(Globals.INI.get(Globals.OpenRomID, "AttackNames"), 0)
        moves_length = int(Globals.INI.get(Globals.OpenRomID, "AttackNameLength"), 0)
        moves_num = int(Globals.INI.get(Globals.OpenRomID, "NumberofAttacks"), 0)
        
        with open(Globals.OpenRomName, "r+b") as rom:
            self.MOVES_LIST = generate_list_of_names(moves_offset, moves_length, 
                                                                             "\xff", moves_num, rom)
        global MOVES_LIST
        MOVES_LIST = self.MOVES_LIST
        #----Create a panel for Learned Moves----#
        learned_moves = wx.Panel(self, -1, style=wx.RAISED_BORDER|wx.TAB_TRAVERSAL)
        learned_moves_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        v_lm_box = wx.BoxSizer(wx.VERTICAL)
        v_lm_box_buttons = wx.BoxSizer(wx.VERTICAL)
        
        learned_moves_txt = wx.StaticText(learned_moves, -1, "Learned Moves:")
        v_lm_box.Add(learned_moves_txt, 0, wx.EXPAND | wx.LEFT | wx.TOP, 2)
        
        self.MOVESET = wx.ListCtrl(learned_moves, -1, style=wx.LC_REPORT, size=(230,350))
        self.MOVESET.InsertColumn(0, 'Attack', width=140)
        self.MOVESET.InsertColumn(1, 'Level', width=40)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnSelectMove,  self.MOVESET)
        v_lm_box.Add(self.MOVESET, wx.EXPAND | wx.ALL, 2)
        
        editing_box = wx.BoxSizer(wx.HORIZONTAL)

        
        self.ATTACK = ComboBox(learned_moves, -1, choices=self.MOVES_LIST,
                                style=wx.SUNKEN_BORDER, size=(100, -1))
        editing_box.Add(self.ATTACK, 0, wx.EXPAND | wx.ALL, 2)
        
        self.LEVEL = wx.TextCtrl(learned_moves, -1,style=wx.TE_CENTRE, size=(40,-1))
        editing_box.Add(self.LEVEL, 0, wx.EXPAND | wx.ALL, 2)
        
        SET = Button(learned_moves, 8, "Replace")
        self.Bind(wx.EVT_BUTTON, self.OnChangeMove, id=8)
        editing_box.Add(SET, 0, wx.EXPAND | wx.ALL, 2)
        
        v_lm_box.Add(editing_box, 0, wx.EXPAND | wx.ALL, 2)
        
        self.FRACTION = wx.StaticText(learned_moves, -1, "XX/XX Moves")
        v_lm_box_buttons.Add(self.FRACTION, 0, wx.EXPAND | wx.ALL, 5)
        
        self.LEARNED_OFFSET = wx.StaticText(learned_moves, -1, "0xXXXXXX")
        v_lm_box_buttons.Add(self.LEARNED_OFFSET, 0, wx.EXPAND | wx.ALL, 5)
        
        REPOINT = Button(learned_moves, 1, "Repoint")
        self.Bind(wx.EVT_BUTTON, self.OnRepoint, id=1)
        v_lm_box_buttons.Add(REPOINT, 0, wx.EXPAND | wx.ALL, 5)

        ADD = Button(learned_moves, 2, "Add")
        self.Bind(wx.EVT_BUTTON, self.OnAdd, id=2)
        v_lm_box_buttons.Add(ADD, 0, wx.EXPAND | wx.ALL, 5)
        
        DELETE = Button(learned_moves, 3, "Delete")
        self.Bind(wx.EVT_BUTTON, self.OnDelete, id=3)
        v_lm_box_buttons.Add(DELETE, 0, wx.EXPAND | wx.ALL, 5)
        
        MOVE_UP = Button(learned_moves, 4, "Move Up")
        self.Bind(wx.EVT_BUTTON, self.OnMoveUp, id=4)
        v_lm_box_buttons.Add(MOVE_UP, 0, wx.EXPAND | wx.ALL, 5)
        
        MOVE_DOWN = Button(learned_moves, 5, "Move Down")
        self.Bind(wx.EVT_BUTTON, self.OnMoveDown, id=5)
        v_lm_box_buttons.Add(MOVE_DOWN, 0, wx.EXPAND | wx.ALL, 5)
        
        learned_moves_sizer.Add(v_lm_box, 0, wx.EXPAND | wx.ALL, 5)
        learned_moves_sizer.Add(v_lm_box_buttons, 0, wx.EXPAND | wx.ALL, 5)
        learned_moves.SetSizerAndFit(learned_moves_sizer)
        
        #----TMsHMs----#
        TMHMPanel = wx.Panel(self, -1, style=wx.RAISED_BORDER|wx.TAB_TRAVERSAL)
        TMHMBIGBOX = wx.BoxSizer()
        TMBox = wx.BoxSizer(wx.VERTICAL)
        ButtonBox = wx.BoxSizer(wx.VERTICAL)
        TMHMBIGBOX.Add(TMBox)
        TMHMBIGBOX.Add(ButtonBox)
        self.TMList = CheckListCtrl(TMHMPanel, size=(230,280))
        self.TMList.InsertColumn(0, 'TM #', width=140)
        self.TMList.InsertColumn(1, 'Move')
        TMBox.Add(self.TMList, 0, wx.EXPAND | wx.ALL, 5)
        
        self.HMList = CheckListCtrl(TMHMPanel, size=(230,105))
        self.HMList.InsertColumn(0, 'HM #', width=140)
        self.HMList.InsertColumn(1, 'Move')
        TMBox.Add(self.HMList, 0, wx.EXPAND | wx.ALL, 5)
        
        SELECTALL = Button(TMHMPanel, 6, "Select All")
        self.Bind(wx.EVT_BUTTON, self.OnSelectAllTMHMs, id=6)
        ButtonBox.Add(SELECTALL, 0, wx.EXPAND | wx.ALL, 5)
        
        CLEAR = Button(TMHMPanel, 7, "Clear All")
        self.Bind(wx.EVT_BUTTON, self.OnClearAllTMHMs, id=7)
        ButtonBox.Add(CLEAR, 0, wx.EXPAND | wx.ALL, 5)
        
        TMHMPanel.SetSizerAndFit(TMHMBIGBOX)
        #----Add Everything to the Sizer----#
        self.sizer.Add(learned_moves, (0,0), wx.DefaultSpan, wx.ALL, 4)
        self.sizer.Add(TMHMPanel, (0,1), wx.DefaultSpan, wx.ALL, 4)
        self.load_everything()
        
    def save(self):
        ##Write new table
        with open(Globals.OpenRomName, "r+b") as rom:
            learned_offset = self.learned_moves_offset
            if self.NEW_LEARNED_OFFSET != None:
                learned_offset = int(self.NEW_LEARNED_OFFSET, 16)
            rom.seek(learned_offset)
            learned_moves = self.prepare_string_of_learned_moves()
            learned_moves = get_hex_from_string(learned_moves)
            if learned_moves != None: rom.write(learned_moves)
            else:
                sys.stderr.write("There was an issue saving learned moves. They have been skipped. Please try again. If this continues, restart the program.")
                sys.stderr.write("\n\nMove data dump:\n")
                for attack, level in self.learned_moves:
                    sys.stderr.write("#"+str(attack)+":"+self.MOVES_LIST[attack]+":"+str(level)+", ")
                return
            learnedmoveslength = int(Globals.INI.get(Globals.OpenRomID, "learnedmoveslength"), 0)
            
            ##Fill old table with free space
            if self.NEW_LEARNED_OFFSET != None:
                if self.overwrite == True:
                    fill = self.original_amount_of_moves*learnedmoveslength
                    original_offset = self.learned_moves_offset
                    rom.seek(original_offset)
                    for n in range(fill):
                        rom.write("\xff")
                    check = rom.read(4)
                    if check == "\xff\xff\xfe\xfe" or check == "\xff\xff\xff\xfe":
                        rom.seek(-4, 1)
                        rom.write("\xff\xff\xff\xff")
            
            ##Write TM & HM Data
            num = self.TMList.GetItemCount()
            binary = ""
            for i in range(num):
                if self.TMList.IsChecked(i): binary += "1"
                else: binary += "0"
            num = self.HMList.GetItemCount()
            for i in range(num):
                if self.HMList.IsChecked(i): binary += "1"
                else: binary += "0"
            check = len(binary)%32
            if check != 0:
                for n in range(32-check): 
                    binary += "0"
            hexTMHM = ""
            while True:
                word = binary[:32]
                word = word[::-1]
                word = int(word, 2)
                word = hex(word).rstrip("L").lstrip("0x").zfill(8)
                word = reverse_hex(word)
                word = get_hex_from_string(word)
                hexTMHM += word
                
                if len(binary) == 32:
                    break
                binary = binary[32:]
            rom.seek(self.TMHMoffset)
            rom.write(hexTMHM)
        
    def OnSelectMove(self, *args):
        self.UPDATE_FRACTION()
        sel = self.MOVESET.GetFocusedItem()
        
        self.LEVEL.SetValue(str(self.learned_moves[sel][1]))
        self.ATTACK.SetSelection(self.learned_moves[sel][0])
        
    def OnRepoint(self, *args):
        repoint = MOVE_REPOINTER(parent=None)
        repoint.ShowModal()
        Current = self.MOVESET.GetItemCount()
        if not self.NEW_NUMBER_OF_MOVES:
            return
        if Current > self.NEW_NUMBER_OF_MOVES:
            while Current > self.NEW_NUMBER_OF_MOVES:
                self.MOVESET.DeleteItem(Current-1)
                del self.learned_moves[Current-1]
                Current = self.MOVESET.GetItemCount()
        self.overwrite = repoint.cb.IsChecked()
        self.UPDATE_FRACTION()
        self.save()
        repoint.Destroy()
        
    def OnAdd(self, *args):
        self.UPDATE_FRACTION()
        move_len = len(self.learned_moves)
        if self.NEW_NUMBER_OF_MOVES == None:
            if self.original_amount_of_moves != move_len:
                if self.original_amount_of_moves > move_len:
                    self.AddNewMove()
            elif self.original_amount_of_moves == move_len:
                ERROR = wx.MessageDialog(None, 
                                'You must repoint or delete before adding a new entry.', 
                                'Data Error', 
                                wx.OK | wx.ICON_ERROR)
                ERROR.ShowModal()
        else:
            if self.NEW_NUMBER_OF_MOVES != move_len:
                if self.NEW_NUMBER_OF_MOVES > move_len:
                    self.AddNewMove()
            elif self.NEW_NUMBER_OF_MOVES == move_len:
                ERROR = wx.MessageDialog(None, 
                                'You must repoint or delete before adding a new entry.', 
                                'Data Error', 
                                wx.OK | wx.ICON_ERROR)
                ERROR.ShowModal()
        
    def OnDelete(self, *args):
        selection = self.MOVESET.GetFocusedItem()
        if selection != -1:
            self.MOVESET.DeleteItem(selection)
            del self.learned_moves[selection]
        self.UPDATE_FRACTION()
        
    def OnMoveUp(self, *args):
        selection = self.MOVESET.GetFocusedItem()
        if selection != -1 and selection != 0:
            self.learned_moves[selection], self.learned_moves[selection-1] = self.learned_moves[selection-1], self.learned_moves[selection]
            self.MOVESET.DeleteAllItems()
            for move, level in self.learned_moves:
                index = self.MOVESET.InsertStringItem(sys.maxint, self.MOVES_LIST[move])
                self.MOVESET.SetStringItem(index, 1, str(level))
            self.MOVESET.Select(selection-1)
            self.MOVESET.Focus(selection-1)
            
    def OnMoveDown(self, *args):
        selection = self.MOVESET.GetFocusedItem()
        length = len(self.learned_moves)-1
        if selection != -1 and selection != length:
            self.learned_moves[selection], self.learned_moves[selection+1] = self.learned_moves[selection+1], self.learned_moves[selection]
            self.MOVESET.DeleteAllItems()
            for move, level in self.learned_moves:
                index = self.MOVESET.InsertStringItem(sys.maxint, self.MOVES_LIST[move])
                self.MOVESET.SetStringItem(index, 1, str(level))
            self.MOVESET.Select(selection+1)
            self.MOVESET.Focus(selection+1)
            
    def OnChangeMove(self, *args):
        selection = self.MOVESET.GetFocusedItem()
        if selection != -1:
            try: level = int(self.LEVEL.GetValue(), 0)
            except: return
            attack = self.ATTACK.GetSelection()
            if attack == -1: return
            if level > 100: level = 100
            self.learned_moves[selection] = (attack, level)
            self.MOVESET.DeleteAllItems()
            for move, level in self.learned_moves:
                index = self.MOVESET.InsertStringItem(sys.maxint, self.MOVES_LIST[move])
                self.MOVESET.SetStringItem(index, 1, str(level))
            self.MOVESET.Select(selection)
            self.MOVESET.Focus(selection)
        
    def AddNewMove(self, *args):
        try: level = int(self.LEVEL.GetValue(), 0)
        except: level = ""
        attack = self.ATTACK.GetSelection()
        if attack == -1:
            index = self.MOVESET.InsertStringItem(sys.maxint, self.MOVES_LIST[1])
            attack = 1
        else:
            index = self.MOVESET.InsertStringItem(sys.maxint, self.MOVES_LIST[attack])
        if level == "":
            self.MOVESET.SetStringItem(index, 1, "1")
        else:
            if level > 100:
                level = 100
            self.MOVESET.SetStringItem(index, 1, str(level))
        if level == "":
            level = 1
        self.learned_moves.append((attack, level))
        self.UPDATE_FRACTION()
    
    def UPDATE_FRACTION(self):
        Current = str(self.MOVESET.GetItemCount())
        if self.NEW_NUMBER_OF_MOVES == None:
            MAX = str(self.original_amount_of_moves)
        else:
            MAX = str(self.NEW_NUMBER_OF_MOVES)
        
        self.FRACTION.SetLabel(Current+"/"+MAX+" Moves")
        
    def prepare_string_of_learned_moves(self):
        Jambo51HackCheck = Globals.INI.get(Globals.OpenRomID, "Jambo51LearnedMoveHack")
        string = ""
        if Jambo51HackCheck == "False":
            for attack, level in self.learned_moves:
                lvl = level
                atk = attack
                lvl *= 2
                if attack >= 256:
                    lvl += 1
                    atk = atk-256
                if atk > 255:
                    continue
                set = hex(atk)[2:].zfill(2)+hex(lvl)[2:].zfill(2)
                string += set
        else:
            for attack, level in self.learned_moves:
                lvl = hex(level)[2:]
                atk = hex(attack)[2:].zfill(4)
                atk = atk[2:]+atk[:2]
                set = atk+lvl
                string += set
        return string
    
    def load_everything(self): #Moves
        self.NEW_LEARNED_OFFSET = None
        self.NEW_NUMBER_OF_MOVES = None
        self.original_amount_of_moves = 0
        #Load learned move data:
        self.MOVESET.DeleteAllItems()
        self.learned_moves = self.get_move_data()
        for move, level in self.learned_moves:
            try:
                index = self.MOVESET.InsertStringItem(sys.maxint, self.MOVES_LIST[move])
                self.MOVESET.SetStringItem(index, 1, str(level))
            except:
                ERROR = wx.MessageDialog(None, 
                                    textwrap.fill("Moves have not been fully loaded because there was an error. Either not enough moves were loaded due to a bad number in the ini or the learned move data offset is bad/corrupted. The error occurred trying to read move #{0}. The current number of moves is: {1}.".format(move, len(self.MOVES_LIST)-1),100), 
                                    'Error', 
                                    wx.OK | wx.ICON_ERROR)
                ERROR.ShowModal()
                return
        self.LEARNED_OFFSET.SetLabel(hex(self.learned_moves_offset))
        
        self.UPDATE_FRACTION()
        
        self.getTMHMdata()
        self.LoadTMNames()
        global MOVES_LIST
        NumberofTMs = int(Globals.INI.get(Globals.OpenRomID, "NumberofTMs"), 0)
        self.TMList.DeleteAllItems()
        for num, TM in enumerate(self.TMNumbers):
            index = self.TMList.InsertStringItem(sys.maxint, "TM"+str(num+1))
            self.TMList.SetStringItem(index, 1, MOVES_LIST[TM])
            if self.TMHMCompatibility[num] == True:
                self.TMList.CheckItem(index) 
        self.HMList.DeleteAllItems()
        for num, HM in enumerate(self.HMNumbers):
            index = self.HMList.InsertStringItem(sys.maxint, "HM"+str(num+1))
            self.HMList.SetStringItem(index, 1, MOVES_LIST[HM])
            if self.TMHMCompatibility[num+NumberofTMs] == True:
                self.HMList.CheckItem(index)
        
        self.TMList.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.TMList.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        self.HMList.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.HMList.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        
    def get_move_data(self):
        self.learned_moves_pointer = int(Globals.INI.get(Globals.OpenRomID, "LearnedMoves"), 0)
        learned_moves_length = int(Globals.INI.get(Globals.OpenRomID, "LearnedMovesLength"), 0)
        
        Jambo51HackCheck = Globals.INI.get(Globals.OpenRomID, "Jambo51LearnedMoveHack")
        global poke_num
        self.learned_moves_pointer = (poke_num)*4+self.learned_moves_pointer
        with open(Globals.OpenRomName, "r+b") as rom:
            rom.seek(self.learned_moves_pointer, 0)
            self.learned_moves_offset = read_pointer(rom.read(4))
            rom.seek(self.learned_moves_offset, 0)
            learned_moves = []
            if Jambo51HackCheck == "False":
                while True:
                        last_read = rom.read(2)
                        if last_read != "\xff\xff" and last_read != "\x00\xff":
                            #moves will be a tupple of (move, level)
                            last_read = get_bytes_string_from_hex_string(last_read)
                            last_read = split_string_into_bytes(last_read)
                            if int(last_read[1],16)%2 == 0:
                                level = int(int(last_read[1], 16)/2)
                                move = int(last_read[0], 16)
                            else:
                                level = int((int(last_read[1], 16)-1)/2)
                                move = int(last_read[0],16)+256
                            learned_moves.append((move, level))
                        else:
                            break
            else:
                 while True:
                        last_read = rom.read(3)
                        last_read = get_bytes_string_from_hex_string(last_read)
                        last_read = split_string_into_bytes(last_read)
                        if last_read[2] != "FF":
                            #moves will be a tupple of (move, level)
                            move = int(last_read[1]+last_read[0], 16)
                            level = int(last_read[2], 16)
                            learned_moves.append((move, level))
                        else:
                            break
            self.original_amount_of_moves = len(learned_moves)
        return learned_moves
        
    def getTMHMdata(self):
        self.TMHMoffset = int(Globals.INI.get(Globals.OpenRomID, "TMHMCompatibility"), 0)
        length = int(Globals.INI.get(Globals.OpenRomID, "TMHMCompatibilityLength"), 0)
        global poke_num
        
        self.TMHMoffset += (poke_num)*length
        with open(Globals.OpenRomName, "r+b") as rom:
            rom.seek(self.TMHMoffset)
            read = rom.read(length)
        TMHM = ""
        while True:
            word = get_bytes_string_from_hex_string(read[:4])
            
            word = reverse_hex(word)
            word = int(word, 16)
            
            binary = bin(word)[2:].zfill(32)
            binary = binary[::-1]
            
            TMHM += binary
            
            if len(read) == 4:
                break
            read = read[4:]
        self.TMHMCompatibility = []
        for c in TMHM:
            if c == "0": self.TMHMCompatibility.append(False)
            else: self.TMHMCompatibility.append(True)
            
    def LoadTMNames(self):
        TMList = int(Globals.INI.get(Globals.OpenRomID, "TMList"), 0)
        TMListLength = int(Globals.INI.get(Globals.OpenRomID, "TMListEntryLength"), 0)
        NumberofTMs = int(Globals.INI.get(Globals.OpenRomID, "NumberofTMs"), 0)
        NumberofHMs = int(Globals.INI.get(Globals.OpenRomID, "NumberofHMs"), 0)
        with open(Globals.OpenRomName, "r+b") as rom:
            rom.seek(TMList)
            
            self.TMNumbers = []
            for n in range(NumberofTMs):
                read = rom.read(TMListLength)
                read = get_bytes_string_from_hex_string(read)
                read = read[2:]+read[:2]
                read = int(read, 16)
                
                self.TMNumbers.append(read)
            self.HMNumbers = []
            for n in range(NumberofHMs):
                read = rom.read(TMListLength)
                read = get_bytes_string_from_hex_string(read)
                read = read[2:]+read[:2]
                read = int(read, 16)
                
                self.HMNumbers.append(read)
            
    def OnSelectAllTMHMs(self, instance):
        num = self.TMList.GetItemCount()
        for n in range(num):
            self.TMList.CheckItem(n) 
        
        num = self.HMList.GetItemCount()
        for n in range(num):
            self.HMList.CheckItem(n)
    
    def OnClearAllTMHMs(self, instance):
        num = self.TMList.GetItemCount()
        for n in range(num):
            self.TMList.CheckItem(n, False) 
        
        num = self.HMList.GetItemCount()
        for n in range(num):
            self.HMList.CheckItem(n, False)
    
class EvoTab(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.arg_type = None
        self.generate_UI()
        self.Locations = self.get_locations()
        self.SetSizer(self.sizer)

    def generate_UI(self):
        EVO = wx.Panel(self, -1, style=wx.RAISED_BORDER|wx.TAB_TRAVERSAL)
        EVO_Sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        self.evo_list = wx.ListCtrl(EVO, -1, style=wx.LC_REPORT, size=(570,300))
        self.evo_list.InsertColumn(0, 'Method', width=150)
        self.evo_list.InsertColumn(1, 'Argument', width=150)
        self.evo_list.InsertColumn(2, 'Evolves into...', width=130)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnSelectEvo,  self.evo_list)
        vbox.Add(self.evo_list, 0, wx.EXPAND | wx.ALL, 5)
        
        editor_area = wx.BoxSizer(wx.HORIZONTAL)
        editor_area_a = wx.BoxSizer(wx.VERTICAL)
        editor_area_b = wx.BoxSizer(wx.VERTICAL)
        editor_area_c = wx.BoxSizer(wx.VERTICAL)
        editor_area.Add(editor_area_a, 0, wx.EXPAND | wx.ALL, 5)
        editor_area.Add(editor_area_b, 0, wx.EXPAND | wx.ALL, 5)
        editor_area.Add(editor_area_c, 0, wx.EXPAND | wx.ALL, 5)
        
        method_txt = wx.StaticText(EVO, -1, "Method:")
        editor_area_a.Add(method_txt, 0, wx.EXPAND | wx.ALL, 5)
        
        EvolutionMethods = Globals.INI.get(Globals.OpenRomID, "EvolutionMethods").split(",")
        self.method = wx.ComboBox(EVO, -1, choices=EvolutionMethods,
                                            style=wx.SUNKEN_BORDER, size=(100, -1))
        self.method.Bind(wx.EVT_COMBOBOX, self.change_method)
        editor_area_a.Add(self.method, 0, wx.EXPAND | wx.ALL, 5)
        
        self.arg_txt = wx.StaticText(EVO, -1, "Argument:")
        editor_area_b.Add(self.arg_txt, 0, wx.EXPAND | wx.ALL, 5)
        
        self.arg = ComboBox(EVO, -1, choices=[],
                                            style=wx.SUNKEN_BORDER, size=(100, -1))
        editor_area_b.Add(self.arg, 0, wx.EXPAND | wx.ALL, 5)
        
        poke_txt = wx.StaticText(EVO, -1, "Evolves Into:")
        editor_area_c.Add(poke_txt, 0, wx.EXPAND | wx.ALL, 5)
        
        self.poke = ComboBox(EVO, -1, choices=Globals.PokeNames,
                                               style=wx.SUNKEN_BORDER, size=(100, -1))
        editor_area_c.Add(self.poke, 0, wx.EXPAND | wx.ALL, 5)
        
        ReplaceEvo = Button(EVO, 3, "Replace Evolution")
        self.Bind(wx.EVT_BUTTON, self.OnReplaceEvo, id=3)
        editor_area.Add(ReplaceEvo, 0, wx.EXPAND | wx.ALL, 5)
        
        buttons = wx.BoxSizer(wx.VERTICAL)
        
        ChangeNumberofEvos = Button(EVO, 0, "Change Number of\nEvolutions per 'MON")
        self.Bind(wx.EVT_BUTTON, self.OnChangeNumberofEvos, id=0)
        buttons.Add(ChangeNumberofEvos, 0, wx.EXPAND | wx.ALL, 5)
        
        AddEvo = Button(EVO, 1, "Add Evolution")
        self.Bind(wx.EVT_BUTTON, self.OnAddEvo, id=1)
        buttons.Add(AddEvo, 0, wx.EXPAND | wx.ALL, 5)
        
        RemoveEvo = Button(EVO, 2, "Delete Evolution")
        self.Bind(wx.EVT_BUTTON, self.OnRemoveEvo, id=2)
        buttons.Add(RemoveEvo, 0, wx.EXPAND | wx.ALL, 5)
        
        MoveUp = Button(EVO, 4, "Move Up")
        self.Bind(wx.EVT_BUTTON, self.OnMoveUp, id=4)
        buttons.Add(MoveUp, 0, wx.EXPAND | wx.ALL, 5)
        
        MoveDown = Button(EVO, 5, "Move Down")
        self.Bind(wx.EVT_BUTTON, self.OnMoveDown, id=5)
        buttons.Add(MoveDown, 0, wx.EXPAND | wx.ALL, 5)
        
        vbox.Add(editor_area, 0, wx.EXPAND | wx.ALL, 5)
        
        EVO_Sizer.Add(vbox, 0, wx.EXPAND | wx.ALL, 5)
        EVO_Sizer.Add(buttons, 0, wx.EXPAND | wx.ALL, 5)
        EVO.SetSizer(EVO_Sizer)
        self.sizer.Add(EVO, 0, wx.EXPAND | wx.ALL, 5)
        self.load_everything()
        
    def OnChangeNumberofEvos(self, *args):
        NumberofEvosChanger()
        
    def OnAddEvo(self, *args):
        sel = self.evo_list.GetFocusedItem()
        if sel != -1:
            method = self.method.GetSelection()
            if method == -1:
                method = 0
            arg = self.arg.GetSelection()
            if self.evomethodsproperties[method] == "Level":
                arg += 1
            elif arg == -1:
                arg = 0
            elif self.evomethodsproperties[method] == "Location":
                arg += self.Locations[0]
            poke = self.poke.GetSelection()
            if poke == -1:
                poke = 1
            
            location = None
            for num, evo in enumerate(self.evos):
                if evo[0] == 0:
                    location = num
                    break
            if location == None:
                ERROR = wx.MessageDialog(None, 
                                    "Please increase the number of evolutions or delete an\nevolution before trying to add a new one.", 
                                    'Error', 
                                    wx.OK | wx.ICON_ERROR)
                ERROR.ShowModal()
                return
                
            self.evos[location] = [method,arg,poke]
            self.load_evos_into_list()
            
            self.evo_list.Select(location)
            self.evo_list.Focus(location)
    
    def OnRemoveEvo(self, *args):
        sel = self.evo_list.GetFocusedItem()
        if sel != -1:
            self.evos[sel] = [0,0,0]
            self.load_evos_into_list()
            self.evo_list.Select(sel)
            self.evo_list.Focus(sel)
                
    def OnMoveUp(self, *args):
        sel = self.evo_list.GetFocusedItem()
        if sel != -1 and sel != 0:
            self.evos[sel], self.evos[sel-1] = self.evos[sel-1], self.evos[sel]
            self.load_evos_into_list()
            self.evo_list.Select(sel-1)
            self.evo_list.Focus(sel-1)
            
    def OnMoveDown(self, *args):
        sel = self.evo_list.GetFocusedItem()
        max = len(self.evos)-1
        if sel != -1 and sel != max:
            self.evos[sel], self.evos[sel+1] = self.evos[sel+1], self.evos[sel]
            self.load_evos_into_list()
            self.evo_list.Select(sel+1)
            self.evo_list.Focus(sel+1)
            
    def OnReplaceEvo(self, *args):
        sel = self.evo_list.GetFocusedItem()
        if sel != -1:
            method = self.method.GetSelection()
            if method == -1:
                method = 0
            arg = self.arg.GetSelection()
            if self.evomethodsproperties[method] == "Level":
                arg += 1
            elif arg == -1:
                arg = 0
            elif self.evomethodsproperties[method] == "Location":
                arg += self.Locations[0]
            poke = self.poke.GetSelection()
            if poke == -1:
                poke = 1
                
            self.evos[sel] = [method,arg,poke]
            self.load_evos_into_list()
            self.evo_list.Select(sel)
            self.evo_list.Focus(sel)
        
    def OnSelectEvo(self, instance):
        sel = self.evo_list.GetFocusedItem()
        
        self.method.SetSelection(self.evos[sel][0])
        type = self.change_method(self.method)
        if self.evomethodsproperties[type] == "Level":
            self.arg.SetSelection(self.evos[sel][1]-1)
        elif self.evomethodsproperties[type] != None:
            self.arg.SetSelection(self.evos[sel][1])
        else:
            self.arg.SetSelection(0)
        self.poke.SetSelection(self.evos[sel][2])
        
    def change_method(self, instance):
        method = instance.GetSelection()
        if self.evomethodsproperties[method] == "Level": #Level type
            if self.arg_type != "Level":
                nums = []
                for n in range(101):
                    if n != 0:
                        nums.append(str(n))
                wx.CallAfter(self.arg.Clear)
                wx.CallAfter(self.arg.AppendItems,nums)
                wx.CallAfter(self.arg_txt.SetLabel,"Level:")
                self.arg.IgnoreEverything = True
                self.arg_type = "Level"
        elif self.evomethodsproperties[method] == "Item": #Item type
            if self.arg_type != "Item":
                global ITEM_NAMES
                wx.CallAfter(self.arg.Clear)
                wx.CallAfter(self.arg.AppendItems,ITEM_NAMES)
                wx.CallAfter(self.arg_txt.SetLabel,"Item:")
                self.arg_type = "Item"
                self.arg.IgnoreEverything = False
        elif self.evomethodsproperties[method] == "Pokemon": #Pokemon type
            if self.arg_type != "Pokemon":
                wx.CallAfter(self.arg.Clear)
                wx.CallAfter(self.arg.AppendItems,Globals.PokeNames)
                wx.CallAfter(self.arg_txt.SetLabel,"Pokemon")
                self.arg_type = "Pokemon"
                self.arg.IgnoreEverything = False
        elif self.evomethodsproperties[method] == "Move": #Move type
            if self.arg_type != "Move":
                global MOVES_LIST
                wx.CallAfter(self.arg.Clear)
                wx.CallAfter(self.arg.AppendItems,MOVES_LIST)
                wx.CallAfter(self.arg_txt.SetLabel,"Move")
                self.arg_type = "Move"
                self.arg.IgnoreEverything = False
        elif self.evomethodsproperties[method] == "Location": #Location type
            if self.arg_type != "Location":
                Locations_List = self.Locations[1]
                wx.CallAfter(self.arg.Clear)
                wx.CallAfter(self.arg.AppendItems,Locations_List)
                wx.CallAfter(self.arg_txt.SetLabel,"Location")
                self.arg_type = "Location"
                self.arg.IgnoreEverything = False
        else: #None type
            wx.CallAfter(self.arg.Clear)
            wx.CallAfter(self.arg.AppendItems,["-None needed-"])
            wx.CallAfter(self.arg_txt.SetLabel,"Argument:")
            self.arg.IgnoreEverything = False
            self.arg_type = None
        return method
    
    def get_locations(self):
        LocationTable = int(Globals.INI.get(Globals.OpenRomID, "locationnames"), 0)
        locationstart = int(Globals.INI.get(Globals.OpenRomID, "locationstart"), 0)
        locationend = int(Globals.INI.get(Globals.OpenRomID, "locationend"), 0)
        locationtblfmt = int(Globals.INI.get(Globals.OpenRomID, "locationtblfmt"), 0)
        lst = []
        with open(Globals.OpenRomName, "r+b") as rom:
            for x in range((locationend-locationstart)+1):
                rom.seek(LocationTable+x*4*locationtblfmt)
                offset = read_pointer(rom.read(4))
                rom.seek(offset)
                string = ""
                read = ""
                while read != "\xFF":
                    
                    read = rom.read(1)
                    string += read
                lst.append(convert_ascii_and_poke(string[:-1],"to_poke"))
        return (locationstart, lst)
                
    def load_everything(self):
        EvolutionTable = int(Globals.INI.get(Globals.OpenRomID, "EvolutionTable"), 0)
        EvolutionsPerPoke = int(Globals.INI.get(Globals.OpenRomID, "EvolutionsPerPoke"), 0)
        LengthOfOneEntry = int(Globals.INI.get(Globals.OpenRomID, "LengthOfOneEntry"), 0)
        EvolutionMethods = Globals.INI.get(Globals.OpenRomID, "EvolutionMethods").split(",")
        self.evomethodsproperties = Globals.INI.get(Globals.OpenRomID, "evomethodsproperties").split(",")
        global poke_num
        self.offset = EvolutionTable+(poke_num)*(LengthOfOneEntry*EvolutionsPerPoke)
        with open(Globals.OpenRomName, "r+b") as rom:
            rom.seek(self.offset, 0)
            raw = rom.read(LengthOfOneEntry*EvolutionsPerPoke)
        hexValues = get_bytes_string_from_hex_string(raw)
        self.evos = []
        list_of_entries = []
        for n in range(EvolutionsPerPoke):
            split = hexValues[:LengthOfOneEntry*2]
            list_of_entries.append(split)
            hexValues = hexValues[LengthOfOneEntry*2:]
        for num, entry in enumerate(list_of_entries):
            method = int(entry[:2],16)
            arg = int(entry[6:8]+entry[4:6],16)
            poke = int(entry[10:12]+entry[8:10],16)
            self.evos.append([method,arg,poke])
            self.load_evos_into_list()
            
    def load_evos_into_list(self):
        EvolutionMethods = Globals.INI.get(Globals.OpenRomID, "EvolutionMethods").split(",")
        global ITEM_NAMES
        global MOVES_LIST
        self.evo_list.DeleteAllItems()
        for opts in self.evos:
            if opts[0] == 0 and opts[2] == 0:
                index = self.evo_list.InsertStringItem(sys.maxint, "None")
                self.evo_list.SetStringItem(index, 1, "-")
                self.evo_list.SetStringItem(index, 2, "-")
            else:
                try: method = EvolutionMethods[opts[0]]
                except: 
                    method = EvolutionMethods[0]
                    opts[0] = 0
                    opts[1] = 0
                    opts[2] = 0
                    index = self.evo_list.InsertStringItem(sys.maxint, "None")
                    self.evo_list.SetStringItem(index, 1, "-")
                    self.evo_list.SetStringItem(index, 2, "-")
                    continue
                index = self.evo_list.InsertStringItem(sys.maxint, method)
                try: 
                    assettype = self.evomethodsproperties[opts[0]]
                    asset = opts[1]
                except: 
                    assettype = self.evomethodsproperties[0]
                    asset = 0
                    opts[0] = 0
                    opts[1] = 0
                    opts[2] = 0
                    index = self.evo_list.InsertStringItem(sys.maxint, "None")
                    self.evo_list.SetStringItem(index, 1, "-")
                    self.evo_list.SetStringItem(index, 2, "-")
                    continue
                if assettype == "Level":
                    need = "Level: "+str(asset)
                elif assettype == "Item":
                    need = "Item: "+ITEM_NAMES[asset]
                elif assettype == "Pokemon":
                    need = "Pokemon: "+Globals.PokeNames[asset]
                elif assettype == "Move":
                    need = "Move: "+MOVES_LIST[asset]
                elif assettype == "Location":
                    need = "Location: "+self.Locations[1][asset-self.Locations[0]]
                else:
                    need = "-"
                self.evo_list.SetStringItem(index, 1, need)
                self.evo_list.SetStringItem(index, 2, Globals.PokeNames[opts[2]])
            

    def save(self):
        hex_string = ""
        LengthOfOneEntry = int(Globals.INI.get(Globals.OpenRomID, "LengthOfOneEntry"), 0)
        for evo in self.evos:
            tmp = ""
            for arg in evo:
                x = hex(arg)[2:].zfill(4)
                x = reverse_hex(x)
                tmp += x
            while len(tmp) < LengthOfOneEntry*2:
                tmp += "00"
            hex_string += tmp
        write_string = get_hex_from_string(hex_string)
        with open(Globals.OpenRomName, "r+b") as rom:
            rom.seek(self.offset, 0)
            rom.write(write_string)
        
class PokeDexTab(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.lastPath = None
        self.OriginalEntry1Len = None
        self.OriginalEntry2Len = None
        
        self.GenerateUI()
        
        self.SetSizer(self.sizer)
        
    def GenerateUI(self):
        DEX = wx.Panel(self, -1, style=wx.RAISED_BORDER|wx.TAB_TRAVERSAL)
        MAIN = wx.BoxSizer(wx.HORIZONTAL)
        DEX.SetSizer(MAIN)
        
        DEX_Sizer = wx.BoxSizer(wx.VERTICAL)
        MAIN.Add(DEX_Sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        Type_txt = wx.StaticText(DEX, -1,"Type:")
        DEX_Sizer.Add(Type_txt, 0, wx.ALL, 5)
        self.Type = wx.TextCtrl(DEX, wx.ID_ANY, style=wx.TE_CENTRE, size=(100, -1))
        DEX_Sizer.Add(self.Type, 0, wx.ALL, 5)
        
        Entry1HBox = wx.BoxSizer(wx.HORIZONTAL)
        DEX_Sizer.Add(Entry1HBox, 0, wx.ALL, 0)
        Entry1_txt = wx.StaticText(DEX, -1,"Dex Entry Page 1:                      ")
        Entry1HBox.Add(Entry1_txt, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        RepointE1 = Button(DEX, 5, "Repoint")
        self.Bind(wx.EVT_BUTTON, self.OnRepointE1, id=RepointE1.Id)
        Entry1HBox.Add(RepointE1, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5)
        self.Entry1 = wx.TextCtrl(DEX, wx.ID_ANY, style=wx.TE_MULTILINE, size=(300,70))
        DEX_Sizer.Add(self.Entry1, 0, wx.ALL, 5)
        
        
        Entry2HBox = wx.BoxSizer(wx.HORIZONTAL)
        DEX_Sizer.Add(Entry2HBox, 0, wx.ALL, 0)
        Entry2_txt = wx.StaticText(DEX, -1,"Dex Entry Page 2:                      ")
        Entry2HBox.Add(Entry2_txt, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        self.RepointE2 = Button(DEX, 6, "Repoint")
        self.Bind(wx.EVT_BUTTON, self.OnRepointE2, id=self.RepointE2.Id)
        Entry2HBox.Add(self.RepointE2, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5)
        self.Entry2 = wx.TextCtrl(DEX, wx.ID_ANY, style=wx.TE_MULTILINE, size=(300,70))
        DEX_Sizer.Add(self.Entry2, 0, wx.ALL, 5)
        
        gamecode = Globals.INI.get(Globals.OpenRomID, "gamecode")
        if gamecode == "BPRE":
            self.FixNameBug = Button(DEX, 1, "Fix 'Dex Not Displaying Names Properly")
            self.Bind(wx.EVT_BUTTON, self.OnFixNameBug, id=1)
            DEX_Sizer.Add(self.FixNameBug, 1, wx.ALL|wx.ALIGN_TOP, 5)
        
        #Footprints
        FootHBox = wx.BoxSizer(wx.HORIZONTAL)
        DEX_Sizer.Add(FootHBox, 0, wx.ALL, 5)
        
        FootTxt = wx.StaticText(DEX, -1,"Footprint:")
        FootHBox.Add(FootTxt, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER, 5)
        
        self.FootPrint = wx.BitmapButton(DEX,3,wx.EmptyBitmap(64,64), size=(76,76))
        self.Bind(wx.EVT_BUTTON, self.OnFoot, id=self.FootPrint.Id)
        FootHBox.Add(self.FootPrint, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        
        RepointFeets = Button(DEX, 4, "Repoint Footprint")
        self.Bind(wx.EVT_BUTTON, self.OnRepointFeet, id=RepointFeets.Id)
        FootHBox.Add(RepointFeets, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        
        ##This is the Height and Weight Section
        
        vbox = wx.BoxSizer(wx.VERTICAL)
        MAIN.Add(vbox, 0, wx.EXPAND | wx.ALL, 5)
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        vbox.Add(hbox, 0, wx.EXPAND | wx.ALL, 5)
        
        HWbox = wx.BoxSizer(wx.VERTICAL)
        hbox.Add(HWbox, 0, wx.EXPAND | wx.ALL, 5)
        
        Height_txt = wx.StaticText(DEX, -1,"Height:")
        HWbox.Add(Height_txt, 0, wx.ALL, 5)
        self.Height = wx.TextCtrl(DEX, wx.ID_ANY, style=wx.TE_CENTRE, size=(50, -1))
        self.Height.Bind(wx.EVT_TEXT, self.ChangeHeight)
        HWbox.Add(self.Height, 0, wx.EXPAND | wx.ALL, 5)
        
        Weight_txt = wx.StaticText(DEX, -1,"Weight:")
        HWbox.Add(Weight_txt, 0, wx.ALL, 5)
        self.Weight = wx.TextCtrl(DEX, wx.ID_ANY, style=wx.TE_CENTRE, size=(50, -1))
        self.Weight.Bind(wx.EVT_TEXT, self.ChangeWeight)
        HWbox.Add(self.Weight, 0, wx.EXPAND | wx.ALL, 5)
        
        HWbox2 = wx.BoxSizer(wx.VERTICAL)
        hbox.Add(HWbox2, 0, wx.EXPAND | wx.ALL, 5)
        
        self.Meters = wx.StaticText(DEX, -1,"Meters: XXXX")
        HWbox2.Add(self.Meters, 0, wx.ALL, 7)
        
        self.Feet = wx.StaticText(DEX, -1,"Feet: XXXX")
        HWbox2.Add(self.Feet, 0, wx.ALL, 7)
        
        self.kg = wx.StaticText(DEX, -1,"Kilograms: XXXX")
        HWbox2.Add(self.kg, 0, wx.ALL, 7)
        
        self.ilbs = wx.StaticText(DEX, -1,"Pounds: XXXX")
        HWbox2.Add(self.ilbs, 0, wx.ALL, 7)
        
        SizeCmpLbl = wx.StaticText(DEX, -1,"Size Comparison:")
        vbox.Add(SizeCmpLbl, 0, wx.TOP|wx.LEFT, 8)
        
        ##Pokemon Scale
        PScaleBox = wx.BoxSizer(wx.HORIZONTAL)
        vbox.Add(PScaleBox, 0, wx.LEFT, 5)
        PScaleBoxLeft = wx.BoxSizer(wx.VERTICAL)
        PScaleBox.Add(PScaleBoxLeft, 0, wx.LEFT | wx.RIGHT, 5)
        
        Pscale_txt = wx.StaticText(DEX, -1,encode_per_platform("POK\xe9MON Scale:"))
        PScaleBoxLeft.Add(Pscale_txt, 0, wx.ALL, 5)
        self.Pscale = wx.TextCtrl(DEX, wx.ID_ANY, style=wx.TE_CENTRE, size=(50, -1))
        self.Pscale.Bind(wx.EVT_TEXT, self.ChangePscale)
        PScaleBoxLeft.Add(self.Pscale, 0, wx.ALL, 5)
        
        Poffset_txt = wx.StaticText(DEX, -1,encode_per_platform("POK\xe9MON Offset:"))
        PScaleBoxLeft.Add(Poffset_txt, 0, wx.ALL, 5)
        self.Poffset = wx.TextCtrl(DEX, wx.ID_ANY, style=wx.TE_CENTRE, size=(50, -1))
        self.Poffset.Bind(wx.EVT_TEXT, self.ChangePoffset)
        PScaleBoxLeft.Add(self.Poffset, 0, wx.ALL, 5)
        
        PScaleBoxRight = wx.BoxSizer(wx.VERTICAL)
        PScaleBox.Add(PScaleBoxRight, 0, wx.LEFT | wx.RIGHT, 5)
        
        self.PScale_x = wx.StaticText(DEX, -1,"0.000x---")
        PScaleBoxRight.Add(self.PScale_x, 0, wx.TOP, 15)
        
        self.PScale_px = wx.StaticText(DEX, -1,"64px")
        PScaleBoxRight.Add(self.PScale_px, 0, wx.TOP, 5)

        ##Trainer Scale
        TScaleBox = wx.BoxSizer(wx.HORIZONTAL)
        vbox.Add(TScaleBox, 0, wx.LEFT, 5)
        TScaleBoxLeft = wx.BoxSizer(wx.VERTICAL)
        TScaleBox.Add(TScaleBoxLeft, 0, wx.LEFT | wx.RIGHT, 5)
        
        Tscale_txt = wx.StaticText(DEX, -1, "Trainer Scale:")
        TScaleBoxLeft.Add(Tscale_txt, 0, wx.ALL, 5)
        self.Tscale = wx.TextCtrl(DEX, wx.ID_ANY, style=wx.TE_CENTRE, size=(50, -1))
        self.Tscale.Bind(wx.EVT_TEXT, self.ChangeTscale)
        TScaleBoxLeft.Add(self.Tscale, 0, wx.ALL, 5)
        
        Toffset_txt = wx.StaticText(DEX, -1,"Trainer Offset:")
        TScaleBoxLeft.Add(Toffset_txt, 0, wx.ALL, 5)
        self.Toffset = wx.TextCtrl(DEX, wx.ID_ANY, style=wx.TE_CENTRE, size=(50, -1))
        self.Toffset.Bind(wx.EVT_TEXT, self.ChangeToffset)
        TScaleBoxLeft.Add(self.Toffset, 0, wx.ALL, 5)
        
        self.sizer.Add(DEX, 0, wx.EXPAND | wx.ALL, 5)
    
        TScaleBoxRight = wx.BoxSizer(wx.VERTICAL)
        TScaleBox.Add(TScaleBoxRight, 0, wx.LEFT | wx.RIGHT, 5)
        
        self.TScale_x = wx.StaticText(DEX, -1,"0.000x---")
        TScaleBoxRight.Add(self.TScale_x, 0, wx.TOP, 15)
        
        self.TScale_px = wx.StaticText(DEX, -1,"64px")
        TScaleBoxRight.Add(self.TScale_px, 0, wx.TOP, 5)
        
        self.LoadEverything()
    
    def OnRepointE1(self, *args):
        pokedex = int(Globals.INI.get(Globals.OpenRomID, "pokedex"), 0)
        LengthofPokedexEntry = int(Globals.INI.get(Globals.OpenRomID, "LengthofPokedexEntry"), 0)
        DexType = Globals.INI.get(Globals.OpenRomID, "DexType")
                    
        global poke_num
        with open(Globals.OpenRomName, "r+b") as rom:
            entry1 = convert_ascii_and_poke(self.Entry1.GetValue(), "to_ascii")
            repoint = Repointer(Globals.OpenRomName, frame, len(entry1), "Entry 1")
            if repoint.ShowModal() == wx.ID_OK:
                offset = repoint.offset
                if offset == None:
                    ERROR = wx.MessageDialog(None, 
                                "No offset was selected and nothing has been changed.", 
                                'Just letting you know...', 
                                wx.OK | wx.ICON_ERROR)
                    ERROR.ShowModal()
                    return
                POKE = poke_num-1
                if POKE == -1:
                    index = 0
                else:
                    index = self.NatDexList[POKE]
                    if index == 0:
                        return
                    else: pokedex = pokedex+(index)*LengthofPokedexEntry
                rom.seek(pokedex+16)
                #Write new pointer
                hexOffset = hex(offset+0x8000000).rstrip("L").lstrip("0x").zfill(8)
                hexOffset = make_pointer(hexOffset)
                hexOffset = unhexlify(hexOffset)
                rom.write(hexOffset)
                rom.seek(-4, 1)
                #Write new image
                rom.seek(offset)
                self.entry1_offset = offset
                self.OriginalEntry1Len = len(entry1)
                rom.write(entry1+"\xff\xff")
        
                rom.seek(0,1)
                check = rom.read(1)
                if check == "\xff":
                    rom.seek(-1,1)
                    rom.write("\xfe")
            else:
                ERROR = wx.MessageDialog(None, 
                                "You have aborted repoint. Nothing was changed.", 
                                'Just letting you know...', 
                                wx.OK | wx.ICON_ERROR)
                ERROR.ShowModal()
    
    def OnRepointE2(self, *args):
        pokedex = int(Globals.INI.get(Globals.OpenRomID, "pokedex"), 0)
        LengthofPokedexEntry = int(Globals.INI.get(Globals.OpenRomID, "LengthofPokedexEntry"), 0)
        DexType = Globals.INI.get(Globals.OpenRomID, "DexType")
                    
        global poke_num
        with open(Globals.OpenRomName, "r+b") as rom:
            entry2 = convert_ascii_and_poke(self.Entry2.GetValue(), "to_ascii")
            repoint = Repointer(Globals.OpenRomName, frame, len(entry2), "Entry 2")
            if repoint.ShowModal() == wx.ID_OK:
                    offset = repoint.offset
                    if offset == None:
                        ERROR = wx.MessageDialog(None, 
                                    "No offset was selected and nothing has been changed.", 
                                    'Just letting you know...', 
                                    wx.OK | wx.ICON_ERROR)
                        ERROR.ShowModal()
                        return
                    POKE = poke_num-1
                    if POKE == -1:
                        index = 0
                    else:
                        index = self.NatDexList[POKE]
                        if index == 0:
                            return
                        else: pokedex = pokedex+(index)*LengthofPokedexEntry
                    rom.seek(pokedex+20)
                    #Write new pointer
                    hexOffset = hex(offset+0x8000000).rstrip("L").lstrip("0x").zfill(8)
                    hexOffset = make_pointer(hexOffset)
                    hexOffset = unhexlify(hexOffset)
                    rom.write(hexOffset)
                    #Write new image
                    rom.seek(offset)
                    rom.write(entry2)
                    self.entry2_offset = offset
                    self.OriginalEntry2Len = len(entry2)
                    rom.write(entry1+"\xff\xff")
            
                    rom.seek(0,1)
                    check = rom.read(1)
                    if check == "\xff":
                        rom.seek(-1,1)
                        rom.write("\xfe")
            else:
                ERROR = wx.MessageDialog(None, 
                                "You have aborted repoint. Nothing was changed.", 
                                'Just letting you know...', 
                                wx.OK | wx.ICON_ERROR)
                ERROR.ShowModal()
    
    def OnRepointFeet(self, *args):
        global poke_num
        with open(Globals.OpenRomName, "r+b") as rom:
            repoint = Repointer(Globals.OpenRomName, frame, 32, "Footprint")
            if repoint.ShowModal() == wx.ID_OK:
                    offset = repoint.offset
                    if offset == None:
                        ERROR = wx.MessageDialog(None, 
                                    "No offset was selected and nothing has been changed.", 
                                    'Just letting you know...', 
                                    wx.OK | wx.ICON_ERROR)
                        ERROR.ShowModal()
                        return
                    footprints = int(Globals.INI.get(Globals.OpenRomID, "footprints"), 0)
                    rom.seek(footprints+(poke_num)*4)
                    #Write new pointer
                    hexOffset = hex(offset+0x8000000).rstrip("L").lstrip("0x").zfill(8)
                    hexOffset = make_pointer(hexOffset)
                    hexOffset = unhexlify(hexOffset)
                    rom.write(hexOffset)
                    #Write new image
                    rom.seek(offset)
                    rom.write(self.GBAPrint)
                    self.FootPrintOffset = offset
                
            else:
                ERROR = wx.MessageDialog(None, 
                                "You have aborted repoint. Nothing was changed.", 
                                'Just letting you know...', 
                                wx.OK | wx.ICON_ERROR)
                ERROR.ShowModal()
            
    def OnFoot(self, *args):
        if not self.lastPath: self.lastPath = os.getcwd()
        wildcard = "PNG (*.png)|*.png|GIF (*.gif)|*.gif|All files (*.*)|*.*"
        open_dialog = wx.FileDialog(self, message="Open a footprint (16x16)...", 
                                    defaultDir=self.lastPath, style=wx.OPEN,
                                    wildcard=wildcard)
        if open_dialog.ShowModal() == wx.ID_OK:
            filename = open_dialog.GetPath()
            self.lastPath = os.path.dirname(filename)
            raw = Image.open(filename)
            if raw.size != (16,16):
                ERROR = wx.MessageDialog(self,
                        "Image is "+str(raw.size[0])+"x"+str(raw.size[1])+". It must be 16x16.", 
                        'Image Size error', 
                        wx.OK | wx.ICON_ERROR)
                ERROR.ShowModal()
                return
            if raw.mode != "1":
                raw = raw.convert("RGB")
                converted = raw.convert("1")
            else:
                if len(raw.getcolors()) > 2:
                    tmp = raw.convert("RGB")
                    converted = raw.convert("1")
                else: converted = raw
            image = PilImageToWxImage(converted)
            self.GBAPrint = ConvertNormalFootPrintToGBA(image)
            bitmap = ConvertGBAFootprintToNormal(self.GBAPrint)
            self.FootPrint.SetBitmapLabel(bitmap)
            
    def OnFixNameBug(self,instance):
        with open(Globals.OpenRomName, "r+b") as rom:
            rom.seek(0x10583C)
            rom.write("\xFF")
            rom.seek(0x105856)
            rom.write("\xFF")
        self.FixNameBug.Disable()
        
    def save(self):
        pokedex = int(Globals.INI.get(Globals.OpenRomID, "pokedex"), 0)
        LengthofPokedexEntry = int(Globals.INI.get(Globals.OpenRomID, "LengthofPokedexEntry"), 0)
        DexType = Globals.INI.get(Globals.OpenRomID, "DexType")

        self.GetNationalDexOrder()
        
        with open(Globals.OpenRomName, "r+b") as rom:
            global poke_num
            POKE = poke_num-1
            if POKE == -1:
                index = 0
            else:
                index = self.NatDexList[POKE]
                if index == 0:
                    return
                else: pokedex = pokedex+(index)*LengthofPokedexEntry
            rom.seek(pokedex)
            
            Type = convert_ascii_and_poke(self.Type.GetValue(), "to_ascii")
            Type = Type[:11]+"\xff"
            rom.write(Type)
            
            rom.seek(pokedex+12)
            
            try: height = int(self.Height.GetValue(),0)
            except: height = 1
            height = hex(height)[2:].zfill(4)
            height = height[2:4]+height[:2]
            rom.write(get_hex_from_string(height))
            
            try: weight = int(self.Weight.GetValue(),0)
            except: weight = 1
            weight = hex(weight)[2:].zfill(4)
            weight = weight[2:4]+weight[:2]
            rom.write(get_hex_from_string(weight))
            
            entry1 = convert_ascii_and_poke(self.Entry1.GetValue(), "to_ascii")
           
            if self.OriginalEntry1Len < len(entry1):
                self.OriginalEntry1Len = len(entry1)
                repointer = POKEDEXEntryRepointer(parent=None, 
                                                  need=len(entry1)+3,
                                                  repoint_what="'Dex Entry 1")
                global returned_offset
                while True:
                    if repointer.ShowModal() == wx.ID_OK:
                        
                        if returned_offset == self.entry1_offset: continue
                        elif returned_offset == None: continue
                        else:
                            org_offset = self.entry1_offset
                            self.entry1_offset = int(returned_offset, 16)
                            returned_offset = None
                            if repointer.cb.IsChecked() == True:
                                need_overwrite = True
                            else:
                                need_overwrite = False
                            break
                    else: return
            else: need_overwrite = False
            
            rom.seek(self.entry1_offset)
            rom.write(entry1+"\xff\xff")
            
            rom.seek(0,1)
            check = rom.read(1)
            if check == "\xff":
                rom.seek(-1,1)
                rom.write("\xfe")

            rom.seek(pokedex+16)
            pointer = self.entry1_offset+0x8000000
            pointer = hex(pointer)[2:]
            pointer = make_pointer(pointer)
            pointer = get_hex_from_string(pointer)
            rom.write(pointer)
            
            if need_overwrite == True:
                rom.seek(org_offset)
                while True:
                    read = rom.read(1)
                    if read != "\xff":
                        rom.seek(-1,1)
                        rom.write("\xff")
                        rom.seek(1,1)
                    else:
                        read2 = rom.read(1)
                        if read2 == "\xff":
                            read3 = rom.read(1)
                            if read3 == "\xfe":
                                rom.seek(-1,1)
                                rom.write("\xff")
                                rom.seek(1,1)
                        break
            
            if self.OriginalEntry2Len != None:
            
                entry2 = convert_ascii_and_poke(self.Entry2.GetValue(), "to_ascii")
           
                if self.OriginalEntry2Len < len(entry2):
                    self.OriginalEntry2Len = len(entry2)
                    repointer = POKEDEXEntryRepointer(parent=None, 
                                                      need=len(entry2)+3,
                                                      repoint_what="'Dex Entry 2")
                    while True:
                        if repointer.ShowModal() == wx.ID_OK:
                            
                            if returned_offset == self.entry2_offset: continue
                            elif returned_offset == None: continue
                            else:
                                org_offset = self.entry2_offset
                                self.entry2_offset =  int(returned_offset, 16)
                                returned_offset = None
                                if repointer.cb.IsChecked() == True:
                                    need_overwrite = True
                                else:
                                    need_overwrite = False
                                break
                        else: return
                else: need_overwrite = False

                rom.seek(self.entry2_offset)
                rom.write(entry2+"\xff\xff")
                
                rom.seek(0,1)
                check = rom.read(1)
                if check == "\xff":
                    rom.seek(-1,1)
                    rom.write("\xfe")
                
                rom.seek(pokedex+20)
                pointer = self.entry2_offset+0x8000000
                pointer = hex(pointer)[2:]
                pointer = make_pointer(pointer)
                pointer = get_hex_from_string(pointer)
                rom.write(pointer)
                
                if need_overwrite == True:
                    rom.seek(org_offset)
                    while True:
                        read = rom.read(1)
                        if read != "\xff":
                            rom.seek(-1,1)
                            rom.write("\xff")
                            rom.seek(1,1)
                        else:
                            read2 = rom.read(1)
                            if read2 == "\xff":
                                read3 = rom.read(1)
                                if read3 == "\xfe":
                                    rom.seek(-1,1)
                                    rom.write("\xff")
                                    rom.seek(1,1)
                            break
            
            if DexType != "E": rom.seek(pokedex+26)
            else: rom.seek(pokedex+22)
            
            try: Pscale = int(self.Pscale.GetValue(),0)
            except: Pscale = 256
            Pscale = hex(Pscale)[2:].zfill(4)
            Pscale = Pscale[2:4]+Pscale[:2]
            rom.write(get_hex_from_string(Pscale))
            
            try: Poffset = int(self.Poffset.GetValue(),0)
            except: Poffset = 0
            Poffset = deal_with_16bit_signed_hex(Poffset, method="backward")
            Poffset = Poffset[2:4]+Poffset[:2]
            rom.write(get_hex_from_string(Poffset))
            
            try: Tscale = int(self.Tscale.GetValue(),0)
            except: Tscale = 256
            Tscale = hex(Tscale)[2:].zfill(4)
            Tscale = Tscale[2:4]+Tscale[:2]
            rom.write(get_hex_from_string(Tscale))
            
            try: Toffset = int(self.Toffset.GetValue(),0)
            except: Toffset = 0
            Toffset = deal_with_16bit_signed_hex(Toffset, method="backward")
            Toffset = Toffset[2:4]+Toffset[:2]
            rom.write(get_hex_from_string(Toffset))
            
            #Write the FEETS
            rom.seek(self.FootPrintOffset)
            rom.write(self.GBAPrint)
            
    def LoadEverything(self):
        pokedex = int(Globals.INI.get(Globals.OpenRomID, "pokedex"), 0)
        LengthofPokedexEntry = int(Globals.INI.get(Globals.OpenRomID, "LengthofPokedexEntry"), 0)
        DexType = Globals.INI.get(Globals.OpenRomID, "DexType")
        footprints = int(Globals.INI.get(Globals.OpenRomID, "footprints"), 0)
        
        self.GetNationalDexOrder()
        with open(Globals.OpenRomName, "r+b") as rom:
            global poke_num
            POKE = poke_num-1
            if POKE == -1:
                index = 0
            else:
                index = self.NatDexList[POKE]
                if index == 0:
                    self.Height.SetValue("")
                    self.Weight.SetValue("")
                    self.Entry1.SetValue("")
                    self.Entry2.SetValue("")
                    self.Pscale.SetValue("")
                    self.Poffset.SetValue("")
                    self.Tscale.SetValue("")
                    self.Toffset.SetValue("")
                    self.Type.SetValue("")
                    return
                else: pokedex = pokedex+(index)*LengthofPokedexEntry

            rom.seek(pokedex)
            type = rom.read(12)
            type = type.split("\xff")[0]
            type = convert_ascii_and_poke(type, "to_poke")
            self.Type.SetValue(type)
            
            height = get_bytes_string_from_hex_string(rom.read(2))
            height = int(height[2:4]+height[:2],16)
            self.Height.SetValue(str(height))
            
            weight = get_bytes_string_from_hex_string(rom.read(2))
            weight = int(weight[2:4]+weight[:2], 16)
            self.Weight.SetValue(str(weight))
            
            self.entry1_offset = read_pointer(rom.read(4))
            rom.seek(self.entry1_offset)
            entry1 = ""
            while True:
                read = rom.read(1)
                if read == "\xff": break
                entry1 += read
            self.OriginalEntry1Len = len(entry1)
            entry1 = convert_ascii_and_poke(entry1, "to_poke")
            self.Entry1.SetValue(entry1)
            
            rom.seek(pokedex+20)
            if DexType != "FRLG" and DexType != "E":
                self.entry2_offset = read_pointer(rom.read(4))
                rom.seek(self.entry2_offset)
                entry2 = ""
                while True:
                    read = rom.read(1)
                    if read == "\xff": break
                    entry2 += read
                self.OriginalEntry2Len = len(entry2)
                entry2 = convert_ascii_and_poke(entry2, "to_poke")
                self.Entry2.SetValue(entry2)
            else: 
                self.Entry2.Disable()
                self.RepointE2.Disable()
            if DexType != "E": rom.seek(pokedex+26)
            else: rom.seek(pokedex+22)
            Pscale = get_bytes_string_from_hex_string(rom.read(2))
            Pscale = int(Pscale[2:4]+Pscale[:2],16)
            self.Pscale.SetValue(str(Pscale))
            
            Poffset = get_bytes_string_from_hex_string(rom.read(2))
            Poffset = int(Poffset[2:4]+Poffset[:2],16)
            Poffset = deal_with_16bit_signed_hex(Poffset)
            self.Poffset.SetValue(str(Poffset))
            
            Tscale = get_bytes_string_from_hex_string(rom.read(2))
            Tscale = int(Tscale[2:4]+Tscale[:2],16)
            self.Tscale.SetValue(str(Tscale))
            
            Toffset = get_bytes_string_from_hex_string(rom.read(2))
            Toffset = int(Toffset[2:4]+Toffset[:2],16)
            Toffset = deal_with_16bit_signed_hex(Toffset)
            self.Toffset.SetValue(str(Toffset))
            
            #Footprints
            rom.seek(footprints+poke_num*4)
            self.FootPrintOffset = read_pointer(rom.read(4))
            rom.seek(self.FootPrintOffset)
            self.GBAPrint = rom.read(32)
            bitmap = ConvertGBAFootprintToNormal(self.GBAPrint)
            self.FootPrint.SetBitmapLabel(bitmap)
            
            gamecode = Globals.INI.get(Globals.OpenRomID, "gamecode")
            if gamecode == "BPRE":
                rom.seek(0x10583C)
                read1 = rom.read(1)
                rom.seek(0x105856)
                read2 = rom.read(1)
                if read1 == "\xFF" and read2 == "\xFF":
                    self.FixNameBug.Disable()
            
    def GetNationalDexOrder(self):
        NationalDexOrder = int(Globals.INI.get(Globals.OpenRomID, "NationalDexOrder"), 0)
        numofnondexpokesbetweencelebiandtreeko = int(Globals.INI.get(Globals.OpenRomID, "numofnondexpokesbetweencelebiandtreeko"), 0)
        numberofpokes = int(Globals.INI.get(Globals.OpenRomID, "numberofpokes"), 0)
        numofnondexpokesafterchimecho = int(Globals.INI.get(Globals.OpenRomID, "numofnondexpokesafterchimecho"), 0)
        self.NatDexList = []
        with open(Globals.OpenRomName, "r+b") as rom:
            rom.seek(NationalDexOrder)
            for n in range(251):
                tmp = rom.read(2)
                reverse = tmp[1]+tmp[0]
                halfword = get_bytes_string_from_hex_string(reverse)
                integer = int(halfword, 16)
                self.NatDexList.append(integer)
            
            
            for n in range(numofnondexpokesbetweencelebiandtreeko):
                self.NatDexList.append(0)
            rom.seek(numofnondexpokesbetweencelebiandtreeko*2,1)
            for n in range(136):
                tmp = rom.read(2)
                tmp = tmp[1]+tmp[0]
                tmp = get_bytes_string_from_hex_string(tmp)
                tmp = int(tmp, 16)
                self.NatDexList.append(tmp)
            for n in range(numofnondexpokesafterchimecho-1):
                self.NatDexList.append(0)
            rom.seek((numofnondexpokesafterchimecho-1)*2,1)
            for n in range(numberofpokes-(136+251+numofnondexpokesafterchimecho-1+numofnondexpokesbetweencelebiandtreeko)):
                tmp = rom.read(2)
                tmp = tmp[1]+tmp[0]
                tmp = get_bytes_string_from_hex_string(tmp)
                tmp = int(tmp, 16)
                self.NatDexList.append(tmp)
                
    def ChangePscale(self, instance):
        try: value = int(self.Pscale.GetValue(),0)
        except:
            limit = self.Pscale.GetValue()[:-1]
            curr = self.Pscale.GetValue()
            if curr != "0x" and curr != "":
                self.Pscale.SetValue(limit)
            return
            
        if value < 0:
            value = 1
            self.Pscale.SetValue("1")
        if value > 1536:
            value = 1536
            self.Pscale.SetValue("1536")
            
        try: 
            size = int(64*(256/value))
            self.PScale_px.SetLabel(str(size)+"px")
        except:
            self.PScale_px.SetLabel("Bad Scale")
            self.PScale_x.SetLabel("")
            return
        scale = 256/value
        scale = ("{0:.3f}x".format(scale))
        self.PScale_x.SetLabel(scale)
        
    def ChangePoffset(self, instance):
        try: value = int(self.Poffset.GetValue(),0)
        except:
            limit = self.Poffset.GetValue()[:-1]
            curr = self.Poffset.GetValue()
            if curr != "0x" and curr != "" and curr != "-" and curr != "-0x-":
                self.Poffset.SetValue(limit)
            return
            
        if value > 99:
            value = 99
            self.Poffset.SetValue("99")
        if value < -99:
            value = -99
            self.Poffset.SetValue("-99")
            
    def ChangeTscale(self, instance):
        try: value = int(self.Tscale.GetValue(),0)
        except:
            limit = self.Tscale.GetValue()[:-1]
            curr = self.Tscale.GetValue()
            if curr != "0x" and curr != "":
                self.Tscale.SetValue(limit)
            return
            
        if value < 0:
            value = 1
            self.Tscale.SetValue("1")
        if value > 1536:
            value = 1536
            self.Tscale.SetValue("1536")
            
            
        try: 
            size = int(64*(256/value))
            self.TScale_px.SetLabel(str(size)+"px")
        except:
            self.TScale_px.SetLabel("Bad Scale")
            self.TScale_x.SetLabel("")
            return
        scale = 256/value
        scale = ("{0:.3f}x".format(scale))
        self.TScale_x.SetLabel(scale)
        
    def ChangeToffset(self, instance):
        try: value = int(self.Toffset.GetValue(),0)
        except:
            limit = self.Toffset.GetValue()[:-1]
            curr = self.Toffset.GetValue()
            if curr != "0x" and curr != "" and curr != "-" and curr != "-0x":
                self.Toffset.SetValue(limit)
            return
            
        if value > 99:
            value = 99
            self.Toffset.SetValue("99")
        if value < -99:
            value = -99
            self.Toffset.SetValue("-99")
    
    def ChangeHeight(self, instance):
        try: height = int(self.Height.GetValue(),0)
        except:
            limit = self.Height.GetValue()[:-1]
            curr = self.Height.GetValue()
            if curr != "0x" and curr != "":
                self.Height.SetValue(limit)
            return
        meters = height/10
        feet = meters*3.28084
        
        meters = ("Meters: {0:.1f}".format(meters))
        feet = ("Feet: {0:.1f}".format(feet))
        
        self.Meters.SetLabel(meters)
        self.Feet.SetLabel(feet)
        
    def ChangeWeight(self, instance):
        try: weight = int(self.Weight.GetValue(),0)
        except:
            limit = self.Weight.GetValue()[:-1]
            curr = self.Weight.GetValue()
            if curr != "0x" and curr != "":
                self.Weight.SetValue(limit)
            return
        kg = weight/10
        pounds = kg*2.20462
        
        kg = ("Kilograms: {0:.1f}".format(kg))
        pounds = ("Pounds: {0:.1f}".format(pounds))
        
        self.kg.SetLabel(kg)
        self.ilbs.SetLabel(pounds)
        
class MoveTutorTab(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.gamecode = Globals.INI.get(Globals.OpenRomID, "gamecode")
        self.GenerateUI()
        
        self.SetSizer(self.sizer)
        
    def GenerateUI(self):
        TUTOR = wx.Panel(self, -1, style=wx.RAISED_BORDER|wx.TAB_TRAVERSAL)
        MAIN = wx.BoxSizer(wx.HORIZONTAL)
        TUTOR.SetSizer(MAIN)
        
        TutorComp = wx.Panel(TUTOR, -1, style=wx.RAISED_BORDER|wx.TAB_TRAVERSAL)
        TutorCompSizer = wx.BoxSizer(wx.HORIZONTAL)
        TutorComp.SetSizer(TutorCompSizer)
        MAIN.Add(TutorComp, 0, wx.EXPAND | wx.ALL, 5)
        
        CompBox = wx.BoxSizer(wx.VERTICAL)
        ButtonBox = wx.BoxSizer(wx.VERTICAL)
        TutorCompSizer.Add(CompBox)
        TutorCompSizer.Add(ButtonBox)
        
        CompTxt = wx.StaticText(TutorComp, -1,"Move Tutor Compatibility:")
        CompBox.Add(CompTxt, 0, wx.EXPAND | wx.ALL, 5)
        
        self.CompList = CheckListCtrl(TutorComp, size=(170,350))
        self.CompList.InsertColumn(0, 'Move', width=140)
        CompBox.Add(self.CompList, 0, wx.EXPAND | wx.ALL, 5)
        
        SELECTALL = Button(TutorComp, 0, "Select All")
        self.Bind(wx.EVT_BUTTON, self.OnSelectAllComp, id=0)
        ButtonBox.Add(SELECTALL, 0, wx.EXPAND | wx.ALL, 5)
        
        CLEAR = Button(TutorComp, 1, "Clear All")
        self.Bind(wx.EVT_BUTTON, self.OnClearAllComp, id=1)
        ButtonBox.Add(CLEAR, 0, wx.EXPAND | wx.ALL, 5)
        
        TutorMoves = wx.Panel(TUTOR, -1, style=wx.RAISED_BORDER|wx.TAB_TRAVERSAL)
        TutorMovesSizer = wx.BoxSizer(wx.HORIZONTAL)
        TutorMoves.SetSizer(TutorMovesSizer)
        MAIN.Add(TutorMoves, 0, wx.EXPAND | wx.ALL, 5)
        
        MovesVBox = wx.BoxSizer(wx.VERTICAL)
        TutorMovesSizer.Add(MovesVBox, 0, wx.EXPAND | wx.ALL, 5)
        
        MovesTxt = wx.StaticText(TutorMoves, -1,"Move Tutor Editor:")
        MovesVBox.Add(MovesTxt, 0, wx.EXPAND | wx.ALL, 5)
        
        self.moves = wx.ListBox(TutorMoves, -1,size=(100,350))
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.OnSelectMove,  self.moves)
        MovesVBox.Add(self.moves, 0, wx.EXPAND | wx.ALL, 5)
        
        TutorMovesButtons = wx.BoxSizer(wx.VERTICAL)
        TutorMovesSizer.Add(TutorMovesButtons, 0, wx.EXPAND | wx.ALL, 5)
        global MOVES_LIST
        self.ATTACK = ComboBox(TutorMoves, -1, choices=MOVES_LIST,
                                style=wx.SUNKEN_BORDER, size=(100, -1))
        TutorMovesButtons.Add(self.ATTACK, 0, wx.EXPAND | wx.ALL, 2)
        
        SET = Button(TutorMoves, 8, "Replace")
        self.Bind(wx.EVT_BUTTON, self.OnChangeMove, id=8)
        TutorMovesButtons.Add(SET, 0, wx.EXPAND | wx.ALL, 2)
        
        DELETE = Button(TutorMoves, 3, "Delete")
        self.Bind(wx.EVT_BUTTON, self.OnDelete, id=3)
        TutorMovesButtons.Add(DELETE, 0, wx.EXPAND | wx.ALL, 5)
        
        MOVE_UP = Button(TutorMoves, 4, "Move Up")
        self.Bind(wx.EVT_BUTTON, self.OnMoveUp, id=4)
        TutorMovesButtons.Add(MOVE_UP, 0, wx.EXPAND | wx.ALL, 5)
        
        MOVE_DOWN = Button(TutorMoves, 5, "Move Down")
        self.Bind(wx.EVT_BUTTON, self.OnMoveDown, id=5)
        TutorMovesButtons.Add(MOVE_DOWN, 0, wx.EXPAND | wx.ALL, 5)
        
        #----Add Everything to the Sizer----#
        self.sizer.Add(TUTOR, 0, wx.EXPAND | wx.ALL, 5)
        self.load_everything()
        
    def save(self):
        num = self.CompList.GetItemCount()
        binary = ""
        for i in range(num):
            if self.CompList.IsChecked(i): binary += "1"
            else: binary += "0"
        check = len(binary)%16
        if check != 0:
            for n in range(16-check): 
                binary += "0"
        hexCOMP = ""
        with open(Globals.OpenRomName, "r+b") as rom:
            while True:
                word = binary[:16]
                word = word[::-1]
                word = int(word, 2)
                word = hex(word).rstrip("L").lstrip("0x").zfill(4)
                word = reverse_hex(word)
                word = get_hex_from_string(word)
                hexCOMP += word
                
                if len(binary) == 16:
                    break
                binary = binary[16:]
            rom.seek(self.MoveTutorComp)
            rom.write(hexCOMP)
            
            attacks = ""
            for move in self.attacks:
                move = hex(move).rstrip("L").lstrip("0x").zfill(4)
                move = move[2:]+move[:2]
                attacks += move
            attacks = get_hex_from_string(attacks)
            
            rom.seek(self.MoveTutorAttacks)
            rom.write(attacks)
            
            self.load_everything()
        
    def load_everything(self):
        global MOVES_LIST
        self.get_comp_data()
        self.CompList.DeleteAllItems()
        for num, move in enumerate(self.attacks):
            try: index = self.CompList.InsertStringItem(sys.maxint, MOVES_LIST[move])
            except:
                ERROR = wx.MessageDialog(None, 
                                    textwrap.fill("Move tutor moves have not been fully loaded because there was an error. Either not enough moves were loaded due to a bad number in the ini or the learned move data offset is bad/corrupted. The error occurred trying to read move #{0}. The current number of moves is: {1}.".format(move, len(MOVES_LIST)-1),100), 
                                    'Error', 
                                    wx.OK | wx.ICON_ERROR)
                ERROR.ShowModal()
                return
            if self.COMP[num] == True:
                self.CompList.CheckItem(index) 
        self.load_list_box()
        
    def load_list_box(self):
        global MOVES_LIST
        self.moves.Clear()
        for move in self.attacks:
            self.moves.Append(MOVES_LIST[move])
        
    def get_comp_data(self):
        self.MoveTutorComp = int(Globals.INI.get(Globals.OpenRomID, "MoveTutorComp"), 0)
        length = int(Globals.INI.get(Globals.OpenRomID, "MoveTutorCompLen"), 0)
        global poke_num
        
        with open(Globals.OpenRomName, "r+b") as rom:
            self.MoveTutorComp += (poke_num)*length
            rom.seek(self.MoveTutorComp)
            read = rom.read(length)
            self.COMP = []
            word = [get_bytes_string_from_hex_string(read)]
            if self.gamecode[:3] == "BPE":
                tmp = word[0][:length]
                tmp2 = word[0][length:]
                word = [tmp, tmp2]
            for set in word:
                swap = int(set[2:]+set[:2],16)
                binary = bin(swap)[2:].zfill(16)
                binary = binary[::-1]
                for c in binary:
                    if c == "0": self.COMP.append(False)
                    else: self.COMP.append(True)
            
            self.MoveTutorAttacks = int(Globals.INI.get(Globals.OpenRomID, "MoveTutorAttacks"), 0)
            MTAttacksLen = int(Globals.INI.get(Globals.OpenRomID, "MTAttacksLen"), 0)
            MTAttacksNum = int(Globals.INI.get(Globals.OpenRomID, "MTAttacksNum"), 0)
            
            self.attacks = []
            rom.seek(self.MoveTutorAttacks)
            for n in range(MTAttacksNum):
                read = rom.read(MTAttacksLen)
                read = read[1]+read[0]
                read = get_bytes_string_from_hex_string(read)
                read = int(read, 16)
                self.attacks.append(read)
        
    def OnDelete(self, *args):
        selection = self.moves.GetSelection()
        if selection != -1:
            self.attacks[selection] = 0
            self.load_list_box()
            
    def OnMoveUp(self, *args):
        selection = self.moves.GetSelection()
        if selection != -1 and selection != 0:
            self.attacks[selection], self.attacks[selection-1] = self.attacks[selection-1], self.attacks[selection]
            self.load_list_box()
            self.moves.Select(selection-1)
            
    def OnMoveDown(self, *args):
        selection = self.moves.GetSelection()
        length = len(self.attacks)-1
        if selection != -1 and selection != length:
            self.attacks[selection], self.attacks[selection+1] = self.attacks[selection+1], self.attacks[selection]
            self.load_list_box()
            self.moves.Select(selection+1)
            
    def OnChangeMove(self, *args):
        selection = self.moves.GetSelection()
        if selection != -1:
            attack = self.ATTACK.GetSelection()
            if attack == -1: return
            self.attacks[selection] = attack
            self.load_list_box()
            self.moves.Select(selection)
            
    def OnSelectMove(self, *args):
        sel = self.moves.GetSelection()
        self.ATTACK.SetSelection(self.attacks[sel])
        
    def OnSelectAllComp(self, instance):
        num = self.CompList.GetItemCount()
        for n in range(num):
            self.CompList.CheckItem(n) 
    
    def OnClearAllComp(self, instance):
        num = self.CompList.GetItemCount()
        for n in range(num):
            self.CompList.CheckItem(n, False) 
            
class EggMoveTab(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.style = wx.RAISED_BORDER|wx.TAB_TRAVERSAL
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.load_egg_moves()
        
        names_buttons_vbox = wx.BoxSizer(wx.VERTICAL)
        self.POKE_NAME = ComboBox(self, -1, choices=Globals.PokeNames,
                                style=wx.SUNKEN_BORDER, size=(100, -1))
        names_buttons_vbox.Add(self.POKE_NAME, 0, wx.EXPAND | wx.ALL, 5)
        
        ADD_POKE =  Button(self, 1, "Add Poke")
        self.Bind(wx.EVT_BUTTON, self.OnAddPoke, id=1)
        names_buttons_vbox.Add(ADD_POKE, 0, wx.EXPAND | wx.ALL, 5)

        DELETE_POKE =  Button(self, 2, "Remove Poke")
        self.Bind(wx.EVT_BUTTON, self.OnDeletePoke, id=2)
        names_buttons_vbox.Add(DELETE_POKE, 0, wx.EXPAND | wx.ALL, 5)

        
        poke_names_vbox = wx.BoxSizer(wx.VERTICAL)
        self.POKES = wx.ListCtrl(self, -1, style=wx.LC_REPORT, size=(230,400))
        self.POKES.InsertColumn(0, '#', width=40)
        self.POKES.InsertColumn(1, 'HEX', width=50)
        self.POKES.InsertColumn(2, 'Name', width=120)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelectPoke,  self.POKES)
        poke_names_vbox.Add(self.POKES, 0, wx.EXPAND | wx.ALL, 5)
        
        self.LoadPOKESList()
        
        
        moves_vbox = wx.BoxSizer(wx.VERTICAL)
        self.MOVES = wx.ListCtrl(self, -1, style=wx.LC_REPORT, size=(230,400))
        self.MOVES.InsertColumn(0, '#', width=40)
        self.MOVES.InsertColumn(1, 'HEX', width=50)
        self.MOVES.InsertColumn(2, 'Name', width=120)
        moves_vbox.Add(self.MOVES, 0, wx.EXPAND | wx.ALL, 5)
        
        moves_butons_vbox = wx.BoxSizer(wx.VERTICAL)
        global MOVES_LIST
        self.MOVE_NAME = ComboBox(self, -1, choices=MOVES_LIST,
                                style=wx.SUNKEN_BORDER, size=(100, -1))
        moves_butons_vbox.Add(self.MOVE_NAME, 0, wx.EXPAND | wx.ALL, 5)
        
        ADD_POKE =  Button(self, 3, "Add Move")
        self.Bind(wx.EVT_BUTTON, self.OnAddMove, id=3)
        moves_butons_vbox.Add(ADD_POKE, 0, wx.EXPAND | wx.ALL, 5)

        DELETE_POKE =  Button(self, 4, "Remove Move")
        self.Bind(wx.EVT_BUTTON, self.OnDeleteMove, id=4)
        moves_butons_vbox.Add(DELETE_POKE, 0, wx.EXPAND | wx.ALL, 5)
        
        MOVE_UP = Button(self, 5, "Move Up")
        self.Bind(wx.EVT_BUTTON, self.OnMoveUp, id=5)
        moves_butons_vbox.Add(MOVE_UP, 0, wx.EXPAND | wx.ALL, 5)
        
        MOVE_DOWN = Button(self, 6, "Move Down")
        self.Bind(wx.EVT_BUTTON, self.OnMoveDown, id=6)
        moves_butons_vbox.Add(MOVE_DOWN, 0, wx.EXPAND | wx.ALL, 5)
        
        sizer.Add(names_buttons_vbox, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(poke_names_vbox, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(moves_vbox, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(moves_butons_vbox, 0, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(sizer)
        
    def save(self):
        string = ""
        eggmovelimit = int(Globals.INI.get(Globals.OpenRomID, "eggmovelimit"), 0)
        NewEggOffset = hex(self.OFFSET)[2:].zfill(6)
        for poke, moveset in self.EGG_MOVES.iteritems():
            number = int("0x4E20", 0)
            pokemon = hex(poke+number)[2:].zfill(4)
            pokemon = pokemon[2:]+pokemon[:2]
            string += pokemon
            for move in moveset:
                move = hex(move)[2:].zfill(4)
                move = move[2:]+move[:2]
                string += move
        string += "ffff0000"
        self.string_to_be_written = get_hex_from_string(string)
        length = len(string)
        if length > self.original_length:
            self.repoint = EGG_MOVE_REPOINTER(parent=None, need=int(length/2))
            while True:
                if self.repoint.ShowModal() == wx.ID_OK:
                    Offset = self.repoint.NewEggOffset
                    wx.CallAfter(self.repoint.Destroy)
                    if self.OFFSET == Offset: continue
                    else: 
                        NewEggOffset = Offset
                        with open(Globals.OpenRomName, "r+b") as rom:
                            rom.seek(eggmovelimit)
                            writeLength = int((length/2-3))
                            writeLength = hex(writeLength).lstrip("0x").rstrip("L").zfill(8)
                            writeLength = get_hex_from_string(writeLength)[::-1]
                            rom.write(writeLength)
                        break
                else: return
        offset = int(NewEggOffset,16)+int("8000000",16)
        offset = hex(offset)[2:].zfill(8)
        with open(Globals.OpenRomName, "r+b") as rom:
            NewEggOffset_pointer_form = make_pointer(offset)
            if NewEggOffset != hex(self.OFFSET)[2:].zfill(6):
                for pointer in self.POINTERS:
                    rom.seek(pointer)
                    rom.write(get_hex_from_string(NewEggOffset_pointer_form))
            
            #Fill old table with FFs
            if self.OFFSET != NewEggOffset:
                rom.seek(self.OFFSET)
                for n in range(int(self.original_length/2)):
                    rom.write("\xff")
            
            NewEggOffset = int(NewEggOffset, 16)
            rom.seek(NewEggOffset)
            rom.write(self.string_to_be_written)
        
    def OnSelectPoke(self, *args):
        global MOVES_LIST
        self.MOVES.DeleteAllItems()
        
        selection = self.POKES.GetFocusedItem()
        if selection != -1:
            selection = self.POKES.GetItem(selection, 0)
            selection = int(selection.GetText())
            
            for move in self.EGG_MOVES[selection]:
                index = self.MOVES.InsertStringItem(sys.maxint, str(move))
                HexMove = hex(move)
                HexMove = HexMove[:2]+HexMove[2:].upper()
                self.MOVES.SetStringItem(index, 1, HexMove)
                self.MOVES.SetStringItem(index, 2, MOVES_LIST[move])
    
    def OnAddPoke(self, *args):
        sel = self.POKE_NAME.GetSelection()
        if sel != -1:
            if sel not in self.EGG_MOVES:
                self.EGG_MOVES[sel] = []
                self.LoadPOKESList()
            
    def OnDeletePoke(self, *args):
        selection = self.POKES.GetFocusedItem()
        index = selection
        Current = str(self.POKES.GetItemCount())
        if selection != -1:
            selection = self.POKES.GetItem(selection, 0)
            selection = int(selection.GetText())
            
            del self.EGG_MOVES[selection]
            self.LoadPOKESList()
            if index == Current:
                self.POKES.Select(index-1)
                self.POKES.Focus(index-1)
            else:
                self.POKES.Focus(index)
                self.POKES.Select(index)
            
    def OnAddMove(self, *args):
        selection = self.POKES.GetFocusedItem()
        if selection != -1:
            selection = self.POKES.GetItem(selection, 0)
            selection = int(selection.GetText())
            
            sel = self.MOVE_NAME.GetSelection()
            if sel != -1:
                if sel not in self.EGG_MOVES[selection]:
                    self.EGG_MOVES[selection].append(sel)
            self.OnSelectPoke()
            end = len(self.EGG_MOVES[selection])-1
            self.MOVES.Select(end)
            self.MOVES.Focus(end)
        
    def OnDeleteMove(self, *args):
        selection = self.POKES.GetFocusedItem()
        if selection != -1:
            selection = self.POKES.GetItem(selection, 0)
            selection = int(selection.GetText())
            
            move_to_delete = self.MOVES.GetFocusedItem()
            index = move_to_delete
            if move_to_delete != -1:
                move_to_delete = self.MOVES.GetItem(move_to_delete, 0)
                move_to_delete = int(move_to_delete.GetText())

                self.EGG_MOVES[selection].remove(move_to_delete)
            
                self.OnSelectPoke()
                self.MOVES.Select(index)
                self.MOVES.Focus(index)
                
    def OnMoveUp(self, *args):
        move = self.MOVES.GetFocusedItem()
        if move != -1:
            move = self.MOVES.GetItem(move, 0)
            move = int(move.GetText())

            selection = self.POKES.GetFocusedItem()
            selection = self.POKES.GetItem(selection, 0)
            selection = int(selection.GetText())
            
            index = self.EGG_MOVES[selection].index(move)
            if index > 0:
                self.EGG_MOVES[selection][index], self.EGG_MOVES[selection][index-1] = self.EGG_MOVES[selection][index-1], self.EGG_MOVES[selection][index]
                self.OnSelectPoke()
                self.MOVES.Select(index-1)
                self.MOVES.Focus(index-1)
                
    def OnMoveDown(self, *args):
        move = self.MOVES.GetFocusedItem()
        if move != -1:
            move = self.MOVES.GetItem(move, 0)
            move = int(move.GetText())

            selection = self.POKES.GetFocusedItem()
            selection = self.POKES.GetItem(selection, 0)
            selection = int(selection.GetText())
            
            index = self.EGG_MOVES[selection].index(move)
            if index < len(self.EGG_MOVES[selection])-1:
                self.EGG_MOVES[selection][index], self.EGG_MOVES[selection][index+1] = self.EGG_MOVES[selection][index+1], self.EGG_MOVES[selection][index]
                self.OnSelectPoke()
                self.MOVES.Select(index+1)
                self.MOVES.Focus(index+1)
        
    def LoadPOKESList(self):
        
        self.POKES.DeleteAllItems()
        for poke in self.EGG_MOVES:
            index = self.POKES.InsertStringItem(sys.maxint, str(poke))
            HexPoke = hex(poke)
            HexPoke = HexPoke[:2]+HexPoke[2:].upper()
            self.POKES.SetStringItem(index, 1, HexPoke)
            self.POKES.SetStringItem(index, 2, Globals.PokeNames[poke])
        
    def load_egg_moves(self):
        self.EGG_MOVES = {}
        
        self.POINTERS = [int(Globals.INI.get(Globals.OpenRomID, "EggMovePointer1"), 0), int(Globals.INI.get(Globals.OpenRomID, "EggMovePointer2"), 0)]
        with open(Globals.OpenRomName, "r+b") as rom:
            rom.seek(self.POINTERS[0])
            self.OFFSET = read_pointer(rom.read(4))
            
            rom.seek(self.OFFSET, 0)
            number = int("0x4E20", 0)
            while True:
                read = rom.read(2)
                read = read[1]+read[0]
                if read == "\xff\xff":
                    break
                read = int(get_bytes_string_from_hex_string(read), 16)
                
                if read-number >= 0:
                    poke = read-number
                    self.EGG_MOVES[poke] = []
                else:
                    self.EGG_MOVES[poke].append(read)
                    
            string = ""
            for poke, moveset in self.EGG_MOVES.iteritems():
                number = int("0x4E20", 0)
                pokemon = hex(poke+number)[2:].zfill(4)
                pokemon = pokemon[2:]+pokemon[:2]
                string += pokemon
                for move in moveset:
                    move = hex(move)[2:].zfill(4)
                    move = move[2:]+move[:2]
                    string += move
            string += "ffff0000"
            self.original_length = len(string)
                            
                        
#############################################################
##---------------------Extra Dialogues---------------------##
#############################################################

class MOVE_REPOINTER(wx.Dialog):
    def __init__(self, parent, *args, **kw):
        wx.Dialog.__init__(self, parent=parent, id=wx.ID_ANY)
        self.SetWindowStyle( self.GetWindowStyle() | wx.RESIZE_BORDER )
        
        self.num = None
        
        self.InitUI()
        self.SetTitle("Repoint")
        
    def InitUI(self):
        pnl = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        txt = wx.StaticText(pnl, -1, "How many moves would you like the\nnew move set to be?")
        vbox.Add(txt, 0, wx.EXPAND | wx.ALL, 5)
        
        self.New_Move_Num = wx.TextCtrl(pnl, -1,style=wx.TE_CENTRE, size=(50,-1))
        vbox.Add(self.New_Move_Num, 0, wx.EXPAND | wx.ALL, 5)
        
        SEARCH = Button(pnl, 1, "Search")
        self.Bind(wx.EVT_BUTTON, self.OnSearch, id=1)
        vbox.Add(SEARCH, 0, wx.EXPAND | wx.ALL, 5)
        
        txt2 = wx.StaticText(pnl, -1, "Please choose an offset to repoint to or specify\na manual offset. If a manual offset is specified,\nthe list choice will be ignored.\nNOTE: Manual offsets will NOT be checked for\nfree space availability.\nFor both, please provide the number of moves you\nexpect. It will not continue without it.",style=wx.TE_CENTRE)
        vbox.Add(txt2, 0, wx.EXPAND | wx.ALL, 5)
        
        self.OFFSETS = wx.ListBox(pnl, -1)
        vbox.Add(self.OFFSETS, 0, wx.EXPAND | wx.ALL, 5)
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        manual_txt = wx.StaticText(pnl, -1, "Manual Offset: 0x",style=wx.TE_CENTRE)
        hbox.Add(manual_txt, 0, wx.EXPAND | wx.LEFT|wx.TOP|wx.BOTTOM, 5)
        self.MANUAL = wx.TextCtrl(pnl, -1,style=wx.TE_CENTRE, size=(100,-1))
        hbox.Add(self.MANUAL, 0, wx.EXPAND | wx.RIGHT|wx.TOP|wx.BOTTOM, 5)
        vbox.Add(hbox, 0, wx.EXPAND | wx.ALL, 0)
        
        self.cb = wx.CheckBox(pnl, -1, 'Fill old table with 0xFF?', (10, 10))
        self.cb.SetValue(True)
        vbox.Add(self.cb, 0, wx.ALL|wx.ALIGN_CENTER, 5)
        
        SUBMIT = Button(pnl, 2, "Submit")
        self.Bind(wx.EVT_BUTTON, self.OnSubmit, id=2)
        vbox.Add(SUBMIT, 0, wx.EXPAND | wx.ALL, 5)
        
        pnl.SetSizerAndFit(vbox)
        self.Fit()
        self.SetMinSize(self.GetEffectiveMinSize())
        
    def OnSubmit(self, *args):
        sel = self.OFFSETS.GetSelection()
        offset = self.MANUAL.GetValue()
        new_offset = None
        if self.num == None:
            try: self.num = int(self.New_Move_Num.GetValue(), 0)
            except: return
        if offset != "":
            if len(offset) > 6:
                check = offset[-7:-6]
                if check == "1" or check == "9":
                    check = "1"
                else:
                    check = ""
                offset = check+offset[-6:].zfill(6)
            new_offset = offset.zfill(6)
            frame.tabbed_area.PokeDataTab.tabbed_area.moves.NEW_LEARNED_OFFSET = new_offset
            frame.tabbed_area.PokeDataTab.tabbed_area.moves.LEARNED_OFFSET.SetLabel("0x"+new_offset)
            frame.tabbed_area.PokeDataTab.tabbed_area.moves.NEW_NUMBER_OF_MOVES = self.num
            frame.tabbed_area.PokeDataTab.tabbed_area.moves.UPDATE_FRACTION()
        elif sel != -1:
            new_offset = self.OFFSETS.GetString(sel)[2:]
            frame.tabbed_area.PokeDataTab.tabbed_area.moves.NEW_LEARNED_OFFSET = new_offset
            frame.tabbed_area.PokeDataTab.tabbed_area.moves.LEARNED_OFFSET.SetLabel("0x"+new_offset)
            frame.tabbed_area.PokeDataTab.tabbed_area.moves.NEW_NUMBER_OF_MOVES = self.num
            frame.tabbed_area.PokeDataTab.tabbed_area.moves.UPDATE_FRACTION()
        if new_offset != None:
            learned_moves_pointer = int(Globals.INI.get(Globals.OpenRomID, "LearnedMoves"), 0)
            int_offset = int(new_offset,16)+int("8000000",16)
            offset = hex(int_offset)[2:].zfill(8)
            pointer = make_pointer(offset)
            pointer = get_hex_from_string(pointer)
            global poke_num
            offset_of_pointer = learned_moves_pointer+(poke_num)*4
            with open(Globals.OpenRomName, "r+b") as rom:
                rom.seek(offset_of_pointer)
                rom.write(pointer)
                
                rom.seek(int(new_offset,16))
                Jambo51HackCheck = Globals.INI.get(Globals.OpenRomID, "Jambo51LearnedMoveHack")
                if Jambo51HackCheck == "False":
                    learnedmoveslength = int(Globals.INI.get(Globals.OpenRomID, "learnedmoveslength"), 0)
                    amount_of_bytes = self.num*learnedmoveslength
                    for n in range(int(amount_of_bytes/2)):
                        rom.write("\x00\xCA")
                    rom.write("\xff\xff\xfe\xfe")
                else:
                    amount_of_bytes = self.num*3
                    for n in range(int(amount_of_bytes/2)):
                        rom.write("\x00\xCA")
                    rom.write("\xff\xff\xff\xfe")
            
            self.OnClose()
            
    def OnSearch(self, *args):
        self.OFFSETS.Clear()
        try:
            self.num = int(self.New_Move_Num.GetValue(), 0)
        except:
            return
        search = "\xff\xff"*self.num
        with open(Globals.OpenRomName, "r+b") as rom:
            rom.seek(0)
            read = rom.read()
            x = (0,True)
            start = 7602176
            for n in range(5):
                if x[1] == None:
                    break
                x = (0,True)
                while x[0] != 1:
                    offset = read.find(search, start)
                    if offset == -1:
                        x = (1,None)
                    if offset%4 != 0:
                        start = offset+1
                        continue
                    if read[offset-1] != "\xFF":
                        start = offset+1
                        continue
                    self.OFFSETS.Append(hex(offset))
                    x = (1,True)
                    start = offset+len(search)
                
    def OnClose(self, *args):
        wx.CallAfter(self.Close)

class EGG_MOVE_REPOINTER(wx.Dialog):
    def __init__(self, parent, need, *args, **kw):
        wx.Dialog.__init__(self, parent=parent, id=wx.ID_ANY)
        self.SetWindowStyle( self.GetWindowStyle() | wx.STAY_ON_TOP | wx.RESIZE_BORDER )
        self.NewEggOffset = None
        self.num = need
        self.InitUI()
        self.OnSearch()
        self.SetTitle("Repoint Egg Moves")

    def InitUI(self):
        pnl = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        txt2 = wx.StaticText(pnl, -1, "Egg Moves need to be repointed.\n\n\nPlease choose an offset to repoint to or specify\na manual offset. If a manual offset is specified,\nthe list choice will be ignored.\nNOTE: Manual offsets will NOT be checked for\nfree space availability.",style=wx.TE_CENTRE)
        vbox.Add(txt2, 0, wx.EXPAND | wx.ALL, 5)
        
        self.OFFSETS = wx.ListBox(pnl, -1)
        vbox.Add(self.OFFSETS, 0, wx.EXPAND | wx.ALL, 5)
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        manual_txt = wx.StaticText(pnl, -1, "Manual Offset: 0x",style=wx.TE_CENTRE)
        hbox.Add(manual_txt, 0, wx.EXPAND | wx.LEFT|wx.TOP|wx.BOTTOM, 5)
        self.MANUAL = wx.TextCtrl(pnl, -1,style=wx.TE_CENTRE, size=(100,-1))
        hbox.Add(self.MANUAL, 0, wx.EXPAND | wx.RIGHT|wx.TOP|wx.BOTTOM, 5)
        vbox.Add(hbox, 0, wx.EXPAND | wx.ALL, 0)
        
        SUBMIT = Button(pnl, 2, "Submit")
        self.Bind(wx.EVT_BUTTON, self.OnSubmit, id=2)
        vbox.Add(SUBMIT, 0, wx.EXPAND | wx.ALL, 5)
        
        pnl.SetSizerAndFit(vbox)
        self.Fit()
        self.SetMinSize(self.GetEffectiveMinSize())
        
    def OnSubmit(self, *args):
        sel = self.OFFSETS.GetSelection()
        offset = self.MANUAL.GetValue()
        
        if offset != "":
            if len(offset) > 6:
                check = offset[-7:-6]
                if check == "1" or check == "9":
                    check = "1"
                else:
                    check = ""
                offset = check+offset[-6:].zfill(6)
            self.NewEggOffset = offset
            self.EndModal(wx.ID_OK)
        elif sel != -1:
            new_offset = self.OFFSETS.GetString(sel)[2:]
            self.NewEggOffset = new_offset
            self.EndModal(wx.ID_OK)
        
    def OnSearch(self, *args):
        self.OFFSETS.Clear()
        search = "\xff"*self.num
        with open(Globals.OpenRomName, "r+b") as rom:
            rom.seek(0)
            read = rom.read()
            x = (0,True)
            start = 7602176
            for n in range(5):
                if x[1] == None:
                    break
                x = (0,True)
                while x[0] != 1:
                    offset = read.find(search, start)
                    if offset == -1:
                        x = (1,None)
                    if offset%4 != 0:
                        start = offset+1
                        continue
                    self.OFFSETS.Append(hex(offset))
                    x = (1,True)
                    start = offset+len(search)
                
class NumberofEvosChanger(wx.Dialog):
    def __init__(self, parent=None, *args, **kw):
        wx.Dialog.__init__(self, parent=parent, id=wx.ID_ANY)
        self.SetWindowStyle( self.GetWindowStyle() | wx.STAY_ON_TOP | wx.RESIZE_BORDER )
        

        self.InitUI()
        self.SetTitle("Change Number of Evolutions per 'MON")
        self.ShowModal()
        
    def InitUI(self):
        pnl = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        txt = wx.StaticText(pnl, -1, "This is the first ever tool to change the number of\nevolutions a 'MON can have. Due to ASM limitations,\nthe number of new evolutions has to be a power of 2\nor just 5. Anything else requires custom ASM that\nwould require a repoint of a lot of things. So, let's get\nstarted!\n\n\nPlease pick a new number of evolutions:",style=wx.TE_CENTRE)
        vbox.Add(txt, 0, wx.EXPAND | wx.ALL, 5)
        
        self.choices = ["4","5","8","16","32"]
        
        self.NewNumberChoices = ComboBox(pnl, -1, choices=self.choices,
                                                    style=wx.SUNKEN_BORDER, size=(100, -1))
        vbox.Add(self.NewNumberChoices, 0, wx.EXPAND | wx.ALL, 5)
        
        txt2 = wx.StaticText(pnl, -1, "Now, you can either search for a free space offset or\n specify a manual offset for the new table.\nNOTE: Manual offsets are not checked\nfor free space content.",style=wx.TE_CENTRE)
        vbox.Add(txt2, 0, wx.EXPAND | wx.ALL, 5)
        
        self.OFFSETS = wx.ListBox(pnl, -1)
        vbox.Add(self.OFFSETS, 0, wx.EXPAND | wx.ALL, 5)
        
        SEARCH = Button(pnl, 1, "Search")
        self.Bind(wx.EVT_BUTTON, self.OnSearch, id=1)
        vbox.Add(SEARCH, 0, wx.EXPAND | wx.ALL, 5)
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        manual_txt = wx.StaticText(pnl, -1, "Manual Offset: 0x",style=wx.TE_CENTRE)
        hbox.Add(manual_txt, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        self.MANUAL = wx.TextCtrl(pnl, -1,style=wx.TE_CENTRE, size=(100,-1))
        hbox.Add(self.MANUAL, 0, wx.ALL | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        vbox.Add(hbox, 0, wx.EXPAND | wx.ALL, 0)
        
        SUBMIT = Button(pnl, 2, "Submit")
        self.Bind(wx.EVT_BUTTON, self.OnSubmit, id=2)
        vbox.Add(SUBMIT, 0, wx.EXPAND | wx.ALL, 5)
        
        txt3 = wx.StaticText(pnl, -1, "\n\nA huge credit goes to DoesntKnowHowToPlay, who\ndiscovered how this can be done and kept notes\nabout it. Drop him a thank you if you really like it!",style=wx.TE_CENTRE)
        vbox.Add(txt3, 0, wx.EXPAND | wx.ALL, 5)
        
        pnl.SetSizerAndFit(vbox)
        self.Fit()
        self.SetMinSize(self.GetEffectiveMinSize())
    
    def OnSubmit(self, *args):
        sel = self.OFFSETS.GetSelection()
        _offset_ = self.MANUAL.GetValue()
        new_number = self.NewNumberChoices.GetSelection()
        new_number = int(self.choices[new_number])
        EvolutionsPerPoke = int(Globals.INI.get(Globals.OpenRomID, "EvolutionsPerPoke"), 0)
        if new_number == EvolutionsPerPoke: 
            ComeOn = wx.MessageDialog(self, 
                                "Look, you are supposed to change the number of evolutions. Haha, everyone makes mistakes. I would pick a different number.", 
                                "What's the purpose?",
                                wx.OK)
            ComeOn.ShowModal()
            return
        if _offset_ != "":
            if len(_offset_) > 6:
                check = _offset_[-7:-6]
                if check == "1" or check == "9":
                    check = "1"
                else:
                    check = ""
                _offset_ = check+_offset_[-6:].zfill(6)
        elif sel != -1:
            _offset_ = self.OFFSETS.GetString(sel)[2:]
        else: return

        ##copy table
        LengthOfOneEntry = int(Globals.INI.get(Globals.OpenRomID, "LengthOfOneEntry"), 0)
        EvolutionTable = int(Globals.INI.get(Globals.OpenRomID, "EvolutionTable"), 0)
        numberofpokes = int(Globals.INI.get(Globals.OpenRomID, "numberofpokes"), 0)
        
        readlength = EvolutionsPerPoke*LengthOfOneEntry*numberofpokes
        
        with open(Globals.OpenRomName, "r+b") as rom:
            rom.seek(EvolutionTable)
            entiretable = rom.read(readlength)

            table = []
            
            if new_number < EvolutionsPerPoke:
                while entiretable != "":
                    split = entiretable[:LengthOfOneEntry*EvolutionsPerPoke]
                    split = split[:new_number*LengthOfOneEntry]
                    table.append(split)
                    entiretable = entiretable[LengthOfOneEntry*EvolutionsPerPoke:]
            else:
                while entiretable != "":
                    split = entiretable[:LengthOfOneEntry*EvolutionsPerPoke]
                    split += "\x00"*(LengthOfOneEntry)*(new_number-EvolutionsPerPoke)
                    table.append(split)
                    entiretable = entiretable[LengthOfOneEntry*EvolutionsPerPoke:]
            int_offset = int(_offset_, 16)
            rom.seek(int_offset)
            for entry in table:
                rom.write(entry)
        ##write new pointers.
        EvolutionTablePointers = []
        list_pointers = Globals.INI.get(Globals.OpenRomID, "EvolutionTablePointers").split(",")
        
        for offset in list_pointers:
            EvolutionTablePointers.append(int(offset, 0))
        
        _offset_ = int(_offset_,16)+0x8000000
        _offset_ = hex(_offset_).lstrip("0x").rstrip("L").zfill(8)
        
        pointer = make_pointer(_offset_)
        pointer = get_hex_from_string(pointer)
        
        with open(Globals.OpenRomName, "r+b") as rom:
            for offset in EvolutionTablePointers:
                rom.seek(offset)
                rom.write(pointer)
        ##Ammend the ini
        
        _offset_ = int(_offset_,16)-0x8000000
        _offset_ = hex(_offset_).rstrip("L")
        
        Globals.INI.set(Globals.OpenRomID, "EvolutionTable", _offset_)
        Globals.INI.set(Globals.OpenRomID, "EvolutionsPerPoke", str(new_number))
        
        with open("PokeRoms.ini", "w") as PokeRomsIni:
            Globals.INI.write(PokeRomsIni)
        
        ##fill table with FF
        with open(Globals.OpenRomName, "r+b") as rom:
            rom.seek(EvolutionTable)
            for n in range(readlength):
                rom.write("\xFF")
        ##Adjust the rom for the new table
        change1 = [] #-> lsl r0, r6, #0x1 (70 00)
        tmp = Globals.INI.get(Globals.OpenRomID, "OffsetsToChangeTolslr0r60x1").split(",")
        for offset in tmp:
            change1.append(int(offset, 0))
        if new_number == 4: write = "3000"
        elif new_number == 8: write = "7000"
        elif new_number == 16: write = "B000"
        elif new_number == 32: write = "F000"
        else: write = "F019"
        
        change1write = unhexlify(write)
        
        with open(Globals.OpenRomName, "r+b") as rom:
            for offset in change1:
                rom.seek(offset, 0)
                rom.write(change1write)
            
        change2 = [] #04 -> 07
        tmp = Globals.INI.get(Globals.OpenRomID, "OffsetsToChangeToNewMinus1").split(",")
        for offset in tmp:
            change2.append(int(offset, 0))

        change2write = get_hex_from_string(str(hex(new_number-1)[2:]))
        
        with open(Globals.OpenRomName, "r+b") as rom:
            for offset in change2:
                rom.seek(offset, 0)
                rom.write(change2write)
            
        TheShedinjaFix = int(Globals.INI.get(Globals.OpenRomID, "LengthOfOneEntry"), 0)
        code = Globals.INI.get(Globals.OpenRomID, "gamecode")
        
        if code != "AXVE" and code != "AXPE":
            if new_number == 4: write = "0000"
            elif new_number == 8: write = "4000"
            elif new_number == 16: write = "8000"
            elif new_number == 32: write = "C000"
            else: write = "5044"
        else:
            if new_number == 4: write = "B90089460000"
            elif new_number == 8: write = "F90089460000"
            elif new_number == 16: write = "390189460000"
            elif new_number == 32: write = "790189460000"
            else: write = "B9008946C819"
            
        TheShedinjaFixWrite = unhexlify(write)
        
        with open(Globals.OpenRomName, "r+b") as rom:
            rom.seek(TheShedinjaFix, 0)
            rom.write(TheShedinjaFixWrite)
        
        change3 = []
        tmp = Globals.INI.get(Globals.OpenRomID, "ChangeToNewNumberTimes8").split(",")
        for offset in tmp:
            change3.append(int(offset, 0))

        change3write = get_hex_from_string(str(hex(new_number*8)[2:]))
        
        with open(Globals.OpenRomName, "r+b") as rom:
            for offset in change3:
                rom.seek(offset, 0)
                rom.write(change3write)
            
            ##Tell the user it worked, close, and reload data.
            #Small fix for some weird bytes that get written. Shhh, don't tell anyone.....
            rom.seek(8)
            rom.write("\x69\x9A")
        
        self.OnClose()
        DONE = wx.MessageDialog(None, 
                                "Table has been moved, ini has been ammended,\nand evolutions have been changed.:)\n\n\nReloading 'MON Data.", 
                                "Done!",
                                wx.OK)
        DONE.ShowModal()
        frame.tabbed_area.PokeDataTab.tabbed_area.reload_tab_data()
        
    def OnSearch(self, *args):
        #EvolutionsPerPoke = int(Globals.INI.get(Globals.OpenRomID, "EvolutionsPerPoke"), 0)
        LengthOfOneEntry = int(Globals.INI.get(Globals.OpenRomID, "LengthOfOneEntry"), 0)
        numberofpokes = int(Globals.INI.get(Globals.OpenRomID, "numberofpokes"), 0)
        
        NewEvolutionsPerPoke = self.NewNumberChoices.GetSelection()
        if NewEvolutionsPerPoke == -1:
            return
        NewEvolutionsPerPoke = int(self.choices[NewEvolutionsPerPoke])
        
        length = LengthOfOneEntry*NewEvolutionsPerPoke*numberofpokes
        
        self.OFFSETS.Clear()
        search = "\xff"*length
        with open(Globals.OpenRomName, "r+b") as rom:
            rom.seek(0)
            read = rom.read()
            x = (0,True)
            start = 7602176
            for n in range(5):
                if x[1] == None:
                    break
                x = (0,True)
                while x[0] != 1:
                    offset = read.find(search, start)
                    if offset == -1:
                        x = (1,None)
                    if offset%4 != 0:
                        start = offset+1
                        continue
                    if read[offset-1] != "\xFF":
                        start = offset+1
                        continue
                    self.OFFSETS.Append(hex(offset))
                    x = (1,True)
                    start = offset+len(search)
                
    def OnClose(self, *args):
        self.Close()
        
class POKEDEXEntryRepointer(wx.Dialog):
    def __init__(self, parent=None, need=None, repoint_what=None, *args, **kw):
        wx.Dialog.__init__(self, parent=parent, id=wx.ID_ANY)
        self.SetWindowStyle( self.GetWindowStyle() | wx.STAY_ON_TOP | wx.RESIZE_BORDER )
        
        self.num = need
        self.repoint = repoint_what

        self.InitUI()
        self.OnSearch()
        self.SetTitle("Repoint 'Dex Entry")
        
    def InitUI(self):
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        txt = wx.StaticText(self, -1, self.repoint+" needs to be repointed.\n\n",style=wx.TE_CENTRE)
        vbox.Add(txt, 0, wx.EXPAND | wx.ALL, 5)
        
        txt2 = wx.StaticText(self, -1, "Please choose an offset to repoint to or specify\na manual offset. If a manual offset is specified,\nthe list choice will be ignored.\nNOTE: Manual offsets will NOT be checked for\nfree space availability.",style=wx.TE_CENTRE)
        vbox.Add(txt2, 0, wx.EXPAND | wx.ALL, 5)
        
        self.OFFSETS = wx.ListBox(self, -1)
        self.OFFSETS.Bind(wx.EVT_LISTBOX, self.GetOffset)
        vbox.Add(self.OFFSETS, 0, wx.EXPAND | wx.ALL, 5)
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        manual_txt = wx.StaticText(self, -1, "Manual Offset: 0x",style=wx.TE_CENTRE)
        hbox.Add(manual_txt, 0, wx.EXPAND | wx.LEFT|wx.TOP|wx.BOTTOM, 5)
        self.MANUAL = wx.TextCtrl(self, -1,style=wx.TE_CENTRE, size=(100,-1))
        self.MANUAL.Bind(wx.EVT_TEXT, self.GetOffset)
        hbox.Add(self.MANUAL, 0, wx.EXPAND | wx.RIGHT|wx.TOP|wx.BOTTOM, 5)
        vbox.Add(hbox, 0, wx.EXPAND | wx.ALL, 0)
        
        self.cb = wx.CheckBox(self, -1, 'Fill old entry with 0xFF?', (10, 10))
        self.cb.SetValue(True)
        vbox.Add(self.cb, 0, wx.ALL|wx.ALIGN_CENTER, 5)
        
        OK = self.CreateButtonSizer(wx.OK)
        vbox.Add(OK, 0, wx.EXPAND | wx.ALL, 5)
        
        txt3 = wx.StaticText(self, -1, "______________________________",style=wx.TE_CENTRE)
        vbox.Add(txt3, 0, wx.EXPAND | wx.ALL, 15)
        
        self.SetSizerAndFit(vbox)
        self.Fit()
        self.SetMinSize(self.GetEffectiveMinSize())
        
    def GetOffset(self, *args):
        global returned_offset
        sel = self.OFFSETS.GetSelection()
        _offset_ = self.MANUAL.GetValue()
        
        if _offset_ != "":
            if len(_offset_) > 6:
                check = _offset_[-7:-6]
                if check == "1" or check == "9":
                    check = "1"
                else:
                    check = ""
                _offset_ = check+_offset_[-6:].zfill(6)
        elif sel != -1:
            _offset_ = self.OFFSETS.GetString(sel)[2:]
        else: return
        
        try: int(_offset_, 16)
        except: return
        b = wx.StaticBox(pnl, label='Colors')
        sbs = wx.StaticBoxSizer(sb, orient=wx.VERTICAL)        
        sbs.Add(wx.RadioButton(pnl, label='256 Colors', 
            style=wx.RB_GROUP))
        sbs.Add(wx.RadioButton(pnl, label='16 Colors'))
        sbs.Add(wx.RadioButton(pnl, label='2 Colors'))
        returned_offset = _offset_

    def OnSearch(self, *args):
        self.OFFSETS.Clear()
        search = "\xff"*self.num
        with open(Globals.OpenRomName, "r+b") as rom:
            rom.seek(0)
            read = rom.read()
            x = (0,True)
            start = 7602176
            for n in range(5):
                if x[1] == None:
                    break
                x = (0,True)
                while x[0] != 1:
                    offset = read.find(search, start)
                    if offset == -1:
                        x = (1,None)
                    if offset%4 != 0:
                        start = offset+1
                        continue
                    if read[offset-1] != "\xFF":
                        start = offset+1
                        continue
                    self.OFFSETS.Append(hex(offset))
                    x = (1,True)
                    start = offset+len(search)

def OnClose(instance):
    sys.exit()

def OnUpdateTimer(instance):
    global timer
    timer.Stop()
    del timer
    global LatestGoodBuild
    if UseDevBuild == False:
        Globals.latestRelease = LatestGoodBuild
    Message = "An update is available for this suite:\n\n"
    Message += "Version: "+Globals.latestRelease["name"]+"\n\n"
    Message += "Updates:\n"+Globals.latestRelease["body"]+"\n\n"
    if Globals.latestRelease["prerelease"] == True:
        Message += "Please note that this is a prerelease and may not work properly.\n\n"
    Message +="Would you like to update?"
    Updater = UpdateDialog(frame,Message)
        

def OnMessageTimer(instance):
    global Msgtimer
    Msgtimer.Stop()
    del Msgtimer
    global MSG
    MSG = textwrap.fill(MSG,110)
    Message = "A message from karatekid552:\n\n"+MSG
    UpdateDialog = wx.MessageDialog(None,Message,"Message", wx.OK)
    UpdateDialog.ShowModal()

def DetermineHigherVersion(new, old):
    new = new.lstrip("v").split(".")
    old = old.lstrip("v").split(".")
    for n, v in enumerate(new):
        new[n] = int(new[n],16)
    for n, v in enumerate(old):
        old[n] = int(old[n],16)
    h = False
    for num, v in enumerate(new):
        try: old[num]
        except: 
            if h: return False
            else: return True
        if old[num] >= v:
            h = True
            continue
        elif old[num] < v:
            return True
        return False
        

app = wx.App(False)
name = "POK\xe9MON Gen III Hacking Suite"
name = encode_per_platform(name)
frame = MainWindow(None, name)
frame.Bind(wx.EVT_CLOSE, OnClose)
if len(sys.argv) > 1:
    file = sys.argv[1]
    frame.open_rom = open(file, "r+b")
    Globals.OpenRomName = file
    frame.work_with_ini()

try:
    checkforupdates = Globals.INI.get("ALL", "checkforupdates")
    if checkforupdates == "True":
        r = urllib2.Request('https://api.github.com/repos/thekaratekid552/Secret-Tool/releases')
        response = urllib2.urlopen(r)
        obj = response.read()
        obj = json.loads(obj)
        Globals.latestRelease = obj[0]
        LatestGoodBuild = None
        timer = None
        UseDevBuild = False
        for x in obj:
            if x["prerelease"] != True:
                LatestGoodBuild = x
                break
        CheckForDevBuilds = Globals.INI.get("ALL", "CheckForDevBuilds")
        if DetermineHigherVersion(Globals.latestRelease["tag_name"],Globals.VersionNumber):
            if Globals.latestRelease["prerelease"] != True or CheckForDevBuilds == "True":
                UseDevBuild = True
                timer = wx.Timer(frame, 99)
                timer.Start(500)
                wx.EVT_TIMER(frame, 99, OnUpdateTimer)
        if not timer:
            if LatestGoodBuild:
                if DetermineHigherVersion(LatestGoodBuild["tag_name"],Globals.VersionNumber):
                    UseDevBuild = False
                    timer = wx.Timer(frame, 99)
                    timer.Start(500)
                    wx.EVT_TIMER(frame, 99, OnUpdateTimer)
except: pass
#If I need to send everyone a message, this is the place.
try:
    r = urllib2.Request("https://raw.github.com/thekaratekid552/Secret-Tool/master/Message.txt")
    MSGresponse = urllib2.urlopen(r)
    MSG = MSGresponse.read()
    if MSG != "":
        Msgtimer = wx.Timer(frame, 98)
        Msgtimer.Start(500)
        wx.EVT_TIMER(frame, 98, OnMessageTimer)
except: pass


sys.stderr = StringIO()
frame.set_timer()
app.MainLoop()
