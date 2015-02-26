import wx

class ErrorDialog():
    def __init__(parent, msg, title):
        ERROR = wx.MessageDialog(parent,msg,title,wx.OK|wx.ICON_ERROR)
        ERROR.ShowModal()