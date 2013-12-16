import wx


class PokemonDataEditor(wx.Panel):
    #This tab will allow editing of Pokemon Stats, moves, etc
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
        
        
"""
~Stats structure
http://bulbapedia.bulbagarden.net/wiki/Pok%C3%A9mon_base_stats_data_structure_in_Generation_III
BPRE Main stats @0x2547A0:
28/0x1C Long

+0 HP [1]
+1 ATK [1]
+2 DEF [1]
+3 SPD[1]
+4 SPATK [1]
+5 SPDEF[1]

+6 Type1 [1]
+7 Type2 [1]

+8 Catch Rate[1]
+9 BaseExp[1]
+10 Evs: [2] (HP, ATK, DEF | SAT, SDF, SPD) Stored in bits, so SPD|DEF|ATK|HP --|--|SDF|SAT

+12 Item1 [2] Reverse Hex
+14 Item2 [2] Reverse Hex

+16 Gender [1]
+17 Steps to hatch[1] Value*256d = real steps

+18 BaseFriendship[1]
+19 Level-up Type [1] 
+20 EggGroup1 [1]
+21 EggGroup2 [1]
+22 Ability1 [1]
+23 Ability2 [1]

+24 SafariRunRate [1]
+25 Color
 
 +26 Padding [2]

"""