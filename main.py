# -*- coding: utf-8 -*- 
#venv pyi-env-name
from __future__ import division
import wx, os, binascii, ConfigParser, sys
from baseconv import *
from module_locator import *
from rom_insertion_operations import *
from CheckListCtrl import *

from cStringIO import StringIO

OPEN = 1
poke_num = 0
poke_names = None
MOVES_LIST = None
ITEM_NAMES = None

fallback = sys.stderr


description = """POK\xe9MON Gen III Hacking Suite was developed to enable better cross-
platform POK\xe9MON  Rom Hacking by removing the need for the .NET
framework.  It was also created in order to be more adaptable to more
advanced hacking techniques that change some boundaries, like the number
of POK\xe9MON. In the past, these changes rendered some very necessary
tools useless and which made using these new limits difficult."""

description = encode_per_platform(description)

licence = """The POK\xe9MON Gen III Hacking Suite is free software; you can redistribute 
it and/or modify it under the terms of the GNU General Public License as 
published by the Free Software Foundation; either version 2 of the License, 
or (at your option) any later version. See the GNU General Public License 
for more details.

This program has NO WARRENTY and the creator is not responsible for any 
corruption/data loss it may cause."""

licence = encode_per_platform(licence)

class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(800,600))
        self.open_rom = None
        self.rom_id = None
        self.path = module_path()
        self.open_rom_ini = {}
        
        self.timer = None
        sys.stderr = StringIO()
        
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
        
        self.Bind(wx.EVT_MENU, self.open_file, id=OPEN)
        self.Bind(wx.EVT_MENU, self.ABOUT, id=wx.ID_ABOUT)
        
        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.
        self.Show(True)
        self.set_timer()
        
    def on_timer(self, event):
        self.set_timer()
        read = sys.stderr.getvalue()
        if read != "":
            sys.stderr.close()
            sys.stderr = StringIO()
            ERROR = wx.MessageDialog(None, 
                                "ERROR:\n\n"+read, 
                                'Piped error from sys.stderr: PLEASE REPORT', 
                                wx.OK | wx.ICON_ERROR)
            ERROR.ShowModal()

    def set_timer(self):
        TIMER_ID = 100  # pick a number
        self.timer = wx.Timer(self, TIMER_ID)  # message will be sent to the panel
        self.timer.Start(1000)  # x1000 milliseconds
        wx.EVT_TIMER(self, TIMER_ID, self.on_timer)  # call the on_timer function

    def ABOUT(self, *args):
        
        info = wx.AboutDialogInfo()
        global description
        global licence
        name = 'POK\xe9MON Gen III Hacking Suite'
        name = encode_per_platform(name)
        info.SetName(name)
        info.SetVersion('Alpha Demo 0.2')
        info.SetDescription(description)
        info.SetCopyright('(C) 2013 karatekid552')
        #info.SetWebSite('')
        info.SetLicence(licence)
        #info.AddDocWriter('')

        wx.AboutBox(info)
        
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
                            byte_rom_id = get_hex_from_string(self.rom_id)
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
        
        self.PokeDataTab = PokemonDataEditor(self)
        name = "POK\xe9MON Data Editor"
        name = encode_per_platform(name)
        self.AddPage(self.PokeDataTab, name)
        
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
                self.poke_names = self.get_pokemon_names()
                global poke_names
                poke_names = self.poke_names
                self.Pokes = wx.ComboBox(self, -1, choices=self.poke_names, 
                                value=self.poke_names[0],
                                style=wx.SUNKEN_BORDER,
                                pos=(0, 0), size=(150, -1))
                self.Pokes.Bind(wx.EVT_COMBOBOX, self.on_change_poke)
                global poke_num
                poke_num = 0
                
                Change_Name = wx.StaticText(self, -1, "Change Name:")
                self.Poke_Name = wx.TextCtrl(self, -1,style=wx.TE_CENTRE, size=(150,-1))
                self.Poke_Name.SetValue(self.poke_names[0])
                
                save = wx.Button(self, 1, "Save All")
                self.Bind(wx.EVT_BUTTON, self.OnSave, id=1)
                self.sizer = wx.BoxSizer(wx.VERTICAL)
                self.sizer_top = wx.BoxSizer(wx.HORIZONTAL)
                
                self.sizer_top.Add(self.Pokes, 0, wx.ALL, 5)
                self.sizer_top.Add(Change_Name, 0, wx.ALL, 5)
                self.sizer_top.Add(self.Poke_Name, 0, wx.ALL, 5)
                self.sizer_top.Add(save, 0, wx.LEFT, 20)
                
                self.sizer.Add(self.sizer_top, 0, wx.ALL, 2)
                self.tabbed_area = DataEditingTabs(self)
                
                self.sizer.Add(self.tabbed_area, 1, wx.ALL|wx.EXPAND, 2)
                self.SetSizer(self.sizer)
        self.Layout()
        
    def get_pokemon_names(self):
        offset = int(frame.Config.get(frame.rom_id, "PokeNames"),0)
        frame.open_rom.seek(offset, 0)
        number = int(frame.Config.get(frame.rom_id, "NumberofPokes"), 0)
        name_length = int(frame.Config.get(frame.rom_id, "PokeNamesLength"), 0)
        names = [] 
        for num in range(number):
            tmp_name = frame.open_rom.read(name_length)
            tmp_name = convert_ascii_and_poke(tmp_name, "to_poke")
            name = tmp_name.split("\\xFF", 1)
            names.append(name[0])
        return names
    
    def on_change_poke(self, event):
        global poke_num
        poke_num = self.Pokes.GetSelection()
        self.Poke_Name.SetValue(self.poke_names[poke_num])
        
        self.tabbed_area.reload_tab_data()
        
    def OnSave(self, event):
        self.tabbed_area.stats.save()
        self.save_new_poke_name()
        self.poke_names = self.get_pokemon_names()
        self.Pokes.SetItems(self.poke_names)
        global poke_num
        self.Pokes.SetSelection(poke_num)
        self.tabbed_area.moves.save()
        self.tabbed_area.egg_moves.save()
        
    def save_new_poke_name(self):
        name = self.Poke_Name.GetValue()
        name = convert_ascii_and_poke(str(name), "to_ascii")
        name += "\xff"
        max_length = int(frame.Config.get(frame.rom_id, "PokeNamesLength"), 0)
        need = max_length-len(name)
        if need < 0:
            m = max_length - 1
            name = name[:m]+"\xff"
            need = 0
        for n in range(need):
            name += "\x00"
        global poke_num
        offset = int(frame.Config.get(frame.rom_id, "PokeNames"),0)
        offset = max_length*poke_num + offset
        frame.open_rom.seek(offset,0)
        frame.open_rom.write(name)
        
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
        
        self.stats = StatsTab(self)
        self.moves = MovesTab(self)
        self.evo = EvoTab(self)
        self.dex = PokeDexTab(self)
        self.egg_moves = EggMoveTab(self)
        
        self.AddPage(self.stats, "Stats")
        self.AddPage(self.moves, "Moves")
        self.AddPage(self.evo, "Evolutions")
        dex_name = "POK\xe9Dex"
        dex_name = encode_per_platform(dex_name)
        self.AddPage(self.dex, dex_name)
        self.AddPage(self.egg_moves, "Egg Moves")
        
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
        
    def reload_tab_data(self):
        self.stats.reload_stuff()
        self.moves.load_everything()
        self.evo.load_everything()
        
class StatsTab(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.sizer = wx.GridBagSizer(3,3)
        basestatsoffset = int(frame.Config.get(frame.rom_id, "pokebasestats"), 0)
        basestatslength = int(frame.Config.get(frame.rom_id, "pokebasestatslength"), 0)
        global poke_num
        self.basestatsoffset = basestatslength*poke_num + basestatsoffset
        frame.open_rom.seek(self.basestatsoffset, 0)
        self.base_stats_dict = {}
        self.basestats = frame.open_rom.read(basestatslength)
        self.sort_base_stats()
        self.generate_ui()
        
        self.SetSizer(self.sizer)
        self.Layout()
        
    def reload_stuff(self):
        basestatsoffset = int(frame.Config.get(frame.rom_id, "pokebasestats"), 0)
        basestatslength = int(frame.Config.get(frame.rom_id, "pokebasestatslength"), 0)
        global poke_num
        self.basestatsoffset = basestatslength*poke_num + basestatsoffset
        frame.open_rom.seek(self.basestatsoffset, 0)
        self.base_stats_dict = {}
        self.basestats = frame.open_rom.read(basestatslength)
        self.sort_base_stats()
        self.load_stats_into_boxes()

    def generate_ui(self):
        #----------Set up a panel for the regular stats.----------#
        basic_stats = wx.Panel(self, -1, style=wx.RAISED_BORDER|wx.TAB_TRAVERSAL)
        basic_stats_sizer = wx.GridBagSizer(3,3)
        
        basic_stats_txt = wx.StaticText(basic_stats, -1,"Base Stats:")
        basic_stats_sizer.Add(basic_stats_txt, (0, 0), (1,2), wx.EXPAND)
        
        HP_txt = wx.StaticText(basic_stats, -1,"HP:")
        basic_stats_sizer.Add(HP_txt, (1, 0), wx.DefaultSpan,  wx.ALL, 6)
        self.HP = wx.TextCtrl(basic_stats, -1,style=wx.TE_CENTRE, size=(40,-1))
        basic_stats_sizer.Add(self.HP,(1, 1), wx.DefaultSpan,  wx.ALL, 4)
        
        ATK_txt = wx.StaticText(basic_stats, -1,"ATK:")
        basic_stats_sizer.Add(ATK_txt, (2, 0), wx.DefaultSpan,  wx.ALL, 6)
        self.ATK = wx.TextCtrl(basic_stats, -1,style=wx.TE_CENTRE, size=(40,-1))
        basic_stats_sizer.Add(self.ATK,(2, 1), wx.DefaultSpan,  wx.ALL, 4)
        
        DEF_txt = wx.StaticText(basic_stats, -1,"DEF:")
        basic_stats_sizer.Add(DEF_txt, (3, 0), wx.DefaultSpan,  wx.ALL, 6)
        self.DEF = wx.TextCtrl(basic_stats, -1,style=wx.TE_CENTRE, size=(40,-1))
        basic_stats_sizer.Add(self.DEF,(3, 1), wx.DefaultSpan,  wx.ALL, 4)
        
        SPD_txt = wx.StaticText(basic_stats, -1,"SPD:")
        basic_stats_sizer.Add(SPD_txt, (4, 0), wx.DefaultSpan,  wx.ALL, 6)
        self.SPD = wx.TextCtrl(basic_stats, -1,style=wx.TE_CENTRE, size=(40,-1))
        basic_stats_sizer.Add(self.SPD,(4, 1), wx.DefaultSpan,  wx.ALL, 4)
        
        SpATK_txt = wx.StaticText(basic_stats, -1,"Sp. ATK:")
        basic_stats_sizer.Add(SpATK_txt, (5, 0), wx.DefaultSpan,  wx.ALL, 6)
        self.SpATK = wx.TextCtrl(basic_stats, -1,style=wx.TE_CENTRE, size=(40,-1))
        basic_stats_sizer.Add(self.SpATK,(5, 1), wx.DefaultSpan,  wx.ALL, 4)
        
        SpDEF_txt = wx.StaticText(basic_stats, -1,"Sp. DEF:")
        basic_stats_sizer.Add(SpDEF_txt, (6, 0), wx.DefaultSpan,  wx.ALL, 6)
        self.SpDEF = wx.TextCtrl(basic_stats, -1,style=wx.TE_CENTRE, size=(40,-1))
        basic_stats_sizer.Add(self.SpDEF,(6, 1), wx.DefaultSpan,  wx.ALL, 4)
        
        basic_stats_sizer.SetFlexibleDirection(wx.BOTH)
        
        basic_stats.SetSizerAndFit(basic_stats_sizer)
        
         #----------Set up a panel for EVs----------#
        evs = wx.Panel(self, -1, style=wx.RAISED_BORDER|wx.TAB_TRAVERSAL)
        evs_sizer = wx.GridBagSizer(3,3)
        
        e_txt = wx.StaticText(evs, -1,"Effort Values:")
        evs_sizer.Add(e_txt, (0, 0), (1,2), wx.EXPAND)
        
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
        
        e_SPD_txt = wx.StaticText(evs, -1,"SPD:")
        evs_sizer.Add(e_SPD_txt, (4, 0), wx.DefaultSpan,  wx.ALL, 6)
        self.e_SPD = wx.TextCtrl(evs, -1,style=wx.TE_CENTRE, size=(40,-1))
        evs_sizer.Add(self.e_SPD,(4, 1), wx.DefaultSpan,  wx.ALL, 4)
        
        e_SpATK_txt = wx.StaticText(evs, -1,"Sp. ATK:")
        evs_sizer.Add(e_SpATK_txt, (5, 0), wx.DefaultSpan,  wx.ALL, 6)
        self.e_SpATK = wx.TextCtrl(evs, -1,style=wx.TE_CENTRE, size=(40,-1))
        evs_sizer.Add(self.e_SpATK,(5, 1), wx.DefaultSpan,  wx.ALL, 4)
        
        e_SpDEF_txt = wx.StaticText(evs, -1,"Sp. DEF:")
        evs_sizer.Add(e_SpDEF_txt, (6, 0), wx.DefaultSpan,  wx.ALL, 6)
        self.e_SpDEF = wx.TextCtrl(evs, -1,style=wx.TE_CENTRE, size=(40,-1))
        evs_sizer.Add(self.e_SpDEF,(6, 1), wx.DefaultSpan,  wx.ALL, 4)
        
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
        
        level_up_tmp = frame.Config.get(frame.rom_id, "LevelUpTypes")
        level_up_list = level_up_tmp.split(",")
        LEVEL_txt = wx.StaticText(assorted, -1,"Level-Up Rate:")
        assorted_sizer.Add(LEVEL_txt, (3, 0), wx.DefaultSpan,  wx.ALL, 4)
        self.LEVEL = wx.ComboBox(assorted, -1, choices=level_up_list,
                                style=wx.SUNKEN_BORDER, size=(100, -1))
        assorted_sizer.Add(self.LEVEL, (3, 1), wx.DefaultSpan,  wx.ALL, 4)
        
        egg_tmp = frame.Config.get(frame.rom_id, "EggGroups")
        egg_groups = egg_tmp.split(",")
        
        EGG1_txt = wx.StaticText(assorted, -1,"Egg Group 1:")
        assorted_sizer.Add(EGG1_txt, (4, 0), wx.DefaultSpan,  wx.ALL, 4)
        self.EGG1 = wx.ComboBox(assorted, -1, choices=egg_groups,
                                style=wx.SUNKEN_BORDER, size=(100, -1))
        assorted_sizer.Add(self.EGG1, (4, 1), wx.DefaultSpan,  wx.ALL, 4)
        
        EGG2_txt = wx.StaticText(assorted, -1,"Egg Group 2:")
        assorted_sizer.Add(EGG2_txt, (5, 0), wx.DefaultSpan,  wx.ALL, 4)
        self.EGG2 = wx.ComboBox(assorted, -1, choices=egg_groups,
                                style=wx.SUNKEN_BORDER, size=(100, -1))
        assorted_sizer.Add(self.EGG2, (5, 1), wx.DefaultSpan,  wx.ALL, 4)
        
        assorted.SetSizerAndFit(assorted_sizer)

        #---------Set up a panel for Types----------#
        types = wx.Panel(self, -1, style=wx.RAISED_BORDER|wx.TAB_TRAVERSAL)
        types_sizer = wx.GridBagSizer(3,3)
        
        #Get list of types:
        t_offset = int(frame.Config.get(frame.rom_id, "TypeNames"), 0)
        t_name_length = int(frame.Config.get(frame.rom_id, "TypeNamesLength"), 0)
        t_number = int(frame.Config.get(frame.rom_id, "NumberofTypes"), 0)
        list_of_types = []
        
        frame.open_rom.seek(t_offset, 0)
        for n in range(t_number):
            temp_type = frame.open_rom.read(t_name_length)
            temp_type = convert_ascii_and_poke(temp_type, "to_poke")
            temp_type = temp_type.split("\\xFF")
            list_of_types.append(temp_type[0])
        
        TYPE1_txt = wx.StaticText(types, -1,"Type 1:")
        types_sizer.Add(TYPE1_txt, (0, 0), wx.DefaultSpan,  wx.ALL, 4)
        self.TYPE1 = wx.ComboBox(types, -1, choices=list_of_types,
                                style=wx.SUNKEN_BORDER, size=(80, -1))
        types_sizer.Add(self.TYPE1, (0, 1), wx.DefaultSpan,  wx.ALL, 4)
        
        TYPE2_txt = wx.StaticText(types, -1,"Type 2:")
        types_sizer.Add(TYPE2_txt, (1, 0), wx.DefaultSpan,  wx.ALL, 4)
        self.TYPE2 = wx.ComboBox(types, -1, choices=list_of_types,
                                style=wx.SUNKEN_BORDER, size=(80, -1))
        types_sizer.Add(self.TYPE2, (1, 1), wx.DefaultSpan,  wx.ALL, 4)
        
        types.SetSizerAndFit(types_sizer)
        
        #----------Panel for Abilities----------#
        abilities = wx.Panel(self, -1, style=wx.RAISED_BORDER|wx.TAB_TRAVERSAL)
        abilities_sizer = wx.GridBagSizer(3,3)
        
        abil_offset = int(frame.Config.get(frame.rom_id, "Abilities"), 0)
        abil_num = int(frame.Config.get(frame.rom_id, "NumberofAbilities"), 0)
        abil_len = int(frame.Config.get(frame.rom_id, "AbiltiesNameLength"), 0)

        abilities_list = generate_list_of_names(abil_offset, abil_len, "\xff", abil_num, frame.open_rom)
        
        ABILITY1_txt = wx.StaticText(abilities, -1,"Ability 1:")
        abilities_sizer.Add(ABILITY1_txt, (0, 0), wx.DefaultSpan,  wx.ALL, 4)
        self.ABILITY1 = wx.ComboBox(abilities, -1, choices=abilities_list,
                                style=wx.SUNKEN_BORDER, size=(150, -1))
        abilities_sizer.Add(self.ABILITY1, (0, 1), wx.DefaultSpan,  wx.ALL, 4)
        
        ABILITY2_txt = wx.StaticText(abilities, -1,"Ability 2:")
        abilities_sizer.Add(ABILITY2_txt, (1, 0), wx.DefaultSpan,  wx.ALL, 4)
        self.ABILITY2 = wx.ComboBox(abilities, -1, choices=abilities_list,
                                style=wx.SUNKEN_BORDER, size=(150, -1))
        abilities_sizer.Add(self.ABILITY2, (1, 1), wx.DefaultSpan,  wx.ALL, 4)
        
        abilities.SetSizerAndFit(abilities_sizer)
        
        #----------Panel for items----------#
        items = wx.Panel(self, -1, style=wx.RAISED_BORDER|wx.TAB_TRAVERSAL)
        items_sizer = wx.GridBagSizer(3,3)
        
        items_offset = int(frame.Config.get(frame.rom_id, "Items"), 16)
        number_of_items = int(frame.Config.get(frame.rom_id, "NumberofItems"), 16)
        item_data_len = int(frame.Config.get(frame.rom_id, "ItemsDataLength"), 16)
        
        items_list = generate_list_of_names(items_offset, item_data_len, 
                            "\xff", number_of_items, frame.open_rom)
        global ITEM_NAMES
        ITEM_NAMES = items_list
        ITEM1_txt = wx.StaticText(items, -1,"Item 1:")
        items_sizer.Add(ITEM1_txt, (0, 0), wx.DefaultSpan,  wx.ALL, 4)
        self.ITEM1 = wx.ComboBox(items, -1, choices=items_list,
                                 style=wx.SUNKEN_BORDER, size=(160, -1))
        items_sizer.Add(self.ITEM1, (0, 1), wx.DefaultSpan,  wx.ALL, 4)
        
        ITEM2_txt = wx.StaticText(items, -1,"Item 2:")
        items_sizer.Add(ITEM2_txt, (1, 0), wx.DefaultSpan,  wx.ALL, 4)
        self.ITEM2 = wx.ComboBox(items, -1, choices=items_list,
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
        self.COLOR = wx.ComboBox(run_rate_color, -1, choices=colors_list,
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
        self.load_stats_into_boxes()
    
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
        self.e_SpATK.SetValue(str(d["EVS"][6]))
        self.e_SpDEF.SetValue(str(d["EVS"][7]))
        
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
            HP = hex(int(self.HP.GetValue(), 0))[2:]
            if len(HP) > 2:
                HP = "FF"
            elif len(HP) == 0:
                HP = "00"
            elif len(HP) == 1:
                HP = "0"+HP
                
            ATK = hex(int(self.ATK.GetValue(), 0))[2:]
            if len(ATK) > 2:
                ATK = "FF"
            elif len(ATK) == 0:
                ATK = "00"
            elif len(ATK) == 1:
                ATK = "0"+ATK
                
            DEF = hex(int(self.DEF.GetValue(), 0))[2:]
            if len(DEF) > 2:
                DEF = "FF"
            elif len(DEF) == 0:
                DEF = "00"
            elif len(DEF) == 1:
                DEF = "0"+DEF
                 
            SPD = hex(int(self.SPD.GetValue(), 0))[2:]
            if len(SPD) > 2:
                SPD = "FF"
            elif len(SPD) == 0:
                SPD = "00"
            elif len(SPD) == 1:
                SPD = "0"+SPD
                 
            SpATK = hex(int(self.SpATK.GetValue(), 0))[2:]
            if len(SpATK) > 2:
                SpATK = "FF"
            elif len(SpATK) == 0:
                SpATK = "00"
            elif len(SpATK) == 1:
                SpATK = "0"+SpATK
                 
            SpDEF = hex(int(self.SpDEF.GetValue(), 0))[2:]
            if len(SpDEF) > 2:
                SpDEF = "FF"
            elif len(SpDEF) == 0:
                SpDEF = "00"
            elif len(SpDEF) == 1:
                SpDEF = "0"+SpDEF
                 
            TYPE1 = hex(int(self.TYPE1.GetSelection()))[2:]
            if len(TYPE1) == 1:
                TYPE1 = "0"+TYPE1
                 
            TYPE2 = hex(int(self.TYPE2.GetSelection()))[2:]
            if len(TYPE2) == 1:
                TYPE2 = "0"+TYPE2
            
            CATCHRATE = hex(int(self.CATCHRATE.GetValue(), 0))[2:]
            if len(CATCHRATE) > 2:
                CATCHRATE = "FF"
            elif len(CATCHRATE) == 0:
                CATCHRATE = "00"
            elif len(CATCHRATE) == 1:
                CATCHRATE = "0"+CATCHRATE
                
            BASEEXP = hex(int(self.BASEEXP.GetValue(), 0))[2:]
            if len(BASEEXP) > 2:
                BASEEXP = "FF"
            elif len(BASEEXP) == 0:
                BASEEXP = "00"
            elif len(BASEEXP) == 1:
                BASEEXP = "0"+BASEEXP
                
            evs_list = [str(self.e_SPD.GetValue()), str(self.e_DEF.GetValue()),
                            str(self.e_ATK.GetValue()), str(self.e_HP.GetValue()),
                            "0","0",str(self.e_SpATK.GetValue()),str(self.e_SpDEF.GetValue())]
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
            
            
            ITEM1 = hex(int(self.ITEM1.GetSelection()))[2:]
            ITEM1_len = len(ITEM1)
            if ITEM1_len < 4:
                for n in range(4-ITEM1_len):
                    ITEM1 = "0"+ITEM1
            ITEM1 = ITEM1[2:]+ITEM1[:2] #Flip the bytes around.

            ITEM2 = hex(int(self.ITEM2.GetSelection()))[2:]
            ITEM2_len = len(ITEM2)
            if ITEM2_len < 4:
                for n in range(4-ITEM2_len):
                    ITEM2 = "0"+ITEM2
            ITEM2 = ITEM2[2:]+ITEM2[:2] #Flip the bytes around.
            
            GENDER = hex(int(self.GENDER.GetValue(), 0))[2:]
            if len(GENDER) > 2:
                GENDER = "FF"
            elif len(GENDER) == 0:
                GENDER = "00"
            elif len(GENDER) == 1:
                GENDER = "0"+GENDER
                
            HATCH = hex(int(self.HATCH.GetValue(), 0))[2:]
            if len(HATCH) > 2:
                HATCH = "FF"
            elif len(HATCH) == 0:
                HATCH = "00"
            elif len(HATCH) == 1:
                HATCH = "0"+HATCH
                
            FRIEND = hex(int(self.FRIEND.GetValue(), 0))[2:]
            if len(FRIEND) > 2:
                FRIEND = "FF"
            elif len(FRIEND) == 0:
                FRIEND = "00"
            elif len(FRIEND) == 1:
                FRIEND = "0"+FRIEND
            
            LEVEL = hex(int(self.LEVEL.GetSelection()))[2:]
            if len(LEVEL) == 1:
                LEVEL = "0"+LEVEL          
                
            EGG1 = hex(int(self.EGG1.GetSelection())+1)[2:]
            if len(EGG1) == 1:
                EGG1 = "0"+EGG1 
                
            EGG2 = hex(int(self.EGG2.GetSelection())+1)[2:]
            if len(EGG2) == 1:
                EGG2 = "0"+EGG2 
            
            ABILITY1 = hex(int(self.ABILITY1.GetSelection()))[2:]
            if len(ABILITY1) == 1:
                ABILITY1 = "0"+ABILITY1 
            
            ABILITY2 = hex(int(self.ABILITY2.GetSelection()))[2:]
            if len(ABILITY2) == 1:
                ABILITY2 = "0"+ABILITY2 
                
            RUNRATE = hex(int(self.RUNRATE.GetValue(), 0))[2:]
            if len(RUNRATE) > 2:
                RUNRATE = "FF"
            elif len(RUNRATE) == 0:
                RUNRATE = "00"
            elif len(RUNRATE) == 1:
                RUNRATE = "0"+RUNRATE
                
            COLOR = hex(int(self.COLOR.GetSelection()))[2:]
            if len(COLOR) == 1:
                COLOR = "0"+COLOR
                
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
                                'One of your entries contains in the stats tab contains bad data.', 
                                'Data Error', 
                                wx.OK | wx.ICON_ERROR)
            ERROR.ShowModal()
        
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
        frame.open_rom.seek(self.basestatsoffset, 0)
        string = binascii.unhexlify(string)
        frame.open_rom.write(string)
        
class MovesTab(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.sizer = wx.GridBagSizer(3,3)
        self.generate_ui()
        self.SetSizer(self.sizer)

        self.Layout()
        
    def generate_ui(self):
        moves_offset = int(frame.Config.get(frame.rom_id, "AttackNames"), 0)
        moves_length = int(frame.Config.get(frame.rom_id, "AttackNameLength"), 0)
        moves_num = int(frame.Config.get(frame.rom_id, "NumberofAttacks"), 0)
        
        self.MOVES_LIST = generate_list_of_names(moves_offset, moves_length, "\xff", moves_num, frame.open_rom)
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

        
        self.ATTACK = wx.ComboBox(learned_moves, -1, choices=self.MOVES_LIST,
                                style=wx.SUNKEN_BORDER, size=(100, -1))
        editing_box.Add(self.ATTACK, 0, wx.EXPAND | wx.ALL, 2)
        
        self.LEVEL = wx.TextCtrl(learned_moves, -1,style=wx.TE_CENTRE, size=(40,-1))
        editing_box.Add(self.LEVEL, 0, wx.EXPAND | wx.ALL, 2)
        
        SET = wx.Button(learned_moves, 8, "Replace")
        self.Bind(wx.EVT_BUTTON, self.OnChangeMove, id=8)
        editing_box.Add(SET, 0, wx.EXPAND | wx.ALL, 2)
        
        v_lm_box.Add(editing_box, 0, wx.EXPAND | wx.ALL, 2)
        
        self.FRACTION = wx.StaticText(learned_moves, -1, "XX/XX Moves")
        v_lm_box_buttons.Add(self.FRACTION, 0, wx.EXPAND | wx.ALL, 5)
        
        self.LEARNED_OFFSET = wx.StaticText(learned_moves, -1, "0xXXXXXX")
        v_lm_box_buttons.Add(self.LEARNED_OFFSET, 0, wx.EXPAND | wx.ALL, 5)
        
        REPOINT = wx.Button(learned_moves, 1, "Repoint")
        self.Bind(wx.EVT_BUTTON, self.OnRepoint, id=1)
        v_lm_box_buttons.Add(REPOINT, 0, wx.EXPAND | wx.ALL, 5)
        
        ADD = wx.Button(learned_moves, 2, "Add")
        self.Bind(wx.EVT_BUTTON, self.OnAdd, id=2)
        v_lm_box_buttons.Add(ADD, 0, wx.EXPAND | wx.ALL, 5)
        
        DELETE = wx.Button(learned_moves, 3, "Delete")
        self.Bind(wx.EVT_BUTTON, self.OnDelete, id=3)
        v_lm_box_buttons.Add(DELETE, 0, wx.EXPAND | wx.ALL, 5)
        
        MOVE_UP = wx.Button(learned_moves, 4, "Move Up")
        self.Bind(wx.EVT_BUTTON, self.OnMoveUp, id=4)
        v_lm_box_buttons.Add(MOVE_UP, 0, wx.EXPAND | wx.ALL, 5)
        
        MOVE_DOWN = wx.Button(learned_moves, 5, "Move Down")
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
        
        SELECTALL = wx.Button(TMHMPanel, 6, "Select All")
        self.Bind(wx.EVT_BUTTON, self.OnSelectAllTMHMs, id=6)
        ButtonBox.Add(SELECTALL, 0, wx.EXPAND | wx.ALL, 5)
        
        CLEAR = wx.Button(TMHMPanel, 7, "Clear All")
        self.Bind(wx.EVT_BUTTON, self.OnClearAllTMHMs, id=7)
        ButtonBox.Add(CLEAR, 0, wx.EXPAND | wx.ALL, 5)
        
        TMHMPanel.SetSizerAndFit(TMHMBIGBOX)
        #----Add Everything to the Sizer----#
        self.sizer.Add(learned_moves, (0,0), wx.DefaultSpan, wx.ALL, 4)
        self.sizer.Add(TMHMPanel, (0,1), wx.DefaultSpan, wx.ALL, 4)
        self.load_everything()
        
    def save(self):
        learned_offset = self.learned_moves_offset
        if self.NEW_LEARNED_OFFSET != None:
            pointer = "08"+self.NEW_LEARNED_OFFSET
            pointer = make_pointer(pointer)
            pointer = get_hex_from_string(pointer)
            frame.open_rom.seek(self.learned_moves_pointer)
            frame.open_rom.write(pointer)
            learned_offset = int(self.NEW_LEARNED_OFFSET, 16)
        frame.open_rom.seek(learned_offset)
        learned_moves = self.prepare_string_of_learned_moves()
        learned_moves = get_hex_from_string(learned_moves)
        frame.open_rom.write(learned_moves)
        
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
        frame.open_rom.seek(self.TMHMoffset)
        frame.open_rom.write(hexTMHM)
            
    def OnSelectMove(self, *args):
        self.UPDATE_FRACTION()
        sel = self.MOVESET.GetFocusedItem()
        
        self.LEVEL.SetValue(str(self.learned_moves[sel][1]))
        self.ATTACK.SetSelection(self.learned_moves[sel][0])
        
    def OnRepoint(self, *args):
        repoint = MOVE_REPOINTER(parent=None)
        repoint.Show()
        
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
        Jambo51HackCheck = frame.Config.get(frame.rom_id, "Jambo51LearnedMoveHack")
        string = ""
        if Jambo51HackCheck == "False":
            for attack, level in self.learned_moves:
                lvl = level
                atk = attack
                lvl *= 2
                if attack > 256:
                    lvl += 1
                    atk = atk-256
                set = hex(atk)[2:].zfill(2)+hex(lvl)[2:].zfill(2)
                string += set
            string += "ffff5555"
        else:
            for attack, level in self.learned_moves:
                lvl = hex(level)[2:]
                atk = hex(attack)[2:].zfill(4)
                atk = atk[2:]+atk[:2]
                set = atk+lvl
                string += set
            string += "ffffff55"
        return string
    
    def load_everything(self):
        self.NEW_LEARNED_OFFSET = None
        self.NEW_NUMBER_OF_MOVES = None
        self.original_amount_of_moves = 0
        #Load learned move data:
        self.MOVESET.DeleteAllItems()
        self.learned_moves = self.get_move_data()
        for move, level in self.learned_moves:
            index = self.MOVESET.InsertStringItem(sys.maxint, self.MOVES_LIST[move])
            self.MOVESET.SetStringItem(index, 1, str(level))
        self.LEARNED_OFFSET.SetLabel(hex(self.learned_moves_offset))
        
        self.UPDATE_FRACTION()
        
        self.getTMHMdata()
        self.LoadTMNames()
        global MOVES_LIST
        NumberofTMs = int(frame.Config.get(frame.rom_id, "NumberofTMs"), 0)
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
        self.learned_moves_pointer = int(frame.Config.get(frame.rom_id, "LearnedMoves"), 0)
        learned_moves_length = int(frame.Config.get(frame.rom_id, "LearnedMovesLength"), 0)
        
        Jambo51HackCheck = frame.Config.get(frame.rom_id, "Jambo51LearnedMoveHack")
        global poke_num
        self.learned_moves_pointer = poke_num*4+self.learned_moves_pointer
        frame.open_rom.seek(self.learned_moves_pointer, 0)
        self.learned_moves_offset = read_pointer(frame.open_rom.read(4))
        frame.open_rom.seek(self.learned_moves_offset, 0)
        learned_moves = []
        if Jambo51HackCheck == "False":
            while True:
                    last_read = frame.open_rom.read(2)
                    if last_read != "\xff\xff":
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
                    last_read = frame.open_rom.read(3)
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
        self.TMHMoffset = int(frame.Config.get(frame.rom_id, "TMHMCompatibility"), 0)
        length = int(frame.Config.get(frame.rom_id, "TMHMCompatibilityLength"), 0)
        global poke_num
        
        self.TMHMoffset += length+poke_num*length
        frame.open_rom.seek(self.TMHMoffset)
        read = frame.open_rom.read(length)
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
        TMList = int(frame.Config.get(frame.rom_id, "TMList"), 0)
        TMListLength = int(frame.Config.get(frame.rom_id, "TMListEntryLength"), 0)
        NumberofTMs = int(frame.Config.get(frame.rom_id, "NumberofTMs"), 0)
        NumberofHMs = int(frame.Config.get(frame.rom_id, "NumberofHMs"), 0)

        frame.open_rom.seek(TMList)
        
        self.TMNumbers = []
        for n in range(NumberofTMs):
            read = frame.open_rom.read(TMListLength)
            read = get_bytes_string_from_hex_string(read)
            read = read[2:]+read[:2]
            read = int(read, 16)
            
            self.TMNumbers.append(read)
        self.HMNumbers = []
        for n in range(NumberofHMs):
            read = frame.open_rom.read(TMListLength)
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
        
        self.generate_UI()
        
        self.SetSizer(self.sizer)

    def generate_UI(self):
        EVO = wx.Panel(self, -1, style=wx.RAISED_BORDER|wx.TAB_TRAVERSAL)
        EVO_Sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        self.evo_list = wx.ListCtrl(EVO, -1, style=wx.LC_REPORT, size=(600,300))
        self.evo_list.InsertColumn(0, 'Method', width=160)
        self.evo_list.InsertColumn(1, 'Argument', width=160)
        self.evo_list.InsertColumn(2, 'Evolves into...', width=140)
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
        
        EvolutionMethods = frame.Config.get(frame.rom_id, "EvolutionMethods").split(",")
        self.method = wx.ComboBox(EVO, -1, choices=EvolutionMethods,
                                            style=wx.SUNKEN_BORDER, size=(100, -1))
        self.method.Bind(wx.EVT_COMBOBOX, self.change_method)
        editor_area_a.Add(self.method, 0, wx.EXPAND | wx.ALL, 5)
        
        self.arg_txt = wx.StaticText(EVO, -1, "Argument:")
        editor_area_b.Add(self.arg_txt, 0, wx.EXPAND | wx.ALL, 5)
        
        self.arg = wx.ComboBox(EVO, -1, choices=[],
                                            style=wx.SUNKEN_BORDER, size=(100, -1))
        editor_area_b.Add(self.arg, 0, wx.EXPAND | wx.ALL, 5)
        
        poke_txt = wx.StaticText(EVO, -1, "Evolves Into:")
        editor_area_c.Add(poke_txt, 0, wx.EXPAND | wx.ALL, 5)
        
        global poke_names
        self.poke = wx.ComboBox(EVO, -1, choices=poke_names,
                                               style=wx.SUNKEN_BORDER, size=(100, -1))
        editor_area_c.Add(self.poke, 0, wx.EXPAND | wx.ALL, 5)
        
        buttons = wx.BoxSizer(wx.VERTICAL)
        
        ChangeNumberofEvos = wx.Button(EVO, 0, "Change Number of\nEvolutions per 'MON")
        self.Bind(wx.EVT_BUTTON, self.OnChangeNumberofEvos, id=0)
        buttons.Add(ChangeNumberofEvos, 0, wx.EXPAND | wx.ALL, 5)
        
        AddEvo = wx.Button(EVO, 1, "Add Evolution")
        self.Bind(wx.EVT_BUTTON, self.OnAddEvo, id=1)
        buttons.Add(AddEvo, 0, wx.EXPAND | wx.ALL, 5)
        
        RemoveEvo = wx.Button(EVO, 2, "Delete Evolution")
        self.Bind(wx.EVT_BUTTON, self.OnRemoveEvo, id=2)
        buttons.Add(RemoveEvo, 0, wx.EXPAND | wx.ALL, 5)
        
        
        vbox.Add(editor_area, 0, wx.EXPAND | wx.ALL, 5)
        
        EVO_Sizer.Add(vbox, 0, wx.EXPAND | wx.ALL, 5)
        EVO_Sizer.Add(buttons, 0, wx.EXPAND | wx.ALL, 5)
        EVO.SetSizer(EVO_Sizer)
        self.sizer.Add(EVO, 0, wx.EXPAND | wx.ALL, 5)
        self.load_everything()
        
    def OnChangeNumberofEvos(self, *args):
        NumberofEvosChanger()
        
    def OnAddEvo(self, *args):
        pass
    
    def OnRemoveEvo(self, *args):
        pass
        
    def OnSelectEvo(self, instance):
        sel = self.evo_list.GetFocusedItem()
        
        self.method.SetSelection(self.evos[sel][0])
        type = self.change_method(self.method)
        if type == 4 or 8 <= type <=14:
            self.arg.SetSelection(self.evos[sel][1]-1)
        elif type == 6 or type == 7:
            self.arg.SetSelection(self.evos[sel][1])
        else:
            self.arg.SetSelection(0)
        self.poke.SetSelection(self.evos[sel][2]-1)
        
    def change_method(self, instance):
        method = instance.GetSelection()
        if method == 4 or 8 <= method <=14: #Level type
            nums = []
            for n in range(101):
                if n != 0:
                    nums.append(str(n))
            self.arg.Clear()
            self.arg.AppendItems(nums) 
            self.arg_txt.SetLabel("Level:")
        elif method == 6 or method == 7: #Item type
            global ITEM_NAMES
            self.arg.Clear()
            self.arg.AppendItems(ITEM_NAMES) 
            self.arg_txt.SetLabel("Item:")
        else: #None type
            self.arg.Clear()
            self.arg.AppendItems(["-None needed-"]) 
            self.arg_txt.SetLabel("Argument:")
        return method
        
    def load_everything(self):
        EvolutionTable = int(frame.Config.get(frame.rom_id, "EvolutionTable"), 0)
        EvolutionsPerPoke = int(frame.Config.get(frame.rom_id, "EvolutionsPerPoke"), 0)
        LengthOfOneEntry = int(frame.Config.get(frame.rom_id, "LengthOfOneEntry"), 0)
        
        EvolutionMethods = frame.Config.get(frame.rom_id, "EvolutionMethods").split(",")
        
        global poke_num
        offset = EvolutionTable+(poke_num+1)*(LengthOfOneEntry*EvolutionsPerPoke)
        frame.open_rom.seek(offset)
        raw = frame.open_rom.read(LengthOfOneEntry*EvolutionsPerPoke)
        hexValues = get_bytes_string_from_hex_string(raw)
        self.evos = {}
        list_of_entries = []
        for n in range(EvolutionsPerPoke):
            split = hexValues[:LengthOfOneEntry*2]
            list_of_entries.append(split)
            hexValues = hexValues[LengthOfOneEntry*2:]
        for num, entry in enumerate(list_of_entries):
            method = int(entry[2:4]+entry[:2],16)
            arg = int(entry[6:8]+entry[4:6],16)
            poke = int(entry[10:12]+entry[8:10],16)
            self.evos[num] = [method,arg,poke]
        global ITEM_NAMES
        global poke_names
        self.evo_list.DeleteAllItems()
        for num, opts in self.evos.iteritems():
            index = self.evo_list.InsertStringItem(sys.maxint, EvolutionMethods[opts[0]])
            if opts[0] == 4 or 8 <= opts[0] <=14:
                need = "Level: "+str(opts[1])
            elif opts[0] == 6 or opts[0] == 7:
                need = "Item: "+ITEM_NAMES[opts[1]]
            else:
                need = "-"
            self.evo_list.SetStringItem(index, 1, need)
            if opts[0] != 0:
                self.evo_list.SetStringItem(index, 2, poke_names[opts[2]-1])
            else:
                self.evo_list.SetStringItem(index, 2, "-")

    
class PokeDexTab(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.SetSizer(sizer)
        
class EggMoveTab(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.style = wx.RAISED_BORDER|wx.TAB_TRAVERSAL
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.load_egg_moves()
        
        global poke_names
        names_buttons_vbox = wx.BoxSizer(wx.VERTICAL)
        self.POKE_NAME = wx.ComboBox(self, -1, choices=poke_names,
                                style=wx.SUNKEN_BORDER, size=(100, -1))
        names_buttons_vbox.Add(self.POKE_NAME, 0, wx.EXPAND | wx.ALL, 5)
        
        ADD_POKE =  wx.Button(self, 1, "Add Poke")
        self.Bind(wx.EVT_BUTTON, self.OnAddPoke, id=1)
        names_buttons_vbox.Add(ADD_POKE, 0, wx.EXPAND | wx.ALL, 5)

        DELETE_POKE =  wx.Button(self, 2, "Remove Poke")
        self.Bind(wx.EVT_BUTTON, self.OnDeletePoke, id=2)
        names_buttons_vbox.Add(DELETE_POKE, 0, wx.EXPAND | wx.ALL, 5)

        
        poke_names_vbox = wx.BoxSizer(wx.VERTICAL)
        self.POKES = wx.ListCtrl(self, -1, style=wx.LC_REPORT, size=(200,400))
        self.POKES.InsertColumn(0, '#', width=50)
        self.POKES.InsertColumn(1, 'Name', width=140)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelectPoke,  self.POKES)
        poke_names_vbox.Add(self.POKES, 0, wx.EXPAND | wx.ALL, 5)
        
        self.LoadPOKESList()
        
        
        moves_vbox = wx.BoxSizer(wx.VERTICAL)
        self.MOVES = wx.ListCtrl(self, -1, style=wx.LC_REPORT, size=(200,400))
        self.MOVES.InsertColumn(0, '#', width=50)
        self.MOVES.InsertColumn(1, 'Name', width=140)
        moves_vbox.Add(self.MOVES, 0, wx.EXPAND | wx.ALL, 5)
        
        moves_butons_vbox = wx.BoxSizer(wx.VERTICAL)
        global MOVES_LIST
        self.MOVE_NAME = wx.ComboBox(self, -1, choices=MOVES_LIST,
                                style=wx.SUNKEN_BORDER, size=(100, -1))
        moves_butons_vbox.Add(self.MOVE_NAME, 0, wx.EXPAND | wx.ALL, 5)
        
        ADD_POKE =  wx.Button(self, 3, "Add Move")
        self.Bind(wx.EVT_BUTTON, self.OnAddMove, id=3)
        moves_butons_vbox.Add(ADD_POKE, 0, wx.EXPAND | wx.ALL, 5)

        DELETE_POKE =  wx.Button(self, 4, "Remove Move")
        self.Bind(wx.EVT_BUTTON, self.OnDeleteMove, id=4)
        moves_butons_vbox.Add(DELETE_POKE, 0, wx.EXPAND | wx.ALL, 5)
        
        MOVE_UP = wx.Button(self, 5, "Move Up")
        self.Bind(wx.EVT_BUTTON, self.OnMoveUp, id=5)
        moves_butons_vbox.Add(MOVE_UP, 0, wx.EXPAND | wx.ALL, 5)
        
        MOVE_DOWN = wx.Button(self, 6, "Move Down")
        self.Bind(wx.EVT_BUTTON, self.OnMoveDown, id=6)
        moves_butons_vbox.Add(MOVE_DOWN, 0, wx.EXPAND | wx.ALL, 5)
        
        sizer.Add(names_buttons_vbox, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(poke_names_vbox, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(moves_vbox, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(moves_butons_vbox, 0, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(sizer)
        
    def save(self):
        string = ""
        global NewEggOffset
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
            need = int(length/2)
            self.repoint = EGG_MOVE_REPOINTER(parent=None, need=need)
            self.repoint.Bind(wx.EVT_CLOSE, self.repoint_done)
            self.repoint.Show()
        else: self.save_part2()
        
    def repoint_done(self, *args):
        self.repoint.Destroy()
        global NewEggOffset
        if self.OFFSET == NewEggOffset:
            self.save()
        else: self.save_part2()
        
    def save_part2(self, *args):
        global NewEggOffset
        NewEggOffset_pointer_form = make_pointer("08"+NewEggOffset)
        if NewEggOffset != hex(self.OFFSET)[2:].zfill(6):
            for pointer in self.POINTERS:
                frame.open_rom.seek(pointer)
                frame.open_rom.write(get_hex_from_string(NewEggOffset_pointer_form))
        
        #Fill old table with FFs
        if self.OFFSET != NewEggOffset:
            frame.open_rom.seek(self.OFFSET)
            for n in range(int(self.original_length/2)):
                frame.open_rom.write("\xff")
        
        NewEggOffset = int(NewEggOffset, 16)
        frame.open_rom.seek(NewEggOffset)
        frame.open_rom.write(self.string_to_be_written)
        
    def OnSelectPoke(self, *args):
        global MOVES_LIST
        self.MOVES.DeleteAllItems()
        
        selection = self.POKES.GetFocusedItem()
        if selection != -1:
            selection = self.POKES.GetItem(selection, 0)
            selection = int(selection.GetText())
            
            for move in self.EGG_MOVES[selection]:
                index = self.MOVES.InsertStringItem(sys.maxint, str(move))
                self.MOVES.SetStringItem(index, 1, MOVES_LIST[move])
    
    def OnAddPoke(self, *args):
        sel = self.POKE_NAME.GetSelection()
        if sel != -1:
            sel += 1
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
        global poke_names
        
        self.POKES.DeleteAllItems()
        for poke in self.EGG_MOVES:
            index = self.POKES.InsertStringItem(sys.maxint, str(poke))
            self.POKES.SetStringItem(index, 1, poke_names[poke-1])
        
    def load_egg_moves(self):
        self.EGG_MOVES = {}
        
        self.POINTERS = [int(frame.Config.get(frame.rom_id, "EggMovePointer1"), 0), int(frame.Config.get(frame.rom_id, "EggMovePointer2"), 0)]
        frame.open_rom.seek(self.POINTERS[0])
        self.OFFSET = read_pointer(frame.open_rom.read(4))
        
        frame.open_rom.seek(self.OFFSET, 0)
        number = int("0x4E20", 0)
        while True:
            read = frame.open_rom.read(2)
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
        
        SEARCH = wx.Button(pnl, 1, "Search")
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
        
        SUBMIT = wx.Button(pnl, 2, "Submit")
        self.Bind(wx.EVT_BUTTON, self.OnSubmit, id=2)
        vbox.Add(SUBMIT, 0, wx.EXPAND | wx.ALL, 5)
        
        pnl.SetSizerAndFit(vbox)
        self.Fit()
        self.SetMinSize(self.GetEffectiveMinSize())
        
    def OnSubmit(self, *args):
        sel = self.OFFSETS.GetSelection()
        offset = self.MANUAL.GetValue()
        if self.num == None:
            try: self.num = int(self.New_Move_Num.GetValue(), 0)
            except: return
        if offset != "":
            if len(offset) > 6:
                offset = offset[-6:]
            new_offset = offset.zfill(6)
            frame.tabbed_area.PokeDataTab.tabbed_area.moves.NEW_LEARNED_OFFSET = new_offset
            frame.tabbed_area.PokeDataTab.tabbed_area.moves.LEARNED_OFFSET.SetLabel("0x"+new_offset)
            frame.tabbed_area.PokeDataTab.tabbed_area.moves.NEW_NUMBER_OF_MOVES = self.num
            frame.tabbed_area.PokeDataTab.tabbed_area.moves.UPDATE_FRACTION()
            self.OnClose()
        elif sel != -1:
            new_offset = self.OFFSETS.GetString(sel)[2:]
            frame.tabbed_area.PokeDataTab.tabbed_area.moves.NEW_LEARNED_OFFSET = new_offset
            frame.tabbed_area.PokeDataTab.tabbed_area.moves.LEARNED_OFFSET.SetLabel("0x"+new_offset)
            frame.tabbed_area.PokeDataTab.tabbed_area.moves.NEW_NUMBER_OF_MOVES = self.num
            frame.tabbed_area.PokeDataTab.tabbed_area.moves.UPDATE_FRACTION()
            self.OnClose()
            
    def OnSearch(self, *args):
        self.OFFSETS.Clear()
        try:
            self.num = int(self.New_Move_Num.GetValue(), 0)
        except:
            return
        search = "\xff\xff"*self.num
        frame.open_rom.seek(0)
        rom = frame.open_rom.read()
        x = (0,True)
        start = 7602176
        for n in range(5):
            if x[1] == None:
                break
            x = (0,True)
            while x[0] != 1:
                offset = rom.find(search, start)
                if offset == -1:
                    x = (1,None)
                if offset%4 != 0:
                    start = offset+1
                    continue
                self.OFFSETS.Append(hex(offset))
                x = (1,True)
                start = offset+len(search)
                
    def OnClose(self, *args):
        self.Destroy()

class EGG_MOVE_REPOINTER(wx.Dialog):
    def __init__(self, parent, need, *args, **kw):
        wx.Dialog.__init__(self, parent=parent, id=wx.ID_ANY)
        self.SetWindowStyle( self.GetWindowStyle() | wx.STAY_ON_TOP | wx.RESIZE_BORDER )
        
        self.num = need
        self.InitUI()
        self.OnSearch()
        self.SetTitle("Repoint")

        
    def InitUI(self):

        pnl = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        txt2 = wx.StaticText(pnl, -1, "Please choose an offset to repoint to or specify\na manual offset. If a manual offset is specified,\nthe list choice will be ignored.\nNOTE: Manual offsets will NOT be checked for\nfree space availability.",style=wx.TE_CENTRE)
        vbox.Add(txt2, 0, wx.EXPAND | wx.ALL, 5)
        
        self.OFFSETS = wx.ListBox(pnl, -1)
        vbox.Add(self.OFFSETS, 0, wx.EXPAND | wx.ALL, 5)
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        manual_txt = wx.StaticText(pnl, -1, "Manual Offset: 0x",style=wx.TE_CENTRE)
        hbox.Add(manual_txt, 0, wx.EXPAND | wx.LEFT|wx.TOP|wx.BOTTOM, 5)
        self.MANUAL = wx.TextCtrl(pnl, -1,style=wx.TE_CENTRE, size=(100,-1))
        hbox.Add(self.MANUAL, 0, wx.EXPAND | wx.RIGHT|wx.TOP|wx.BOTTOM, 5)
        vbox.Add(hbox, 0, wx.EXPAND | wx.ALL, 0)
        
        SUBMIT = wx.Button(pnl, 2, "Submit")
        self.Bind(wx.EVT_BUTTON, self.OnSubmit, id=2)
        vbox.Add(SUBMIT, 0, wx.EXPAND | wx.ALL, 5)
        
        pnl.SetSizerAndFit(vbox)
        self.Fit()
        self.SetMinSize(self.GetEffectiveMinSize())
        
    def OnSubmit(self, *args):
        sel = self.OFFSETS.GetSelection()
        offset = self.MANUAL.GetValue()
        global NewEggOffset
        if offset != "":
            if len(offset) > 6:
                offset = offset[-6:]
            offset = offset.zfill(6)
            NewEggOffset = offset
        elif sel != -1:
            new_offset = self.OFFSETS.GetString(sel)[2:]
            NewEggOffset = new_offset
            self.OnClose()
        
    def OnSearch(self, *args):
        self.OFFSETS.Clear()
        search = "\xff"*self.num
        frame.open_rom.seek(0)
        rom = frame.open_rom.read()
        x = (0,True)
        start = 7602176
        for n in range(5):
            if x[1] == None:
                break
            x = (0,True)
            while x[0] != 1:
                offset = rom.find(search, start)
                if offset == -1:
                    x = (1,None)
                if offset%4 != 0:
                    start = offset+1
                    continue
                self.OFFSETS.Append(hex(offset))
                x = (1,True)
                start = offset+len(search)
                
    def OnClose(self, *args):
        self.Close()

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
        
        self.choices = ["4","5","8","16","32","64","128"]
        
        self.NewNumberChoices = wx.ComboBox(pnl, -1, choices=self.choices,
                                                    style=wx.SUNKEN_BORDER, size=(100, -1))
        vbox.Add(self.NewNumberChoices, 0, wx.EXPAND | wx.ALL, 5)
        
        txt2 = wx.StaticText(pnl, -1, "Now, you can either search for a free space offset or\n specify a manual offset for the new table.\nNOTE: Manual offsets are not checked\nfor free space content.",style=wx.TE_CENTRE)
        vbox.Add(txt2, 0, wx.EXPAND | wx.ALL, 5)
        
        self.OFFSETS = wx.ListBox(pnl, -1)
        vbox.Add(self.OFFSETS, 0, wx.EXPAND | wx.ALL, 5)
        
        SEARCH = wx.Button(pnl, 1, "Search")
        self.Bind(wx.EVT_BUTTON, self.OnSearch, id=1)
        vbox.Add(SEARCH, 0, wx.EXPAND | wx.ALL, 5)
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        manual_txt = wx.StaticText(pnl, -1, "Manual Offset: 0x",style=wx.TE_CENTRE)
        hbox.Add(manual_txt, 0, wx.EXPAND | wx.LEFT|wx.TOP|wx.BOTTOM, 5)
        self.MANUAL = wx.TextCtrl(pnl, -1,style=wx.TE_CENTRE, size=(100,-1))
        hbox.Add(self.MANUAL, 0, wx.EXPAND | wx.RIGHT|wx.TOP|wx.BOTTOM, 5)
        vbox.Add(hbox, 0, wx.EXPAND | wx.ALL, 0)
        
        SUBMIT = wx.Button(pnl, 2, "Submit")
        self.Bind(wx.EVT_BUTTON, self.OnSubmit, id=2)
        vbox.Add(SUBMIT, 0, wx.EXPAND | wx.ALL, 5)
        
        pnl.SetSizerAndFit(vbox)
        self.Fit()
        self.SetMinSize(self.GetEffectiveMinSize())
    
    def OnSubmit(self, *args):
        sel = self.OFFSETS.GetSelection()
        _offset_ = self.MANUAL.GetValue()
        
        new_number = self.NewNumberChoices.GetSelection()
        new_number = int(self.choices[new_number])
        
        EvolutionsPerPoke = int(frame.Config.get(frame.rom_id, "EvolutionsPerPoke"), 0)
        
        if new_number == EvolutionsPerPoke: return
        if _offset_ != "":
            if len(_offset_) > 6:
                _offset_ = _offset_[-7:]
        elif sel != -1:
            _offset_ = self.OFFSETS.GetString(sel)[2:]
        else: return

        ##copy table
        LengthOfOneEntry = int(frame.Config.get(frame.rom_id, "LengthOfOneEntry"), 0)
        EvolutionTable = int(frame.Config.get(frame.rom_id, "EvolutionTable"), 0)
        numberofpokes = int(frame.Config.get(frame.rom_id, "numberofpokes"), 0)
        
        readlength = EvolutionsPerPoke*LengthOfOneEntry*numberofpokes
        
        frame.open_rom.seek(EvolutionTable)
        entiretable = frame.open_rom.read(readlength)

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
        
        int_offset = _offset_[-6:]
        int_offset = int(int_offset, 16)
        frame.open_rom.seek(int_offset)
        for entry in table:
            frame.open_rom.write(entry)
        
        
        ##write new pointers.
        EvolutionTablePointers = []
        list_pointers = frame.Config.get(frame.rom_id, "EvolutionTablePointers").split(",")
        
        for offset in list_pointers:
            EvolutionTablePointers.append(int(offset, 0))
        
        if len(_offset_) == 6:
            _offset_ = "08"+_offset_
        elif len(_offset_) == 7:
            _offset_ = _offset_.zfill(8)
        else:
            _offset_ = _offset_.zfill(6)
            _offset_ = "08"+_offset_
        
        pointer = make_pointer(_offset_)
        
        pointer = get_hex_from_string(pointer)
        
        for offset in EvolutionTablePointers:
            frame.open_rom.seek(offset)
            frame.open_rom.write(pointer)
            
            
        ##Ammend the ini
        
        frame.Config.set(frame.rom_id, "EvolutionTable", "0x"+_offset_[2:])
        frame.Config.set(frame.rom_id, "EvolutionsPerPoke", str(new_number))
        
        ini = os.path.join(frame.path,"PokeRoms.ini")
        
        with open(ini, "w") as PokeRomsIni:
            frame.Config.write(PokeRomsIni)
        
        ##fill table with FF
        frame.open_rom.seek(EvolutionTable)
        for n in range(readlength):
            frame.open_rom.write("\xFF")
            
        
        ##Adjust the rom for the new ini
        
        change1 = [] #-> lsl r0, r6, #0x1 (70 00)
        tmp = frame.Config.get(frame.rom_id, "OffsetsToChangeTolslr0r60x1").split(",")
        for offset in tmp:
            change1.append(int(offset, 0))
        if new_number == 4: write = "3000"
        elif new_number == 8: write = "7000"
        elif new_number == 16: write = "B000"
        elif new_number == 32: write = "F000"
        elif new_number == 64: write = "3001"
        elif new_number == 128: write = "7001"
        else: write = "F019"
        
        change1write = binascii.unhexlify(write)
        
        for offset in change1:
            frame.open_rom.seek(offset, 0)
            frame.open_rom.write(change1write)
            
        change2 = [] #04 -> 07
        tmp = frame.Config.get(frame.rom_id, "OffsetsToChangeToNewMinus1").split(",")
        for offset in tmp:
            change2.append(int(offset, 0))

        change2write = get_hex_from_string(str(hex(new_number-1)[2:]))
        
        for offset in change2:
            frame.open_rom.seek(offset, 0)
            frame.open_rom.write(change2write)
        
        change3 = []  #-> mov r6, #0x8 (08 26)
        tmp = frame.Config.get(frame.rom_id, "OffsetToChangeTomovr60x8").split(",")
        for offset in tmp:
            change3.append(int(offset, 0))

        change3write = get_hex_from_string(str(hex(new_number)[2:])+"26")
        
        for offset in change3:
            frame.open_rom.seek(offset, 0)
            frame.open_rom.write(change3write)
            
        ##Tell the user it worked, close, and reload data.
        self.OnClose()
        DONE = wx.MessageDialog(None, 
                                "Done! Reloading 'MON Data.", 
                                'Table has been moved and evolutions have been changed.:)', 
                                wx.OK)
        DONE.ShowModal()
        frame.tabbed_area.PokeDataTab.tabbed_area.reload_tab_data()
        

        
    def OnSearch(self, *args):
        #EvolutionsPerPoke = int(frame.Config.get(frame.rom_id, "EvolutionsPerPoke"), 0)
        LengthOfOneEntry = int(frame.Config.get(frame.rom_id, "LengthOfOneEntry"), 0)
        numberofpokes = int(frame.Config.get(frame.rom_id, "numberofpokes"), 0)
        
        NewEvolutionsPerPoke = self.NewNumberChoices.GetSelection()
        if NewEvolutionsPerPoke == -1:
            return
        NewEvolutionsPerPoke = int(self.choices[NewEvolutionsPerPoke])
        
        length = LengthOfOneEntry*NewEvolutionsPerPoke*numberofpokes
        
        self.OFFSETS.Clear()
        search = "\xff"*length
        frame.open_rom.seek(0)
        rom = frame.open_rom.read()
        x = (0,True)
        start = 7602176
        for n in range(5):
            if x[1] == None:
                break
            x = (0,True)
            while x[0] != 1:
                offset = rom.find(search, start)
                if offset == -1:
                    x = (1,None)
                if offset%4 != 0:
                    start = offset+1
                    continue
                self.OFFSETS.Append(hex(offset))
                x = (1,True)
                start = offset+len(search)
                
    def OnClose(self, *args):
        self.Close()
        
app = wx.App(False)
name = "POK\xe9MON Gen III Hacking Suite"
name = encode_per_platform(name)
frame = MainWindow(None, name)

app.MainLoop()
