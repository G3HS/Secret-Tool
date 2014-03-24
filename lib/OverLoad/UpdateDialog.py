import wx
import webbrowser
try: from wx.lib.pubsub import Publisher as pub
except: 
    from wx.lib.pubsub import setuparg1
    from wx.lib.pubsub import pub
from lib.Tools.Updater import DownloaderDialog

class UpdateDialog(wx.Dialog):
    def __init__(self, parent, Message):
        wx.Dialog.__init__(self, parent, id=wx.NewId(), title="Update is available...")
        self.SetWindowStyle( self.GetWindowStyle() | wx.STAY_ON_TOP | wx.RESIZE_BORDER )
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        MSG = wx.StaticText(self, -1,Message)
       
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        autoButton = wx.Button(self, label='Auto-Update')
        manualButton = wx.Button(self, label='Manual-Update')
        noButton = wx.Button(self, label='No')
        hbox2.Add(autoButton, flag=wx.ALL, border=5)
        hbox2.Add(manualButton, flag=wx.ALL, border=5)
        hbox2.Add(noButton, flag=wx.ALL, border=5)

        vbox.Add(MSG, proportion=1, 
            flag=wx.ALL|wx.EXPAND, border=5)
        vbox.Add(hbox2, 
            flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=10)

        self.SetSizer(vbox)
        
        autoButton.Bind(wx.EVT_BUTTON, self.OnAuto)
        manualButton.Bind(wx.EVT_BUTTON, self.OnManual)
        noButton.Bind(wx.EVT_BUTTON, self.OnClose)
        
        self.SetSizerAndFit(vbox)
        self.Fit()
        self.SetMinSize(self.GetEffectiveMinSize())
        self.ShowModal()
        
    def OnManual(self, event=None):
        webbrowser.open("http://adf.ly/5621614/g3hs-releases")
        wx.CallAfter(pub.sendMessage, "CloseG3HS")
        self.OnClose()
        
    def OnAuto(self, event=None):
        Globals.latestRelease = latestRelease
        DownloaderDialog(frame)
        self.OnClose()
        
    def OnClose(self, event=None):
        self.Destroy()
