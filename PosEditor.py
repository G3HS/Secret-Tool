import wx, os

class PosEditorBase():
    def __init__(self, parent, FrontSprite=None, BackSprite=None):
        self.parent = parent
        self.FS = FrontSprite
        self.BS = BackSprite
        self.BG = wx.Bitmap(os.path.join("Resources","BattleBG.png"),wx.BITMAP_TYPE_PNG)
        self.Shadow = wx.Image(os.path.join("Resources","Shadow.png"))
        self.Shadow.ConvertAlphaToMask()
        self.Shadow = wx.BitmapFromImage(self.Shadow)
        
        self.TB = wx.Bitmap(os.path.join("Resources","BattleTextBox.png"),wx.BITMAP_TYPE_PNG)
        
        self.RECTS = [0,0,0]
        self.EnemyY = 0
        
    def OnPaint(self, event):
        DC = wx.PaintDC(self.parent)
        DC.DrawBitmap(self.BG,0, 0)
        if self.RECTS[2] != 0:
            DC.DrawBitmap(self.Shadow,160,65,True)
        if self.FS != None:
            DC.DrawBitmap(self.FS,144, self.RECTS[1],True)
        if self.BS != None:
            DC.DrawBitmap(self.BS,40, self.RECTS[0],True)
        
        DC.DrawBitmap(self.TB,0, 112)
        
    def UpdateFSandDS(self, SpriteTabObj):
        self.LoadFSandBS(SpriteTabObj.TMPFrontSprite,SpriteTabObj.TMPSBackSprite)
        SpriteTabObj.Refresh()
        
    def LoadFSandBS(self, FS, BS):
        self.FS = FS
        tmp = self.FS.ConvertToImage()
        color = (tmp.GetRed(0,0), tmp.GetGreen(0,0), tmp.GetBlue(0,0))
        self.FS.SetMaskColour(color)
        del tmp
        
        self.BS = BS
        tmp = self.BS.ConvertToImage()
        color = (tmp.GetRed(0,0), tmp.GetGreen(0,0), tmp.GetBlue(0,0))
        self.BS.SetMaskColour(color)
        del tmp
        
    def ChangePlayerY(self, event):
        event = event.GetEventObject()
        self.RECTS[0] = 48+event.GetValue()
        self.parent.Refresh()
        
    def ChangeEnemyY(self, event):
        event = event.GetEventObject()
        self.EnemyY = event.GetValue()
        self.RECTS[1] = 8+self.EnemyY-self.RECTS[2]
        self.parent.Refresh()
        
    def ChangeEnemyAlt(self, event):
        event = event.GetEventObject()
        self.RECTS[2] = event.GetValue()
        self.RECTS[1] = 8+self.EnemyY-self.RECTS[2]
        self.parent.Refresh()
        