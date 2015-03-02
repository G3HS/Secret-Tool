import wx
import smtplib
from email.mime.text import MIMEText
import time
import sys, os
import platform


class EmailError(wx.Dialog):
    def __init__(self, parent=None, error=None, version=None, *args, **kw):
        wx.Dialog.__init__(self, parent=parent, id=wx.ID_ANY)
        self.SetWindowStyle(self.GetWindowStyle()|wx.STAY_ON_TOP|wx.RESIZE_BORDER|wx.OK|wx.ICON_ERROR)
        system_info = "\n\nSystem Info:\n{0}\n{1}\nG3HS {2}".format(sys.platform, platform.platform(),version)
        self.Error = error+system_info
        self.Report = self.Error
        
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        txt = wx.StaticText(self, -1, "You have requested that this crash report be sent.\nCan you please provide any more details?",style=wx.TE_CENTRE)
        vbox.Add(txt, 0, wx.EXPAND | wx.ALL, 5)
        
        Entry = wx.TextCtrl(self, wx.ID_ANY, style=wx.TE_MULTILINE, size=(400,100))
        Entry.Bind(wx.EVT_TEXT, self.GetInfo)
        vbox.Add(Entry, 0, wx.ALL, 5)
        
        OK = self.CreateButtonSizer(wx.OK)
        vbox.Add(OK, 0, wx.EXPAND | wx.ALL, 5)
        
        txt3 = wx.StaticText(self, -1, "All reports are completely anonymous.\nHave no fear, they only help karatekid552 fix bugs.\nYour platform and OS version will be sent too.",style=wx.TE_CENTRE)
        vbox.Add(txt3, 0, wx.EXPAND | wx.ALL, 15)
        
        self.SetSizerAndFit(vbox)
        self.Fit()
        self.SetMinSize(self.GetEffectiveMinSize())
        
    def GetInfo(self, instance):
        instance = instance.GetEventObject()
        self.Report = self.Error+"\n\nMessage:\n"+instance.GetValue()
    
    def SendCrashReport(self):
        #I know this is blatent. Just don't abuse my trust.
        address = "G3HSCrashReports@gmail.com"
        password = "OneToolToRuleThemAll"
        ErrorTime = time.strftime("%H:%M:%S")+" "+time.strftime("%m/%d/%Y")
        msg = MIMEText(self.Report)
        msg["Subject"] = "Error at "+ErrorTime
        msg["From"] = address
        msg["To"] = address
        
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.ehlo()
        server.starttls()
        server.login(address,password)
        server.sendmail(address,address,msg.as_string())
        server.quit()

        
class ContactDialog(wx.Dialog):
    def __init__(self, parent=None, *args, **kw):
        wx.Dialog.__init__(self, parent=parent, id=wx.ID_ANY)
        self.SetWindowStyle( self.GetWindowStyle()|wx.STAY_ON_TOP|wx.RESIZE_BORDER|wx.OK|wx.ICON_ERROR)
        
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        txt = wx.StaticText(self, -1, "(user)name:")
        vbox.Add(txt, 0, wx.EXPAND | wx.ALL, 5)
        
        self.ContactersName = wx.TextCtrl(self, wx.ID_ANY, size=(400,-1))
        vbox.Add(self.ContactersName, 0, wx.ALL, 5)
        
        txt2 = wx.StaticText(self, -1, "return email for reply:")
        vbox.Add(txt2, 0, wx.EXPAND | wx.ALL, 5)
        
        self.Email = wx.TextCtrl(self, wx.ID_ANY, size=(400,-1))
        vbox.Add(self.Email, 0, wx.ALL, 5)
        
        txt3 = wx.StaticText(self, -1, "message:")
        vbox.Add(txt3, 0, wx.EXPAND | wx.ALL, 5)
        
        self.Entry = wx.TextCtrl(self, wx.ID_ANY, style=wx.TE_MULTILINE, size=(400,100))
        vbox.Add(self.Entry, 0, wx.ALL, 5)
        
        OK = self.CreateButtonSizer(wx.OK)
        vbox.Add(OK, 0, wx.EXPAND | wx.ALL, 5)
        
        self.SetSizerAndFit(vbox)
        self.Fit()
        self.SetMinSize(self.GetEffectiveMinSize())
    
    def Send(self):
        email = self.Email.GetValue()
        name = self.ContactersName.GetValue()
        message = self.Entry.GetValue()
        
        body = "Message from {0}:\n\n{1}\n\nReply email is {2}".format(name, message, email)
        #I know this is blatent. Just don't abuse my trust.
        address = "G3HSCrashReports@gmail.com"
        password = "OneToolToRuleThemAll"
        ErrorTime = time.strftime("%H:%M:%S")+" "+time.strftime("%m/%d/%Y")
        msg = MIMEText(body)
        msg["Subject"] = "Message at "+ErrorTime+" from "+name
        msg["From"] = address
        msg["To"] = address
        
        self.Report = "Subject:\n"+msg["Subject"]+"\n\n"+"Body:\n"+body
        
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.ehlo()
        server.starttls()
        server.login(address,password)
        server.sendmail(address,address,msg.as_string())
        server.quit()