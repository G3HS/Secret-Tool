import wx

class Button(wx.Button):
    def __init__(self, parent, id=-1, label='',
                 pos = wx.DefaultPosition, size = wx.DefaultSize,
                 style = 0, validator = wx.DefaultValidator,
                 name = "genbutton"):
        wx.Button.__init__(self, parent, id, label, pos, size, style, validator, name)
        self.SetCursor(wx.StockCursor(wx.CURSOR_HAND))  

class ComboBox(wx.ComboBox):
    def __init__(self, parent, id=-1, value="", pos=wx.DefaultPosition, size=wx.DefaultSize, choices=[], style=0, validator=wx.DefaultValidator, name="ComboBox"):
        wx.ComboBox.__init__(self, parent, id, value, pos, size, choices, style|wx.CB_DROPDOWN|wx.TE_PROCESS_ENTER, validator, name) 
        self.Bind(wx.EVT_CHAR, self.EvtChar, self)
        self.Bind(wx.EVT_TEXT, self.SearchWhileTyping, self)
        self.Bind(wx.EVT_TEXT_ENTER, self.SearchOnHitEnter, self)
        self.ignoreEvtText = False
        
    def EvtChar(self, event):
        if event.GetKeyCode() == 8:
            self.ignoreEvtText = True
        event.Skip()
        
    def SearchWhileTyping(self, *args):
        if self.ignoreEvtText:
            self.ignoreEvtText = False
            return
        currentText = self.GetValue()
        items = self.GetItems()
        for item in items:
            if item.startswith(currentText) or item.startswith(currentText.upper()) or item.startswith(currentText.lower()):
                index = self.FindString(item)
                self.SetSelection(index)
                cmd = wx.CommandEvent(wx.EVT_COMBOBOX.evtType[0])
                cmd.SetEventObject(self) 
                cmd.SetId(self.GetId())
                self.GetEventHandler().ProcessEvent(cmd) 
                self.SetInsertionPoint(len(currentText))
                self.SetMark(len(currentText), len(item))
                break
                
    def SearchOnHitEnter(self, instance):
        index = self.FindString(self.GetValue())
        if index != -1:
            self.SetSelection(index)
        else:
            index = self.FindString(self.GetValue().upper())
            if index != -1:
                self.SetSelection(index)
            else:
                index = self.FindString(self.GetValue().lower())
                if index != -1:
                    self.SetSelection(index)
        cmd = wx.CommandEvent(wx.EVT_COMBOBOX.evtType[0])
        cmd.SetEventObject(self) 
        cmd.SetId(self.GetId())
        self.GetEventHandler().ProcessEvent(cmd) 
        
        
        