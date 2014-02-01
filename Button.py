import wx

class Button(wx.Button):
    def __init__(self, parent, id=-1, label='',
                 pos = wx.DefaultPosition, size = wx.DefaultSize,
                 style = 0, validator = wx.DefaultValidator,
                 name = "genbutton"):
        wx.Button.__init__(self, parent, id, label, pos, size, style, validator, name)
        self.SetCursor(wx.StockCursor(wx.CURSOR_HAND))  
        