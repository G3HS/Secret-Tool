#!/usr/local/bin/python
# coding: utf-8

import wx, os, binascii, ConfigParser
from baseconv import *
from module_locator import *
from rom_insertion_operations import *

OPEN = 1

class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(800,600))
        self.open_rom = None
        self.rom_id = None
        self.path = module_path()
        self.open_rom_ini = {}
        
        self.panel = wx.Panel(self)
        self.tabbed_area = TabbedEditorArea(self.panel)
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.tabbed_area, 1, wx.ALL|wx.EXPAND, 5)
        self.panel.SetSizer(self.sizer)
        self.Layout()
        
        self.CreateStatusBar() # A Statusbar in the bottom of the window

        # Setting up the menu.
        filemenu= wx.Menu()

        # wx.ID_ABOUT and wx.ID_EXIT are standard IDs provided by wxWidgets.
        filemenu.Append(OPEN, "&Open"," Open a ROM.")
        filemenu.AppendSeparator()
        filemenu.Append(wx.ID_ABOUT, "&About"," Information about this program")
        filemenu.AppendSeparator()
        filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")
        
        self.Bind(wx.EVT_MENU, self.open_file, id=OPEN)
        
        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.
        self.Show(True)
        
    def open_file(self, *args):
        open_dialog = wx.FileDialog(self, message="Open a rom...", 
                                                        defaultDir=os.getcwd(), style=wx.OPEN)
        if open_dialog.ShowModal() == wx.ID_OK:
            filename = open_dialog.GetPath()
            self.open_rom = open(filename, "r+b")
            
            #Here we are going to check if the game has been opened before.
            #If yes, load it's custom ini. If no, create its ini.
            self.Config = ConfigParser.ConfigParser()
            ini = os.path.join(self.path,"PokeRoms.ini")
            self.Config.read(ini)
            if str(self.Config.get("ALL", "JustUseStandardIni")) == "True":
                game_code_offset = get_decimal_offset_from_hex_string("AC")
                self.open_rom.seek(game_code_offset, 0)
                self.rom_id = self.open_rom.read(4)
            
            else:
                rom_id_offset_hex = str(self.Config.get("ALL", "OffsetThatContainsSecondRomID"))
                rom_id_offset = get_decimal_offset_from_hex_string(rom_id_offset_hex)
                
                self.open_rom.seek(rom_id_offset) #Seek to last 2 bytes in rom
                self.rom_id = self.open_rom.read(2)
                self.rom_id = str(binascii.hexlify(self.rom_id)) 

                all_possible_rom_ids = self.Config.sections()
                
                if self.rom_id != "ffff":
                    if self.rom_id not in all_possible_rom_ids:
                        wx.MessageBox(
                        "At rom offset %s there is an unknown rom id. Please see documentation." %rom_id_offset_hex, 
                        'Error', 
                        wx.OK | wx.ICON_INFORMATION)
                    
                else:
                    game_code_offset = get_decimal_offset_from_hex_string("AC")
                    self.open_rom.seek(game_code_offset, 0)
                    game_code = self.open_rom.read(4)
                    self.open_rom.seek(rom_id_offset)
                    x = "0000"
                    y = None
                    while y == None:
                        if x in all_possible_rom_ids:
                            x = str(int(x) + 1)
                            if len(x) != 4:
                                n = 4 - len(x)
                                for n in range(n):
                                    x = "0"+x
                            continue
                        else:
                            self.rom_id = x
                            
                            #Write new rom_id to rom.
                            byte_rom_id = get_bytes_string_from_hex_string(self.rom_id)
                            self.open_rom.write(byte_rom_id)
                            
                            self.Config.add_section(self.rom_id)
                            options = self.Config.options(game_code)
                            tmp_ini = {}
                            for opt in options:
                                tmp_ini[opt] = self.Config.get(game_code, opt)
                                
                            for opt, value in tmp_ini.items():
                                self.Config.set(self.rom_id, opt, value)
                            with open(ini, "w") as PokeRomsIni:
                                self.Config.write(PokeRomsIni)
                            y = True
            self.reload_all_tabs()
            
    def reload_all_tabs(self):
        self.panel.Destroy()
        self.panel = wx.Panel(self)
        
        self.tabbed_area = TabbedEditorArea(self.panel)
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.tabbed_area, 1, wx.ALL|wx.EXPAND, 5)
        self.panel.SetSizer(self.sizer)
        self.Layout()
        size = self.GetSize()
        self.SetSize((size[0]+1, size[1]+1))
        self.SetSize(size)


#############################################################
#This class is what holds all of the main tabs.
#############################################################
class TabbedEditorArea(wx.Notebook):
    def __init__(self, parent):
        wx.Notebook.__init__(self, parent, id=wx.ID_ANY, style=
                                             wx.BK_DEFAULT
                                             #wx.BK_TOP 
                                             #wx.BK_BOTTOM
                                             #wx.BK_LEFT
                                             #wx.BK_RIGHT
                                             )
        
        PokeDataTab = PokemonDataEditor(self)
        self.AddPage(PokeDataTab, "Pokemon Data Editor")
        
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.OnPageChanging)
        
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

        
#############################################################
#This tab will allow editing of Pokemon Stats, moves, etc
#############################################################
class PokemonDataEditor(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        if 'frame' in globals():
            if frame.open_rom is not None:
                poke_names = self.get_pokemon_names()
            else: poke_names = []
        else: poke_names = ["-"]
        
        self.Pokes = wx.ComboBox(self, -1, choices=poke_names, 
                                value=poke_names[0],
                                style=wx.SUNKEN_BORDER,
                                pos=(0, 0), size=(200, -1))
        self.Pokes.Bind(wx.EVT_COMBOBOX, self.on_change_poke)
        self.poke_num = 0
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.Pokes, 0, wx.ALL, 2)
        self.tabbed_area = DataEditingTabs(self)
        self.sizer.Add(self.tabbed_area, 1, wx.ALL|wx.EXPAND, 2)
        self.SetSizer(self.sizer)
        self.Layout()
        
    def get_pokemon_names(self):
        offset = frame.Config.get(frame.rom_id, "PokeNames")
        offset = get_decimal_offset_from_hex_string(offset)
        frame.open_rom.seek(offset, 0)
        number = int(frame.Config.get(frame.rom_id, "NumberofPokes"))
        name_length = int(frame.Config.get(frame.rom_id, "PokeNamesLength"), 16)
        names = [] 
        for num in range(number):
            tmp_name = frame.open_rom.read(name_length)
            tmp_name = convert_ascii_and_poke(tmp_name, "to_poke")
            name = tmp_name.split("\xff")
            names.append(name[0])
        return names
    
    def on_change_poke(self, event):
        self.poke_num = self.Pokes.GetSelection()
        self.tabbed_area.Destroy()
        self.tabbed_area = DataEditingTabs(self)
        self.sizer.Add(self.tabbed_area, 1, wx.ALL|wx.EXPAND, 2)
        self.Layout()
        
class DataEditingTabs(wx.Notebook):
    def __init__(self, parent):
        wx.Notebook.__init__(self, parent, id=wx.ID_ANY, style=
                                             wx.BK_DEFAULT
                                             #wx.BK_TOP 
                                             #wx.BK_BOTTOM
                                             #wx.BK_LEFT
                                             #wx.BK_RIGHT
                                             )
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        stats = StatsTab(self)
        moves = MovesTab(self)
        evo = EvoTab(self)
        dex = PokeDexTab(self)
        
        self.AddPage(stats, "Stats")
        self.AddPage(moves, "Moves")
        self.AddPage(evo, "Evolutions")
        self.AddPage(dex, "PokeDex")
        
        self.SetSizer(sizer)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.OnPageChanging)
        
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
        
class StatsTab(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.SetSizer(sizer)

class MovesTab(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.SetSizer(sizer)

class EvoTab(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.SetSizer(sizer)

class PokeDexTab(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.SetSizer(sizer)
#############################################################



app = wx.App(False)
frame = MainWindow(None, "Pokemon Gen III Hacking Suite")
app.MainLoop()