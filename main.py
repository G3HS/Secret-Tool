import wx, os
from TabbedDataPanel import *

OPEN = 1
open_rom = None

class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(800,600))
        
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
            with open(filename, "r+b") as file:
                open_rom = file
                
app = wx.App(False)
frame = MainWindow(None, "Pokemon Gen III Hacking Suite")
app.MainLoop()