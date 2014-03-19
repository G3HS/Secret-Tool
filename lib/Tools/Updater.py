import os
import wx
import urllib2
import time
import ConfigParser
from GLOBALS import *
import platform, locale
from zipfile import ZipFile
import shutil
from threading import Thread
from wx.lib.pubsub import Publisher as pub
from subprocess import Popen
 
########################################################################
class DownloadThread(Thread):
    """Downloading thread"""
 
    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        Thread.__init__(self)
        self.start()
 
    #----------------------------------------------------------------------
    def run(self):
        """
        Run the worker thread
        """
        url = "https://github.com/thekaratekid552/"\
        "Secret-Tool/releases/download/"\
            "{0}/{1}".format(Globals.latestRelease["name"],
                             Globals.ZIPName)
        
        file_name = url.split('/')[-1]
        Globals.DownloadedZipName = file_name
        u = urllib2.urlopen(url)
        f = open(file_name, 'w+b')
        meta = u.info()
        self.fsize = int(meta.getheaders("Content-Length")[0])
        wx.CallAfter(pub.sendMessage, 
                     "set_range_gauge",
                     data=self.fsize)
        total_size = 0
        block_sz = 1024
        while True:
            buffer = u.read(block_sz)
            if not buffer:
                break

            total_size += len(buffer)
            f.write(buffer)
            if total_size < self.fsize:
                wx.CallAfter(pub.sendMessage, 
                                "update_gauge",
                                data=total_size)
        wx.CallAfter(pub.sendMessage,
                     "update_gauge",
                     data=self.fsize)
        wx.CallAfter(pub.sendMessage,
                     "ContinueUpdate",
                     data="DownloadComplete")
        f.close()
        
class UnpackThread(Thread):
    """Unpacking thread"""
    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        Thread.__init__(self)
        self.start()
 
    #----------------------------------------------------------------------
    def run(self):
        with ZipFile(Globals.DownloadedZipName, 'r') as updatezip:
            self.UpdateGauge(25)
            tmpdir = os.path.join(os.getcwd(),"tmp")
            self.UpdateGauge(50)
            try: os.mkdir(tmpdir)
            except:
                shutil.rmtree(tmpdir)
                os.mkdir(tmpdir)
            self.UpdateGauge(75)
            ZipFile.extractall(updatezip,tmpdir)
            self.UpdateGauge(100)
            
            self.UpdateGauge(0)
            self.UpdateStatus("Copying resources....")
            #Move new resources folder out.
            try: shutil.rmtree(os.path.join(os.getcwd(),'Resources'))
            except: pass
            root_src_dir = os.path.join(tmpdir,"Resources")
            root_target_dir = os.path.join(os.getcwd(),'Resources')
            x = 0
            for src_dir, dirs, files in os.walk(root_src_dir):
                dst_dir = src_dir.replace(root_src_dir, root_target_dir)
                if not os.path.exists(dst_dir):
                    os.mkdir(dst_dir)
                for file_ in files:
                    x += 5
                    self.UpdateGauge(x)
                    src_file = os.path.join(src_dir, file_)
                    dst_file = os.path.join(dst_dir, file_)
                    if os.path.exists(dst_file):
                        os.remove(dst_file)
                    shutil.move(src_file, dst_dir))
                        
            self.UpdateGauge(100)
            self.UpdateGauge(0)
            self.UpdateStatus("Copying documentation....")
            #Move documentation
            try: os.remove(os.path.join(os.getcwd(),"G3HS_Documentation.pdf"))
            except: pass
            self.UpdateGauge(50)
            NewDocLoc = os.path.join(os.getcwd(),'tmp',"G3HS_Documentation.pdf")
            shutil.move(NewDocLoc, os.path.join(os.getcwd()))
            self.UpdateGauge(100)
            
            
            self.UpdateGauge(0)
            self.UpdateStatus("Merging ini....")
            #Merge ini
            iniloc = os.path.join(tmpdir, "PokeRoms.ini")
            orginiloc = os.path.join(os.getcwd(), "PokeRoms.ini")
            NewIni = ConfigParser.ConfigParser().read(iniloc)
            NewRomSections = NewIni.sections()
            #Check if all sections are present:
            OldRomSections = Globals.INI.sections()
            #Get any new sections I may have added.
            #Update any current base sections.
            for section in NewRomSections:
                NewOptions = NewRomSections.options(section)
                NewIni = []
                OldOptions = Globals.INI.options(section)
                for opt in NewOptions:
                    NewIni.append((opt, 
                                    NewRomSections.options(section, opt)))
                if section not in OldRomSections:
                    Globals.INI.add_section(section)
                    for opt, value in NewIni:
                        Globals.INI.set(section, opt, value)
                else:
                    for opt in NewOptions:
                        if opt not in OldOptions:
                            Globals.INI.set(section, opt, 
                                            NewRomSections.get(section, opt))
            for section in OldRomSections:
                if section is not "ALL":
                    gamecode = Globals.INI.get(section, "gamecode")
                else: return
                UpdateOpts = NewRomSections.options(section)
                NewUpdateSections = []
                for opt in UpdateOpts:
                    NewUpdateSections.append((opt, 
                                        NewRomSections.options(gamecode, opt)))
                OldOpts = Globals.INI.options(section)
                OldOptsLst = []
                for opt in OldOpts:
                    Globals.INI.append((opt, 
                                        Globals.INI.options(section, opt)))
                for opt, value in NewUpdateSections:
                    if opt not in OldOpts:
                        Globals.INI.set(section, opt, value)
                        
            with open(orginiloc, "w") as PokeRomsIni:
                Globals.INI.write(PokeRomsIni)
            
            self.UpdateGauge(100)
            
            #Replace exe
            self.UpdateStatus("G3HS will now exit, complete the update, and restart.")
            
            time.sleep(5)
            try: popen = Popen([".\Finish.sh"])
            except: 
                try: popen = Popen([".\Finish.bat"])
                except:
                    print "Failed"
            wx.CallAfter(pub.sendMessage, "CloseG3HS")

    def UpdateGauge(self, data):
        wx.CallAfter(pub.sendMessage, "update_gauge",data=data)
        
    def UpdateStatus(self, status):
        wx.CallAfter(pub.sendMessage, "UpdateStatus",data=status)
            
########################################################################
class MyGauge(wx.Gauge):
    """"""
 
    #----------------------------------------------------------------------
    def __init__(self, parent):
        """Constructor"""
        wx.Gauge.__init__(self, parent, range=0)
        pub.subscribe(self.updateProgress, "update_gauge")
        pub.subscribe(self.SetRangeOfFile, "set_range_gauge")
 
    #----------------------------------------------------------------------
    def updateProgress(self, msg):
        """"""
        self.SetValue(msg.data)
    #----------------------------------------------------------------------
    def SetRangeOfFile(self, range):
        self.SetRange(range.data)
 
########################################################################
class MyPanel(wx.Panel):
    """"""
    #----------------------------------------------------------------------
    def __init__(self, parent):
        """Constructor"""
        wx.Panel.__init__(self, parent)
 
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.status = wx.StaticText(self, label="")
        self.main_sizer.Add(self.status,0,wx.ALL|wx.ALIGN_CENTER_HORIZONTAL,20)
        self.gauge = MyGauge(self)
        self.main_sizer.Add(self.gauge, 0, wx.ALL|wx.EXPAND, 10)
 
        self.SetSizer(self.main_sizer)
        self.SetAutoLayout(1)
        self.Update()
        pub.subscribe(self.Update, "ContinueUpdate")
        pub.subscribe(self.ChangeStatus, "UpdateStatus")

 
    #----------------------------------------------------------------------
    def Update(self, msg=None):
        if msg == None:
            DownloadThread()
            self.status.SetLabel("Downloading update....")
        else:
            if msg.data == "DownloadComplete":
                self.status.SetLabel("Download Complete.")
                time.sleep(2)
                self.status.SetLabel("Unpacking update")
                self.gauge.SetRange(100)
                self.gauge.SetValue(0)
                UnpackThread()
                
    def ChangeStatus(self, msg):
        self.status.SetLabel(msg.data)
        
########################################################################
class DownloaderDialog(wx.Dialog):
    def __init__(self, parent=None, id=wx.ID_ANY):
        wx.Dialog.__init__(self, parent, title="Updater", size=(600, 300))
        panel = MyPanel(self)
        self.Show()
 
#----------------------------------------------------------------------
if __name__ == "__main__":
    app = wx.App(False)
    frame = DownloaderDialog()
    app.MainLoop()
