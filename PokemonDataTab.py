import wx

class PokemonDataEditor(wx.Panel):
    #This tab will allow editing of Pokemon Stats, moves, etc
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.SetSizer(sizer)