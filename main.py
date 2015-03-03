#!/bin/env python2
# -*- coding: utf-8 -*-
#venv pyi-env-name
from __future__ import division
import wx, os, ConfigParser, sys, textwrap, platform
from lib.Tools.rom_insertion_operations import *
from lib.OverLoad.CheckListCtrl import *
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
from lib.Tools.IniMerger import MergerPrompt

##
def start_pdb(signal, trace):
    import pdb
    pdb.set_trace()

import signal
signal.signal(signal.SIGQUIT, start_pdb)
##

try:
    from wx.lib.pubsub import Publisher as pub
except:
    print "Changing pub mode"
    from wx.lib.pubsub import setuparg1
    from wx.lib.pubsub import pub

from GLOBALS import *

from pokemondataeditor import PokemonDataEditor

OPEN = 1
poke_num = 0
MOVES_LIST = None
ITEM_NAMES = None
returned_offset = None

description = ("POK\xe9MON Gen III Hacking Suite was developed to enable "
               "better cross-platform POK\xe9MON Rom Hacking by removing the "
               "need for the .NET framework.  It was also created in order to "
               "be more adaptable to more advanced hacking techniques that change "
               "some boundaries, like the number of POK\xe9MON. In the past, "
               "these changes rendered some very necessary tools useless and "
               "which made using these new limits difficult.")

description = encode_per_platform(textwrap.fill(description, 110))

licence = "The MIT License (MIT)\n\n\nCopyright (c) 2014 karatekid552\n\n\n" + (
    '\n\n'.join([textwrap.fill(p, 80) for p in (
    "Permission is hereby granted, free of charge, to any person obtaining "
    "a copy of this software and associated documentation files (the 'Software'), "
    "to deal in the Software without restriction, including without limitation the "
    "rights to use, copy, modify, merge, publish, distribute, sublicense, and/or "
    "sell copies of the Software, and to permit persons to whom the Software is "
    "furnished to do so, subject to the following conditions:",
    "The above copyright notice and this permission notice shall be included in "
    "all copies or substantial portions of the Software.",
    "THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR "
    "IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, "
    "FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE "
    "AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER "
    "LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, "
    "OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE "
    "SOFTWARE.")]))

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
        self.tabbed_area = TabbedEditorArea(self.panel, self)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.tabbed_area, 1, wx.ALL|wx.EXPAND, 5)
        self.panel.SetSizer(self.sizer)
        self.Layout()

        self.CreateStatusBar() # A Statusbar in the bottom of the window
        # Setting up the menu.
        filemenu = wx.Menu()
        toolmenu = wx.Menu()
        helpmenu = wx.Menu()
        # wx.ID_ABOUT and wx.ID_EXIT are standard IDs provided by wxWidgets.
        filemenu.Append(wx.ID_OPEN, "&Open"," Open a ROM.")
        help_ID = wx.NewId()
        ContactID = wx.NewId()
        iniID = wx.NewId()
        toolmenu.Append(iniID, "&Ini Merger","Merge a new and old ini.")
        helpmenu.Append(help_ID, "&Documentation"," Open documentation. Requires a pdf reader.")
        helpmenu.AppendSeparator()
        helpmenu.Append(ContactID, "&Contact"," Contact the developer.")
        helpmenu.Append(wx.ID_ABOUT, "&About"," Information about this program")
        self.Bind(wx.EVT_MENU, self.open_file, id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.ini_merger, id=iniID)
        self.Bind(wx.EVT_MENU, self.Help, id=help_ID)
        self.Bind(wx.EVT_MENU, self.Contact, id=ContactID)
        self.Bind(wx.EVT_MENU, self.ABOUT, id=wx.ID_ABOUT)
        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
        menuBar.Append(toolmenu,"&Tools")
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

    def ini_merger(self, event=None):
        MergerPrompt(self)

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
            except AttributeError:
                directory = os.getcwd()
        open_dialog = wx.FileDialog(None, message="Open a rom...",
                                    defaultDir=directory,
                                    wildcard = "Rom files (*.gba,*.bin)|*.gba;*.GBA;*.BIN;*.bin|All files (*.*)|*.*",
                                    style=wx.FD_OPEN)
        if open_dialog.ShowModal() == wx.ID_OK:
            filename = open_dialog.GetPath()
            Globals.OpenRomName = filename
            self.open_rom = open(filename, "r+b")
            #try:
            with open("LastOpenedRom.txt", "w+") as pathfile:
                path = filename+"\n"+p+"\n"
                pathfile.write(path)
            #except:
            #    pass
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
        #try:
        self.tabbed_area.Destroy()
        #except: pass
        self.tabbed_area = TabbedEditorArea(self.panel, self)
        self.tabbed_area.LoadHexEditor()

        self.sizer.Add(self.tabbed_area, 1, wx.ALL|wx.EXPAND, 5)
        self.panel.Layout()
        self.Layout()
        self.Show(True)
        self.Refresh()

class TabbedEditorArea(wx.Notebook):
    """This class is what holds all of the main tabs."""
    def __init__(self, panel, parent):
        wx.Notebook.__init__(self, panel, id=wx.ID_ANY, style=wx.BK_DEFAULT)
        self.parent = parent

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
        try:
            old[num]
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
except urllib2.HTTPError:
    pass
#If I need to send everyone a message, this is the place.
try:
    r = urllib2.Request("https://raw.github.com/thekaratekid552/Secret-Tool/master/Message.txt")
    MSGresponse = urllib2.urlopen(r)
    MSG = MSGresponse.read()
    if MSG != "":
        Msgtimer = wx.Timer(frame, 98)
        Msgtimer.Start(500)
        wx.EVT_TIMER(frame, 98, OnMessageTimer)
except urllib2.HTTPError:
    pass

sys.stderr = StringIO()
frame.set_timer()
app.MainLoop()
