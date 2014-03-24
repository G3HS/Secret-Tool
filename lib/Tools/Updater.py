import os
import wx
import urllib2
import time
import ConfigParser
import sys
from GLOBALS import *
import platform, locale
from zipfile import ZipFile
import shutil
from threading import Thread
from subprocess import Popen
"""
There are two version of the publisher library in wxPython. Only one gets
put in the final execuatable. This attempts to load either to be safe.
"""
try: from wx.lib.pubsub import Publisher as pub
except: 
    print "Changing pub mode"
    from wx.lib.pubsub import setuparg1
    from wx.lib.pubsub import pub
    
class DownloadThread(Thread):
    """Downloading thread"""
    def __init__(self):
        Thread.__init__(self)
        self.start()
        
    def run(self):
        """
        Run the download thread-
        When main.py is run, it will download the information on the latest
        release. If there is an update, then that information gets passed
        to Globals.latestRelease. This builds the url for the proper update.
        
        Globals.ZIPName determines which file should be downloaded for the 
        update. This is set before building by the person who is compiling.
        """
        url = "https://github.com/thekaratekid552/"\
        "Secret-Tool/releases/download/"\
            "{0}/{1}".format(Globals.latestRelease["name"],
                             Globals.ZIPName)
        
        #Need to access this file during the unpack.
        Globals.DownloadedZipName = url.split('/')[-1] #Filename
        #Five tries to access the url with a 2 second wait in between.
        for x in range(5):
            try: u = urllib2.urlopen(url)
            except:
                if x == 4:
                    return False
                else:
                    time.sleep(2)
                    continue
        
        f = open(Globals.DownloadedZipName, 'w+b')
        #Get the size of the download.
        meta = u.info()
        fsize = int(meta.getheaders("Content-Length")[0])
        #Set the size of the download bar to the size of the download.
        wx.CallAfter(pub.sendMessage, "set_range_gauge", data=fsize)
        #Download the update.
        total_size = 0
        block_sz = 1024
        while True:
            buffer = u.read(block_sz)
            if not buffer:
                break

            total_size += len(buffer)
            f.write(buffer)
            if total_size < fsize:
                #Update the download bar.
                wx.CallAfter(pub.sendMessage, "update_gauge", data=total_size)
        #Max out the download bar.
        wx.CallAfter(pub.sendMessage,"update_gauge",data=fsize)
        #Proceed to next phase of the update.
        wx.CallAfter(pub.sendMessage,"ContinueUpdate",data="DownloadComplete")
        f.close()
        return
        
class UnpackThread(Thread):
    """Unpacking thread"""
    def __init__(self):
        Thread.__init__(self)
        self.start()
 
    def run(self):
        """
        The zip file contains 5 objects:
        -Resources folder
        -PDF Documentation
        -Finish.sh/Finish.bat (UNIX/DOS)
        -The new execuatable
        -The new config (ini) file
        
        All need to be unpacked and properly distributed.
        
        The progress bar and status are updated throughout using the 
        UpdateGauge(), PulseGauge(), and UpdateStatus() methods. For the most 
        part, this process happens withen a half-second, so those don't so 
        much. However, if the process is for some reason slowed down, these
        will show activity.
        """
        with ZipFile(Globals.DownloadedZipName, 'r') as updatezip:
            self.UpdateGauge(25)
            #Create a tmp directory.
            tmpdir = os.path.join(os.getcwd(),"tmp")
            self.UpdateGauge(50)
            try: os.mkdir(tmpdir)
            except:
                shutil.rmtree(tmpdir)
                os.mkdir(tmpdir)
            self.UpdateGauge(75)
            #Extrace everything.
            ZipFile.extractall(updatezip,tmpdir)
            self.UpdateGauge(100)
            
            self.UpdateGauge(0)
            #Move new resources folder out.
            self.PulseGauge()
            self.UpdateStatus("Copying resources....")
            try: shutil.rmtree(os.path.join(os.getcwd(),'Resources'))
            except: pass
            #Set the locations of the new and old resources folder.
            NewResources = os.path.join(tmpdir,"Resources")
            OldResources = os.path.join(os.getcwd(),'Resources')
            #Recusively copy every file. Thanks stackoverflow!:D
            x = 0
            for src_dir, dirs, files in os.walk(NewResources):
                dst_dir = src_dir.replace(NewResources, OldResources)
                if not os.path.exists(dst_dir):
                    os.mkdir(dst_dir)
                for file_ in files:
                    self.PulseGauge()
                    src_file = os.path.join(src_dir, file_)
                    dst_file = os.path.join(dst_dir, file_)
                    if os.path.exists(dst_file):
                        os.remove(dst_file)
                    shutil.move(src_file, dst_dir)      
            self.UpdateGauge(100)
            
            self.UpdateGauge(0)
            #Move documentation
            self.UpdateStatus("Copying documentation....")
            try: os.remove(os.path.join(os.getcwd(),"G3HS_Documentation.pdf"))
            except: pass
            self.UpdateGauge(50)
            NewDocLoc = os.path.join(os.getcwd(),'tmp',"G3HS_Documentation.pdf")
            shutil.move(NewDocLoc, os.path.join(os.getcwd()))
            self.UpdateGauge(100)
            
            self.UpdateGauge(0)
            """
            This part of the operation is delicate. The old config file contains
            a lot of custom data. This needs to be saved between updates.
            However, updated usually include new options due to increased
            functionality. So, the new sections and options in the updated
            ini need to added to the old ini without destroying the custom
            options.
            """
            self.UpdateStatus("Merging ini....")
            iniloc = os.path.join(tmpdir, "PokeRoms.ini")
            orginiloc = os.path.join(os.getcwd(), "PokeRoms.ini")
            #Backup ini
            BackUpIni = os.path.join(os.getcwd(),"PokeRoms.ini.bak")
            shutil.copy(orginiloc, BackUpIni)
            #Load up our new config file for parsing.
            NewIni = ConfigParser.ConfigParser()
            NewIni.read(iniloc)
            NewRomSections = NewIni.sections()
            #Check if all sections are present:
            OldRomSections = Globals.INI.sections()
            #Get any new sections I may have added and 
            #update any current base sections.
            self.PulseGauge()
            for section in NewRomSections:
                self.PulseGauge()
                NewOptions = NewIni.options(section)
                NewOptsValues = []
                OldOptions = Globals.INI.options(section)
                for opt in NewOptions:
                    NewOptsValues.append((opt, NewIni.get(section, opt)))
                if section not in OldRomSections:
                    Globals.INI.add_section(section)
                    for opt, value in NewOptsValues:
                        Globals.INI.set(section, opt, value)
                else:
                    for opt in NewOptions:
                        if opt not in OldOptions:
                            Globals.INI.set(section, opt, 
                                            NewIni.get(section, opt))
            #Now, go through every section of the old ini and make sure it
            #has every singe option the new ini has.
            for section in OldRomSections:
                self.PulseGauge()
                #The custom sections of the old ini are not found in the 
                #new ini. So, the new options are copied from their base
                #sections found in the new ini.
                if section != "ALL":
                    gamecode = Globals.INI.get(section, "gamecode")
                else: continue
                UpdateOpts = NewIni.options(gamecode)
                NewUpdateOptsValues = []
                #Get all of the options from the new ini for the section.
                for opt in UpdateOpts:
                    NewUpdateOptsValues.append((opt, 
                                        NewIni.get(gamecode, opt)))
                #If option is not found, add it.
                OldOpts = Globals.INI.options(section)
                for opt, value in NewUpdateOptsValues:
                    if opt not in OldOpts:
                        Globals.INI.set(section, opt, value)
            #Write the new changes.
            with open(orginiloc, "w") as PokeRomsIni:
                Globals.INI.write(PokeRomsIni)
            
            #Fool the user into thinking I'm loading the new ini.:P
            #If they even see this..... Haha
            self.UpdateGauge(0)
            self.UpdateGauge(25)
            self.UpdateGauge(75)
            self.UpdateGauge(100)
            
            #Now, since we can't replace the exe while it is running, we
            #tell it to run a bash/batch script to do that for us after the 
            #exe exits.
            self.UpdateStatus("G3HS will now exit, complete "\
                                              "the update, and restart.")
            
            #Make sure the user has time to read the above status.
            time.sleep(5)
            if sys.platform == 'linux2':
                #Give exe permission.
                os.chmod(os.path.join(os.getcwd(),"tmp","Gen_III_Suite"), 0766)
                os.chmod(os.path.join(os.getcwd(),"tmp","Finish.sh"), 0766)
                try: popen = Popen(os.path.join(os.getcwd(),"tmp","Finish.sh"))
                except: print os.path.join(os.getcwd(),"tmp","Finish.sh")
            else:
                try: popen = Popen(os.path.join(os.getcwd(),"tmp","Finish.bat"))
                except:
                    pass
            #Exit the program so the bash/batch script can run.
            wx.CallAfter(pub.sendMessage, "CloseG3HS")

    def UpdateGauge(self, data):
        """
        Update the progess bar. 
        Doesn't really do much for the user unless their computer is running 
        reaaaally slow.
        """
        wx.CallAfter(pub.sendMessage, "update_gauge",data=data)
        
    def UpdateStatus(self, status):
        """Update the status."""
        wx.CallAfter(pub.sendMessage, "UpdateStatus",data=status)

    def PulseGauge(self, data=None):
        """Pulse the progress bar to show activity."""
        wx.CallAfter(pub.sendMessage, "PULSE")
            
class MyGauge(wx.Gauge):
    def __init__(self, parent):
        """
        This is the progress bar. It is set up to allow remote updating of 
        itself from a different thread via the publisher/subscribe methods
        built into wxPython.
        """
        wx.Gauge.__init__(self, parent, range=0)
        pub.subscribe(self.updateProgress, "update_gauge")
        pub.subscribe(self.SetRangeOfFile, "set_range_gauge")
        pub.subscribe(self.DoPulse, "PULSE")
 
    def updateProgress(self, msg):
        """
        Update the progess bar. 
        Doesn't really do much for the user unless their computer is running 
        reaaaally slow.
        """
        self.SetValue(msg.data)
        
    def SetRangeOfFile(self, range):
        """Update the range of the bar."""
        self.SetRange(range.data)
    
    def DoPulse(self, data=None):
        """Pulse the progress bar to show activity."""
        self.Pulse()
 
class MyPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        """
        This is the lovely main panel of our updater.
        """
        #Create the layout.
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.status = wx.StaticText(self, label="")
        self.main_sizer.Add(self.status,0,wx.ALL|wx.ALIGN_CENTER_HORIZONTAL,20)
        self.gauge = MyGauge(self)
        self.main_sizer.Add(self.gauge, 0, wx.ALL|wx.EXPAND, 10)
        #Finalize the layout.
        self.SetSizer(self.main_sizer)
        self.SetAutoLayout(1)
        self.Update()
        #Allow contact from other threads.
        pub.subscribe(self.Update, "ContinueUpdate")
        pub.subscribe(self.ChangeStatus, "UpdateStatus")

    def Update(self, msg=None):
        """
        This function does two things:
        1) If it is called with msg == None, it downloads the file.
        2) If it is called with msg == "DownloadComplete", it will unpack the
           zip file and do all of that.
        """
        if msg == None:
            DownloadThread()
            self.status.SetLabel("Downloading update....")
        else:
            if msg.data == "DownloadComplete":
                self.status.SetLabel("Download Complete.")
                #Give the user time to digest that this is really happening.:D
                time.sleep(2)
                self.status.SetLabel("Unpacking update")
                self.gauge.SetRange(100)
                self.gauge.SetValue(0)
                UnpackThread()
                
    def ChangeStatus(self, msg):
        """Update the status."""
        self.status.SetLabel(msg.data)
        
class DownloaderDialog(wx.Dialog):
    def __init__(self, parent=None, id=wx.ID_ANY):
        wx.Dialog.__init__(self, parent, title="Updater", size=(600, 300))
        """
        Make the download dialog and suspend main.py while it runs.
        """
        panel = MyPanel(self)
        self.ShowModal()
