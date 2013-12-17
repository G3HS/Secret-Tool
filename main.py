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
        
        panel = wx.Panel(self)
        
        tabbed_area = TabbedEditorArea(panel)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(tabbed_area, 1, wx.ALL|wx.EXPAND, 5)
        panel.SetSizer(sizer)
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
        open_dialog = wx.FileDialog(self, message="Open a rom...", defaultDir=os.getcwd(),
                                                        style=wx.OPEN)
        if open_dialog.ShowModal() == wx.ID_OK:
            filename = open_dialog.GetPath()
            self.open_rom = open(filename, "r+b")
            
            #Here we are going to check if the game has been opened before.
            #If yes, load it's custom ini. If no, create its ini.
            Config = ConfigParser.ConfigParser()
            ini = os.path.join(self.path,"PokeRoms.ini")
            Config.read(ini)
            
            rom_id_offset_hex = str(Config.get("ALL", "OffsetThatContainsSecondRomID"))
            rom_id_offset = get_decimal_offset_from_hex_string(rom_id_offset_hex)
            
            self.open_rom.seek(rom_id_offset) #Seek to last 2 bytes in rom
            self.rom_id = self.open_rom.read(2)
            self.rom_id = str(binascii.hexlify(self.rom_id)) 

            all_possible_rom_ids = Config.sections()
            
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
                        
                        Config.add_section(self.rom_id)
                        options = Config.options(game_code)
                        tmp_ini = {}
                        for opt in options:
                            tmp_ini[opt] = Config.get(game_code, opt)
                            
                        for opt, value in tmp_ini.items():
                            Config.set(self.rom_id, opt, value)
                        with open(ini, "w") as PokeRomsIni:
                            Config.write(PokeRomsIni)
                        y = True
                

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
        PokeDataTab.SetBackgroundColour("Gray")
        self.AddPage(PokeDataTab, "Pokemon Data Editor")
        
        
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.OnPageChanging)
        
    def OnPageChanged(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        #print 'OnPageChanged,  old:%d, new:%d, sel:%d\n' % (old, new, sel)
        event.Skip()

    def OnPageChanging(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        #print 'OnPageChanging, old:%d, new:%d, sel:%d\n' % (old, new, sel)
        event.Skip()

        
#############################################################
#This tab will allow editing of Pokemon Stats, moves, etc
#############################################################
class PokemonDataEditor(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        tabbed_area = DataEditingTabs(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(tabbed_area, 1, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(sizer)
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
        
        #print 'OnPageChanged,  old:%d, new:%d, sel:%d\n' % (old, new, sel)
        event.Skip()

    def OnPageChanging(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        #print 'OnPageChanging, old:%d, new:%d, sel:%d\n' % (old, new, sel)
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