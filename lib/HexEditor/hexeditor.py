#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Copyright 2013 Gully Chen
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Author:  CChen
# Purpose: Hex editor based on wxPython
# Created: 04/16/2012
#

#In addition to the above, karatekid552 has made suble changes to 
#layout in order to increase compatibility with G3HS, which this is
#is being integrated into. All credit should be directed to CChen.

#The changes that have been made are all commented as such with a date.

"""
Hex editor based on wxPython
"""
import os
import wx
import re
import sys
import ctypes
import binascii
import wx.grid as wxgrid
from wx.py import dispatcher
import wx.lib.agw.buttonpanel as btnpanel
import wx.lib.agw.genericmessagedialog as gmd

#3/8/14- Need this:
from binascii import hexlify, unhexlify
from GLOBALS import *

if sys.version_info[:2] < (2, 7):
    def bin(number):
        if number == 0:
            return ''
        else:
            return bin(number / 2) + str(number % 2)


class Enum(object):
    """ support class for enum
    """
    __names__ = None
    __items__ = None
    __special_names__ = []

    @classmethod
    def Name(cls, val):
        if cls.__names__ is None:
            cls.__names__ = dict([(getattr(cls, name), name) for name in dir(cls)
                                  if name and not name.startswith("_") and name not in cls.__special_names__ and
                                  not callable(getattr(cls, name))])

        return cls.__names__.get(val, val)

    @classmethod
    def Names(cls):
        return [name for name in dir(cls)
                if name and not name.startswith("_") and name not in cls.__special_names__ and
                not callable(getattr(cls, name))]

    @classmethod
    def Value(cls, name):
        items = cls.Items()
        if name not in items:
            raise AttributeError("No item '%s" % name)
        return items[name]

    @classmethod
    def Values(cls):
        return [getattr(cls, name) for name in dir(cls)
                if name and not name.startswith("_") and name not in cls.__special_names__ and
                not callable(getattr(cls, name))]

    @classmethod
    def Items(cls):
        if cls.__items__ is None:
            cls.__items__ = dict([(name, getattr(cls, name)) for name in dir(cls)
                                  if name and not name.startswith("_") and name not in cls.__special_names__ and
                                  not callable(getattr(cls, name))])
        return cls.__items__


class TransparentText(wx.StaticText):
    def __init__(self, parent, id=wx.ID_ANY, label='',
                 pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=wx.TRANSPARENT_WINDOW, name='transparenttext'):
        wx.StaticText.__init__(self, parent, id, label, pos, size, style, name)

        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda event: None)
        self.Bind(wx.EVT_SIZE, self.on_size)

    def on_paint(self, event):
        bdc = wx.PaintDC(self)
        dc = wx.GCDC(bdc)

        font_face = self.GetFont()
        font_color = self.GetForegroundColour()

        dc.SetFont(font_face)
        dc.SetTextForeground(font_color)
        dc.DrawText(self.GetLabel(), 0, 0)

    def on_size(self, event):
        self.Refresh()
        event.Skip()


#---------------------------------------------------------------------------
class VALID_TYPES(Enum):
    HEX_CHARS = "0123456789ABCDEFabcdef"
    DEC_CHARS = "0123456789"
    BIN_CHARS = "01"


class NumberValidator(wx.PyValidator):
    def __init__(self, allow_chars):
        wx.PyValidator.__init__(self)
        self.allow_chars = allow_chars
        self.Bind(wx.EVT_CHAR, self.OnChar)

    def Clone(self):
        return NumberValidator(self.allow_chars)

    def Validate(self, win):
        val = win.GetValue()
        for char in val:
            if char not in self.allow_chars:
                return False
        return True

    def OnChar(self, event):
        key = event.GetKeyCode()

        if key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > 255:
            event.Skip()
            return

        if chr(key) in self.allow_chars:
            event.Skip()

        return


class HexCellEditor(wxgrid.PyGridCellEditor):
    """
    This is a sample GridCellEditor that shows you how to make your own custom
    grid editors.  All the methods that can be overridden are shown here.  The
    ones that must be overridden are marked with "*Must Override*" in the
    docstring.
    """
    def __init__(self, max_length=2):
        wxgrid.PyGridCellEditor.__init__(self)
        self.max_length = 2

    def get_max_length(self):
        return self.max_length

    def set_max_length(self, max_length):
        self.max_length = max_length
        self._tc.SetMaxLength(self.max_length)

    MaxLength = property(get_max_length, set_max_length, doc="Set/Get max length")

    def Create(self, parent, id, evtHandler):
        """
        Called to create the control, which must derive from wx.Control.
        *Must Override*
        """
        self._tc = wx.TextCtrl(parent, id, "",
                               validator=NumberValidator(VALID_TYPES.HEX_CHARS),
                               style=wx.TE_PROCESS_ENTER)
        self._tc.SetInsertionPoint(0)
        self._tc.SetMaxLength(self.max_length)
        self.SetControl(self._tc)

        if evtHandler:
            self._tc.PushEventHandler(evtHandler)

    def SetSize(self, rect):
        """
        Called to position/size the edit control within the cell rectangle.
        If you don't fill the cell (the rect) then be sure to override
        PaintBackground and do something meaningful there.
        """
        self._tc.SetDimensions(rect.x, rect.y, rect.width + 2, rect.height + 2,
                               wx.SIZE_ALLOW_MINUS_ONE)

    def Show(self, show, attr):
        """
        Show or hide the edit control.  You can use the attr (if not None)
        to set colours or fonts for the control.
        """
        super(HexCellEditor, self).Show(show, attr)

    def PaintBackground(self, rect, attr):
        """
        Draws the part of the cell not occupied by the edit control.  The
        base  class version just fills it with background colour from the
        attribute.  In this class the edit control fills the whole cell so
        don't do anything at all in order to reduce flicker.
        """
        pass

    def BeginEdit(self, row, col, grid):
        """
        Fetch the value from the table and prepare the edit control
        to begin editing.  Set the focus to the edit control.
        *Must Override*
        """
        self.startValue = grid.GetTable().GetValue(row, col)
        self._tc.SetValue(self.startValue)
        self._tc.SetInsertionPointEnd()
        self._tc.SetFocus()

        # For this example, select the text
        self._tc.SetSelection(0, self._tc.GetLastPosition())

    def EndEdit(self, row, col, grid):
        """
        Complete the editing of the current cell. Returns True if the value
        has changed.  If necessary, the control may be destroyed.
        *Must Override*
        """
        changed = False

        val = self._tc.GetValue().strip()

        if val != self.startValue:
            try:
                hex_val = int(val, 16)
                changed = True
                dispatcher.send("HexCellEditor.Changed", sender=self, grid=grid,
                                row=row, col=col, val=val)
            except Exception,e:
                changed = False

        self.startValue = ''
        self._tc.SetValue('')
        return changed

    def Reset(self):
        """
        Reset the value in the control back to its starting value.
        *Must Override*
        """
        self._tc.SetValue(self.startValue)
        self._tc.SetInsertionPointEnd()

    def _is_hex_key(self, key):
        return key < 256 and chr(key) in VALID_TYPES.HEX_CHARS

    def IsAcceptedKey(self, evt):
        """
        Return True to allow the given key to start editing: the base class
        version only checks that the event has no modifiers.  F2 is special
        and will always start the editor.
        """
        return (not (evt.ControlDown() or evt.AltDown()) and
                evt.GetKeyCode() != wx.WXK_SHIFT) and self._is_hex_key(evt.GetKeyCode())

    def StartingKey(self, evt):
        """
        If the editor is enabled by pressing keys on the grid, this will be
        called to let the editor do something about that first key if desired.
        """
        key = evt.GetKeyCode()

        if self._is_hex_key(key):
            self._tc.SetValue(chr(key))
            self._tc.SetInsertionPointEnd()
        else:
            evt.Skip()

    def StartingClick(self):
        """
        If the editor is enabled by clicking on the cell, this method will be
        called to allow the editor to simulate the click on the control if
        needed.
        """
        pass

    def Destroy(self):
        """final cleanup"""
        super(HexCellEditor, self).Destroy()

    def Clone(self):
        """
        Create a new object which is the copy of this one
        *Must Override*
        """
        return HexCellEditor(self.max_length)


class SEARCH_TYPES(Enum):
    Hexadecimal = "Hexadecimal"
    NormalText = "Normal Text"
    RegexText = "Regex Text"


class HexGridTable(wx.grid.PyGridTableBase):
    class Actions:
        EditCell = "EditCell"
        RemoveCells = "RemoveCells"
        InsertCells = "InsertCells"

    def __init__(self, binary, length=None, hex_cols=16):
        wx.grid.PyGridTableBase.__init__(self)

        if length is None:
            self.length = len(binary)
        else:
            self.length = length
        if self.length < 0:
            self.length = 0

        self.hex_cols = hex_cols
        self.cols_labels = ["%X" % i for i in range(self.hex_cols)] + ["        Dump       "]

        self.buffer = ctypes.create_string_buffer(self.length)
        ctypes.memmove(self.buffer, binary, self.length)

        self._string = None

        self._dump_cell_attr = wxgrid.GridCellAttr()
        self._dump_cell_attr.SetReadOnly(True)
        self._dump_cell_attr.SetAlignment(wx.ALIGN_LEFT, wx.ALIGN_CENTER)

        self._alt_cell_attr = wxgrid.GridCellAttr()
        self._alt_cell_attr.SetBackgroundColour("#DDDDDD")
        self._page_row_attr = wxgrid.GridCellAttr()
        self._page_row_attr.SetBackgroundColour("#CCFDFD")
        self._range_attr = wxgrid.GridCellAttr()
        self._range_attr.SetBackgroundColour("#F2F5A9")
        self._changed_cell_attr = wxgrid.GridCellAttr()
        self._changed_cell_attr.SetBackgroundColour("#F2F5A9")
        self._changed_cell_attr.SetTextColour("red")

        self._changed_attr = {}

        self._changed_range = (-1, -1)
        self._undo_list = []
        self._redo_list = []

    @property
    def String(self):
        if self._string is None:
            self._string = ctypes.string_at(self.buffer, self.length)
        return self._string

    def _get_value_by_row_col(self, row, col, length=1):
        addr = row * self.hex_cols + col
        return self._get_value_by_addr(addr, length)

    def _get_value_by_addr(self, addr, length=1):
        end = addr + length
        if addr + length > self.length:
            end = self.length
        return self.buffer[addr:end]

    def _set_value_by_addr(self, addr, value):
        if addr > self.length:
            return False
        if addr == self.length:  # append one byte
            self.InsertRange(self.length, value)
        else:  # change one byte
            self.buffer[addr] = value
        self._string = None  # reset string
        return True

    def addr_to_row_col(self, addr):
        return addr / self.hex_cols, addr % self.hex_cols

    def row_col_to_addr(self, row, col):
        return row * self.hex_cols + col

    def _in_changed_range(self, addr):
        return self._changed_range[0] <= addr < self._changed_range[1]

    def Reset_Attr(self):
        self._changed_attr = {}

    def GetNumberCols(self):
        return self.hex_cols + 1

    def GetNumberRows(self):
        return (self.length + self.hex_cols) / self.hex_cols

    def GetColLabelValue(self, col):
        return self.cols_labels[col]

    def GetRowLabelValue(self, row):
        return "0x%X " % (row * self.hex_cols)

    def IsEmptyCell(self, row, col):
        addr = row * self.hex_cols + col
        if addr >= self.length:
            return True
        return False

    def GetAttr(self, row, col, kind=None):
        if col == self.hex_cols:  # disable cell editor for Dump col
            self._dump_cell_attr.IncRef()
            return self._dump_cell_attr
        addr = row * self.hex_cols + col

        if addr > self.length:  # disable cell editor for cells > length
            self._dump_cell_attr.IncRef()
            return self._dump_cell_attr

        if addr in self._changed_attr:  # return changed cells attr first
            attr = self._changed_attr[addr]
            if attr:
                attr.IncRef()
            return attr
        elif self._in_changed_range(addr):  # return range change attr
            self._range_attr.IncRef()
            return self._range_attr
        elif row and not (row % 0x20):   # return pager attr
            self._page_row_attr.IncRef()
            return self._page_row_attr
        elif col in [4, 5, 6, 7, 12, 13, 14, 15]:   # return range change attr
            self._alt_cell_attr.IncRef()
            return self._alt_cell_attr

        # return None for others

    def SetAttr(self, attr, row, col):
        addr = row * self.hex_cols + col
        if addr in self._changed_attr:   # decrease ref for saved attr
            old_attr = self._changed_attr[addr]
            if old_attr:
                old_attr.DecRef()
        self._changed_attr[addr] = attr  # save changed cell attr

    def GetValue(self, row, col):
        if col == self.hex_cols:  # dump col
            row_values = self._get_value_by_row_col(row, 0, 16)
            row_values = ["%c" % val if 0x20 <= ord(val) <= 0x7E else "." for val in row_values if val]
            return "  " + "".join(row_values)
        else:
            val = self._get_value_by_row_col(row, col, 1)
            return val and "%02X" % ord(val)

    def SetValue(self, row, col, value):
        if col == self.hex_cols:
            pass
        else:
            addr = row * self.hex_cols + col
            value = chr(int(value, 16))

            attr = self.GetAttr(row, col)
            saved_val = self._get_value_by_addr(addr)

            in_range = addr < self.length  # add undo for addr < length

            if saved_val != value and self._set_value_by_addr(addr, value):
                self._changed_cell_attr.IncRef()
                self.SetAttr(self._changed_cell_attr, row, col)
                if in_range:
                    self._add_undo_action(self.Actions.EditCell, (addr, saved_val, attr))
                else:
                    if col == self.hex_cols - 1:
                        # this is the last row/col, append a row
                        msg = wxgrid.GridTableMessage(self,
                                                      wxgrid.GRIDTABLE_NOTIFY_ROWS_APPENDED,
                                                      1)
                        self.GetView().ProcessTableMessage(msg)

    def SaveFile(self, output):
        """ output must be a file like object supports 'write' """
        output.write(ctypes.string_at(self.buffer, self.length))

    def GetBinary(self, start=0, length=None):
        if length is None:
            length = self.length
        if start + length > self.length:
            length = self.length - length
        return ctypes.string_at(ctypes.addressof(self.buffer) + start, length)

    def GetText(self, start=0, length=None):
        return binascii.b2a_hex(self.GetBinary(start, length)).upper()

    def InsertText(self, start, text):
        value = binascii.a2b_hex(text)
        self.InsertRange(start, value)

    def _delete_range(self, start, length):
        if start >= self.length:
            return ""
        self._changed_range = (-1, -1)

        deleted_data = ctypes.create_string_buffer(length)
        buf_addr = ctypes.addressof(self.buffer)
        if start + length > self.length:
            length = self.length - length
            ctypes.memmove(deleted_data, buf_addr + start, length)
            self.length -= length
        else:
            ctypes.memmove(deleted_data, buf_addr + start, length)
            ctypes.memmove(buf_addr + start, buf_addr + start + length, self.length - length - start)
            self.length -= length
            self.Reset_Attr()

        self._string = None  # reset string

        dispatcher.send("HexEditor.Changed", sender=self.GetView())

        return deleted_data

    def DeleteRange(self, start, length):
        deleted_data = self._delete_range(start, length)

        self._add_undo_action(self.Actions.RemoveCells, (start, length, deleted_data))

    def _insert_range(self, start, value):
        if start >= self.length:
            start = self.length

        length = len(value)
        new_buf = ctypes.create_string_buffer(self.length + length)
        new_buf_addr = ctypes.addressof(new_buf)

        old_addr = ctypes.addressof(self.buffer)

        self._changed_range = (start, start + length)

        ctypes.memmove(new_buf_addr, old_addr, start)  # copy range before insert point
        ctypes.memmove(new_buf_addr + start, value, length)  # copy insertion value
        # copy range after insert point
        ctypes.memmove(new_buf_addr + start + length, old_addr + start, self.length - start)

        self.buffer = new_buf
        self.length += length

        self.Reset_Attr()

        self._string = None  # reset string

        dispatcher.send("HexEditor.Changed", sender=self.GetView())

        return start

    def InsertRange(self, start, value):
        start = self._insert_range(start, value)

        self._add_undo_action(self.Actions.InsertCells, (start, value))

    def _add_undo_action(self, action, data):
        self._undo_list.append((action, data))
        if action == self.Actions.EditCell:
            return False
        return True

    def _add_redo_action(self, action, data):
        self._redo_list.append((action, data))
        if action == self.Actions.EditCell:
            return False
        return True

    def Undo(self):
        try:
            item = self._undo_list.pop()
            action, data = item
            action, data = self.Do(action, data)
            if action is False:
                return self._add_undo_action(*item)
            elif action is not None:
                return self._add_redo_action(action, data)
        except IndexError:
            return

    def Redo(self):
        try:
            item = self._redo_list.pop()
            action, data = item
            action, data = self.Do(action, data)
            if action is False:
                return self._add_redo_action(*item)
            if action is not None:
                return self._add_undo_action(action, data)
        except IndexError:
            return

    def Do(self, action, data):
        if action == self.Actions.EditCell:
            addr, value, attr = data
            row, col = self.addr_to_row_col(addr)
            saved_value = self._get_value_by_addr(addr)
            saved_attr = self.GetAttr(row, col)
            if self._set_value_by_addr(addr, value):
                self.SetAttr(attr, row, col)
                return  self.Actions.EditCell, (addr, saved_value, saved_attr)
            return False, False

        elif action == self.Actions.RemoveCells:
            start, length, deleted_data = data
            try:
                start = self._insert_range(start, deleted_data)
                return self.Actions.InsertCells, (start, deleted_data)
            except:
                return False, False

        elif action == self.Actions.InsertCells:
            start, deleted_data = data
            try:
                deleted_data = self._delete_range(start, len(deleted_data))
                return self.Actions.RemoveCells, (start, len(deleted_data), deleted_data)
            except:
                return False, False

        return None, None

    def FindIter(self, text, find_type=SEARCH_TYPES.Hexadecimal):
        """ return a iter """
        if find_type == SEARCH_TYPES.RegexText:
            regex = text
        elif find_type == SEARCH_TYPES.Hexadecimal:
            text = binascii.a2b_hex(text)
            regex = re.escape(text)
        elif find_type == SEARCH_TYPES.NormalText:
            regex = re.escape(text)
        else:
            raise Exception("unsupported search type")

        return self.FindRegex(regex)

    def FindRegex(self, regex):
        return re.finditer(regex, self.String)


class HexEditor(wx.Panel):

    def __init__(self, parent, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)
        self.table = None
        #3/6/14- Need to define self.OpenFile
        self.OpenFile = None
        self.__init_ctrls(parent)
        
        self.Binary = "\x00" * 0x100
        #3/6/14- The window itself is a droptarget.
        #self.SetDropTarget(BinFileDropTarget(self))

    def __init_ctrls(self, parent):
        #3/6/14- This font setup just doesn't work on Ubuntu.
        #self.SetFont(wx.Font(9, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Courier New"))

        sizer = wx.BoxSizer(wx.VERTICAL)

        self.toolbar = self.__init_toolbar()
        sizer.Add(self.toolbar, 0, wx.EXPAND)

        self.find_bar = self.__init_find_bar()
        sizer.Add(self.find_bar, 0, wx.EXPAND)

        self._grid_selecting_start = False
        self._in_selecting = False
        self.grid = wxgrid.Grid(self, -1)
        self._hex_cols = 16
        self._init_grid()
        self._reset_grid()
        sizer.Add(self.grid, 1, wx.EXPAND)

        self.status_bar = self.__init_status_bar()
        sizer.Add(self.status_bar, 0, wx.EXPAND)

        self.Bind(wx.EVT_SIZE, self.AutoSize)

        self.SetSizer(sizer)

    def __init_toolbar(self):
        toolbar = btnpanel.ButtonPanel(self, -1, "", btnpanel.BP_DEFAULT_STYLE)

        toolbar.AddControl(TransparentText(toolbar, -1, "Current Addr:", size=(-1, -1)))
        self._current_text = wx.TextCtrl(toolbar, -1,
                                         size=(80, 20),
                                         style=wx.TE_PROCESS_ENTER | wx.TE_RIGHT,
                                         validator=NumberValidator(VALID_TYPES.HEX_CHARS))
        self._current_text.Bind(wx.EVT_KEY_DOWN, self.OnCurrentKeyDown)
        toolbar.AddControl(self._current_text)

        toolbar.AddSeparator()
        #3/8/14- Modification to make this convert ASCII to hex, instead of the reverse.
        toolbar.AddControl(TransparentText(toolbar, -1, "Insert Character:", size=(-1, -1)))
        self._value_text = wx.TextCtrl(toolbar, -1,
                                      size=(40,20),
                                      style=wx.TE_PROCESS_ENTER | wx.TE_RIGHT)
        self._value_text.SetMaxLength(1)
        toolbar.AddControl(self._value_text)
        self._value_text.Bind(wx.EVT_CHAR, self.OnTextChar)
        #self._value_hex = wx.TextCtrl(toolbar, -1,
                                      #size=(30, 20),
                                      #style=wx.TE_PROCESS_ENTER | wx.TE_RIGHT,
                                      #validator=NumberValidator(VALID_TYPES.HEX_CHARS))
        #self._value_hex.SetMaxLength(2)
        #self._value_dec = wx.TextCtrl(toolbar, -1,
                                      #size=(40, 20),
                                      #style=wx.TE_PROCESS_ENTER | wx.TE_RIGHT,
                                      #validator=NumberValidator(VALID_TYPES.DEC_CHARS))
        #self._value_dec.SetMaxLength(3)
        #self._value_bin = wx.TextCtrl(toolbar, -1,
                                      #size=(80, 20),
                                      #style=wx.TE_PROCESS_ENTER | wx.TE_RIGHT,
                                      #validator=NumberValidator(VALID_TYPES.BIN_CHARS))
        #self._value_bin.SetMaxLength(8)
        self._value_chr = TransparentText(toolbar, -1, " ", size=(20, -1))
        #toolbar.AddControl(self._value_hex)
        #toolbar.AddControl(self._value_dec)
        #toolbar.AddControl(self._value_bin)
        #self._value_hex.Bind(wx.EVT_CHAR, self.OnValueTextChar)
        #self._value_dec.Bind(wx.EVT_CHAR, self.OnValueTextChar)
        #self._value_bin.Bind(wx.EVT_CHAR, self.OnValueTextChar)
        toolbar.AddControl(self._value_chr)

        toolbar.AddSeparator()
        #3/6/14- This is a cross platform tool and is integrated
        #into a larger program. Therefore, this menu has been removed
        #and replaced with a simple save button.
        #self.menu = self._init_grid_menu(True)
        #btn_menu = wx.Button(toolbar, label=u"\u25BC", size=(20, 20))
        #toolbar.Bind(wx.EVT_BUTTON, self.OnMenuButton, id=btn_menu.GetId())
        #toolbar.AddControl(btn_menu)
        save = wx.Button(toolbar, label="Save")
        toolbar.Bind(wx.EVT_BUTTON, self.SaveFile, id=save.GetId())
        toolbar.AddControl(save)
        toolbar.DoLayout()
        return toolbar  
    
    def __init_find_bar(self):
        find_bar = btnpanel.ButtonPanel(self, -1, "", btnpanel.BP_DEFAULT_STYLE)

        find_bar.AddControl(TransparentText(find_bar, -1, "Search:", size=(-1, -1)))
        self._find_text = wx.TextCtrl(find_bar, -1,
                                      size=(220, 20),
                                      style=wx.TE_PROCESS_ENTER)
        self._find_text.Bind(wx.EVT_KEY_DOWN, self.OnFindKeyDown)
        find_bar.AddControl(self._find_text)

        btn_find = wx.Button(find_bar, label="Find", size=(40, 22))
        find_bar.Bind(wx.EVT_BUTTON, self.OnFindButton, id=btn_find.GetId())
        find_bar.AddControl(btn_find)

        self.find_types = []
        for find_type in SEARCH_TYPES.Values():
            radio = wx.RadioButton(find_bar, -1, find_type)
            find_bar.AddControl(radio)
            self.find_types.append(radio)
        self.find_types[0].SetValue(True)

        self._search_options = {}
        self._search_result = None

        find_bar.DoLayout()
        return find_bar

    def _init_grid(self):
        self.grid.CreateGrid(0, 0)
        self.grid.SetDefaultCellAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
        self.grid.SetRowLabelAlignment(wx.ALIGN_RIGHT, wx.ALIGN_CENTER)
        self.grid.SetDefaultColSize(26)
        #3/7/14- They don't need to be disabled.
        #self.grid.DisableDragColSize()
        #self.grid.DisableDragRowSize()
        #self.grid.SetLabelBackgroundColour("#E2E8F0")

        corner = self.grid.GetGridCornerLabelWindow()
        addr = wx.StaticText(corner, label="Address", pos=(20, 12))
        corner.Bind(wx.EVT_LEFT_DOWN, lambda e: self.SetSelection(0, self.Length, False))
        addr.Bind(wx.EVT_LEFT_DOWN, lambda e: self.SetSelection(0, self.Length, False))

        cell_editor = HexCellEditor(2)
        self.grid.SetDefaultEditor(cell_editor)
        dispatcher.connect(self.OnCellChanged, signal="HexCellEditor.Changed", sender=cell_editor)

        self._grid_menu = self._init_grid_menu(False)

        self.grid.Bind(wx.EVT_KEY_DOWN, self.OnGridKeyDown)
        self.grid.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.OnSelectCell)
        self.grid.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.OnCellRightClicked)
        self.grid.Bind(wx.grid.EVT_GRID_LABEL_RIGHT_CLICK, self.OnCellRightClicked)

        self.grid.GetGridColLabelWindow().Bind(wx.EVT_LEFT_DOWN, self.OnGridColLeftDown)
        self.grid.GetGridWindow().Bind(wx.EVT_LEFT_DOWN, self.OnGridLeftDown)
        self.grid.GetGridWindow().Bind(wx.EVT_LEFT_UP, self.OnGridLeftUp)
        self.grid.GetGridWindow().Bind(wx.EVT_MOTION, self.OnGridLeftMotion)
        self.grid.GetGridRowLabelWindow().Bind(wx.EVT_MOTION, self.OnGridLeftMotion)
        self.grid.GetGridRowLabelWindow().Bind(wx.EVT_LEFT_UP, self.OnGridRowLeftUp)

    def _reset_grid(self):
        self.grid.ClearGrid()
        self._reset_grid_selecting()
    
    def OnTextChar(self, event):
        key = event.GetKeyCode()
        if key in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            text_ctrl = event.EventObject
            val = text_ctrl.GetValue()
            if val and val.strip():
                try: char = hexlify(val)
                except: return
                self._value_chr.SetLabel(char.upper().zfill(2) + " ")
                #self._set_value_text(val)
                row, col = self.CurrentRowCol
                self.SetCellString(row, col, char)

            text_ctrl.SetInsertionPointEnd()
            text_ctrl.SetSelection(0, -1)

        event.Skip()
    
    def AutoSize(self, event=None):
        size = self.GetSize()
        sb_width = wx.SystemSettings.GetMetric(wx.SYS_VSCROLL_X)
        col_size = (size[0] - 150 - sb_width - self.grid.GetRowLabelSize()) / self.HexCols
        if col_size < -1:
            col_size = -1
        for col in xrange(self.grid.GetNumberCols() - 1):
            self.grid.SetColSize(col, col_size)
        self.grid.SetColSize(self.grid.GetNumberCols() - 1, 160)
        self.grid.Refresh()
        event and event.Skip()

    def _init_grid_menu(self, main_menu=False):
        menu = wx.Menu()
        if main_menu:
            items = [
                ("New", lambda e: self.NewDialog()),
                ("Load", lambda e: self.OpenFileDialog()),
                ("Save", lambda e: self.SaveFileDialog()),
                ("Calculator", lambda e: os.startfile("calc.exe")),
            ]
        else:
            items = [
                ("Cut", lambda e: self._cut()),
                ("Copy", lambda e: self._copy()),
                ("Paste", lambda e: self._paste()),
                ("Insert", lambda e: self._insert()),
                "-",
                ("Undo", lambda e: self.Undo()),
                ("Redo", lambda e: self.Redo()),
                "-",
                ("Delete", lambda e: self._delete()),
                ("Select All", lambda e: self.SetSelection(0, self.Length, False)),
            ]
        for item in items:
            if item == "-":
                menu.AppendSeparator()
            else:
                name, func = item
                menu_id = wx.NewId()
                menu.Append(menu_id, name)
                self.Bind(wx.EVT_MENU, func, id=menu_id)

        return menu

    def __init_status_bar(self):
        sb = wx.StatusBar(self)
        sb.SetFieldsCount(4)
        sb.SetStatusWidths([-2, -1, -1, -1])
        return sb

    #3/8/14- Need to the hex, dec, and bin....
    def _clear_value_text(self):
        self._current_text.SetLabel("")
        #self._value_hex.SetLabel("")
        #self._value_dec.SetLabel("")
        #self._value_bin.SetLabel("")
        self._value_chr.SetLabel(" ")
        self._value_text.SetValue("")
        
    def _set_value_text(self, value):
        #self._value_hex.SetLabel(hex(value).replace("0x", "").upper().zfill(2))
        #self._value_dec.SetLabel(str(value))
        #self._value_bin.SetLabel(bin(value).replace("0b", "").zfill(8))
        if 0x20 <= value <= 0x7E:
            self._value_text.SetValue(chr(value))
            self._value_chr.SetLabel(hex(value).replace("0x", "").upper().zfill(2))
        else:
            self._value_text.SetValue("")
            self._value_chr.SetLabel(" ")
        #if 0x20 <= value <= 0x7E:
            #self._value_chr.SetLabel(chr(value) + " ")
        #else:
            #self._value_chr.SetLabel(" ")

    def _update_status(self, length=None, row=None, col=None, sel=None):
        if length is not None:
            self.status_bar.SetStatusText("Length: 0x%X(%d)" % (length, length), 0)
        if row is not None:
            self.status_bar.SetStatusText("Row: %s" % row, 1)
        if col is not None:
            self.status_bar.SetStatusText("Col: %s" % col, 2)
        if sel is not None:
            self.status_bar.SetStatusText("Selected: %s" % sel, 3)

    @property
    def HexCols(self):
        return self._hex_cols

    def GetBinary(self):
        return self.grid.GetTable().String

    def SetBinary(self, binary):
        self.SetBinary(binary)

    Binary = property(GetBinary, SetBinary, doc="Set/Get Binary String")

    @property
    def Length(self):
        return self.grid.GetTable().length

    def _set_grid_table(self, table):
        self.table = table
        self.grid.BeginBatch()
        self._reset_grid()
        self.grid.SetTable(table)
        self.AutoSize()
        self.grid.EndBatch()

        self._update_status(length=table.length)
        self.toolbar.DoLayout()

    def GetCurrentAddr(self):
        row, col = self.grid.GridCursorRow, self.grid.GridCursorCol
        addr = row * self.HexCols + col
        return addr

    def SetCurrentAddr(self, addr):
        if addr < self.Length:
            row, col = self.AddrToRowCol(addr)
            self.grid.SetGridCursor(row, col)
            self.SetSelection(addr, 1, False)
            self.JumpTo(row, col)
            self.grid.SetFocus()

    CurrentAddr = property(GetCurrentAddr, SetCurrentAddr, doc="Set/Get Current Address")

    def GetCurrentRowCol(self):
        return self.grid.GridCursorRow, self.grid.GridCursorCol

    def SetCurrentRowCol(self, position):
        row, col = position
        self.grid.SetGridCursor(row, col)

    CurrentRowCol = property(GetCurrentRowCol, SetCurrentRowCol, doc="Set/Get Current Row and Col")

    @property
    def Selection(self):
        cells = self.grid.GetSelectedCells()
        top_left = self.grid.GetSelectionBlockTopLeft()
        bottom_right = self.grid.GetSelectionBlockBottomRight()

        addrs = [self.RowColToAddr(row, col) for (row, col) in top_left + bottom_right + cells]
        if addrs:
            min_addr = min(addrs)
            max_addr = max(addrs)
            return min_addr, max_addr - min_addr + 1

    def SetBinary(self, binary, length=None):
        """
        bytes string
        """
        if not isinstance(binary, basestring):
            raise Exception("binary must be string")

        if self.table:
            wx.CallAfter(self.table.Destroy)
        table = HexGridTable(binary, length)
        self._set_grid_table(table)

    def SetBinaryFile(self, path, length=-1):
        """ filename
        """
        bin_file = open(path, "rb")
        binary = bin_file.read(length)
        bin_file.close()
        self.SetBinary(binary, length=length)

    def _file_dialog(self, *args, **kwargs):
        wildcard = 'Binary files (*.bin;*.txt)|*.bin;*.txt|All files (*.*)|*.*'
        kwargs.update({
            "wildcard": wildcard
        })
        dlg = wx.FileDialog(self, *args, **kwargs)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            dlg.Destroy()
            return filename
        dlg.Destroy()

    def MessageBox(self, message, title="", style=wx.OK | wx.ICON_INFORMATION):
        dlg = gmd.GenericMessageDialog(self, message, title, style)
        res = dlg.ShowModal()
        dlg.Destroy()
        return res

    def NewDialog(self):
        dlg = wx.TextEntryDialog(self, "Size in bytes", "New Binary", str(256))
        res = dlg.ShowModal()
        dlg.Destroy()
        if res == wx.ID_OK:
            size = dlg.GetValue()
            size = int(size)
            self.Binary = '\x00' * size
            self.grid.SetFocus()

    def OpenFileDialog(self):
        filename = self._file_dialog("Load a file", style=wx.OPEN)
        if filename:
            self.LoadFile(filename)

    def SaveFileDialog(self):
        filename = self._file_dialog("Save to file", style=wx.SAVE,
                                     defaultFile="backup.bin")
        if filename:
            if os.path.isfile(filename):
                res = self.MessageBox("A file with the name '%s' already exists, "
                                      "do you want to replace it?" % os.path.basename(filename),
                                      "File Replace", wx.YES_NO | wx.ICON_WARNING)
                if res == wx.ID_NO:
                    return
            self.SaveFile(filename)

    def LoadFile(self, filename):
        self.OpenFile = filename
        if os.path.isfile(filename):
            self.SetBinaryFile(filename, os.path.getsize(filename))
        else:
            self.MessageBox("Can not open file %s" % filename, "Load File Error", wx.OK | wx.ICON_ERROR)
        self.grid.SetFocus()
    
    #3/6/14- Modified savefile function to work with the new button.
    def SaveFile(self, event): #filename):
        if self.OpenFile:
            #f = open(filename, "wb")
            f = open(self.OpenFile, "wb")
            self.grid.GetTable().SaveFile(f)
            f.close()
            self.SetBinaryFile(self.OpenFile, os.path.getsize(self.OpenFile))
            self.GetParent().PokeDataTab.tabbed_area.reload_tab_data() #Reload stuffs.:P
            #self.GetParent().PokeDataTab.tabbed_area.egg_moves.load()
            #self.GetParent().PokeDataTab.tabbed_area.reload_tab_data()
        else: return

    def GetCellString(self, row, col, length=1):
        val = ""
        if row < self.grid.GetNumberRows() and col < self.HexCols:
            val = self.grid.GetCellValue(row, col)
        return val

    def SetCellString(self, row, col, val):
        """ val must be Hex string
        """
        val = int(val, 16)
        # update the table
        addr = self.RowColToAddr(row, col)

        self.grid.SetCellValue(row, col, "%02X" % val)

    def AddrToRowCol(self, addr):
        return addr / self.HexCols, addr % self.HexCols

    def RowColToAddr(self, row, col, check_max=True):
        col = self.HexCols - 1 if col >= self.HexCols else col
        addr = row * self.HexCols + col
        if check_max:
            addr = self._check_addr_in_range(addr)
        return addr

    def SetSelection(self, addr, length=1, jumpto=False):
        row, col = self.AddrToRowCol(addr)
        end_row, end_col = self.AddrToRowCol(addr + length - 1)

        self.grid.Freeze()
        self.grid.BeginBatch()
        self.grid.SetGridCursor(row, col)
        if length > 0:
            # in same row
            if row == end_row:
                self.grid.SelectBlock(row, col, end_row, end_col)
            elif end_row > row:
                #first row
                self.grid.SelectBlock(row, col, row, self.HexCols - 1)
                if end_row - row > 1:
                    self.grid.SelectBlock(row + 1, 0, end_row - 1, self.HexCols - 1, addToSelected=True)
                #last row
                self.grid.SelectBlock(end_row, 0, end_row, end_col, addToSelected=True)
        self.grid.EndBatch()
        self.grid.Thaw()
        self._update_status(sel=length)
        if jumpto:
            self.JumpTo(row, col)

    def GetSelection(self):
        return self.Selection

    def OnMenuButton(self, event):
        self.PopupMenu(self.menu)
        event.Skip()

    def OnFindButton(self, event):
        event.Skip()
        text = self._find_text.GetValue()
        if not text:
            self._search_result = None
            return

        options = {
            "text": text,
            "search_type": "",
        }

        for radio in self.find_types:
            if radio.GetValue() is True:
                options["search_type"] = radio.GetLabel()

        if self._search_options.get("text") != options["text"] or\
            self._search_options.get("search_type") != options["search_type"] or\
                self._search_result is None:
                    # search options change, re-search
                    if options["search_type"] == SEARCH_TYPES.Hexadecimal:
                        text = re.sub(r'\s+', '', text)

                    try:
                        self._search_result = self.grid.GetTable().FindIter(text, options["search_type"])
                        self._search_options = options
                    except Exception, e:
                        self.MessageBox("Error: %s" % str(e), "Search Error", wx.OK | wx.ICON_ERROR)
                        return

        try:
            match = self._search_result.next()
            start, end = match.span(0)
            self.SetSelection(start, end - start, True)
            self.grid.SetFocus()
        except StopIteration, e:
            self._search_result = None  # restart
            self.MessageBox("Search to End", "Search Done")
        except Exception, e:
            self.MessageBox("Error: %s" % str(e), "Search Error", wx.OK | wx.ICON_ERROR)

    def OnFindKeyDown(self, event):
        if event.GetKeyCode() in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            self.OnFindButton(event)
            self._find_text.SetFocus()
            return
        event.Skip()

    def OnSelectCell(self, event):
        row = event.GetRow()
        col = event.GetCol()

        addr = self.RowColToAddr(row, col)

        value = self.GetCellString(row, col)
        self._clear_value_text()
        if value:
            value = int(value, 16)
            self._set_value_text(value)
            self._current_text.SetLabel("%X" % addr)

        self._update_status(row=row, col=col)
        event.Skip()

    def OnCellRightClicked(self, event):
        self.grid.PopupMenu(self._grid_menu)
        event.Skip()

    def OnCellChanged(self, signal, grid, row, col, val):
        if grid == self.grid:
            self.SetCellString(row, col, val)
            dispatcher.send("HexEditor.Changed", sender=self, row=row, col=col, val=val)

    def OnCurrentKeyDown(self, event):
        event.Skip()
        if event.GetKeyCode() in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            addr = int(self._current_text.GetValue(), 16)
            self.CurrentAddr = addr

    def OnGridKeyDown(self, event):
        key = event.GetKeyCode()
        controlDown = event.ControlDown()
        altDown = event.AltDown()
        if controlDown and altDown:
            event.Skip()

        if controlDown and key in (ord('A'), ord('a')):
            self.SetSelection(0, self.Length, False)
        elif controlDown and key in (ord('Z'), ord('z')):
            self.Undo()
        elif controlDown and key in (ord('Y'), ord('y')):
            self.Redo()
        elif controlDown and key in (ord('C'), ord('c')):
            self._copy()
        elif controlDown and key in (ord('X'), ord('x')):
            self._cut()
        elif controlDown and key in (ord('V'), ord('v')):
            self._paste()
        elif controlDown and key in (ord('S'), ord('s')):
            self.SaveFileDialog()
        elif controlDown and key in (ord('O'), ord('o'), ord('L'), ord('l')):
            self.OpenFileDialog()
        elif controlDown and key in (ord('N'), ord('n')):
            self.NewDialog()
        elif controlDown and key in (ord('F'), ord('f')):
            selection = self.Selection
            if selection:
                start, length = selection
                value = self.grid.GetTable().GetText(start, length)
                self._find_text.SetValue(value)
                self._find_text.SetFocus()
                self._find_text.SelectAll()
        elif key in (wx.WXK_F3,):
            self.OnFindButton(event)
            self.grid.SetFocus()
        elif key in (wx.WXK_DELETE,):
            self._delete()
        elif key in (wx.WXK_INSERT,):
            self._insert()
        elif key in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER, wx.WXK_TAB):
            row, col = self.CurrentRowCol
            if col >= self.HexCols - 1:
                self.CurrentRowCol = (row + 1, 0)
            else:
                event.m_keyCode = wx.WXK_TAB
                event.Skip()
        else:
            event.Skip()

    def _check_addr_in_range(self, addr):
        addr = addr if addr > 0 else 0
        addr = addr if addr < self.Length else self.Length - 1
        return addr

    def _set_selection(self, end_pos=None, callback=None):
        self._in_selecting = True
        if end_pos and self._grid_selecting_start:
            cur_row, cur_col = self._grid_selecting_start
            end_row, end_col = end_pos

            if cur_col == self.HexCols:
                if cur_row > end_row:
                    cur_row, end_row = end_row, cur_row
                min_addr = self.RowColToAddr(cur_row, 0)
                max_addr = self.RowColToAddr(end_row, self.HexCols - 1)
                self.SetSelection(min_addr, max_addr - min_addr + 1, False)
            else:
                if end_col == self.HexCols:
                    end_col -= 1
                if (cur_row, cur_col) == (end_row, end_col):
                    min_addr = max_addr = self.RowColToAddr(cur_row, cur_col, False)
                    if min_addr > self.Length:
                        min_addr = max_addr = self.Length
                else:
                    min_addr = self.RowColToAddr(cur_row, cur_col)
                    max_addr = self.RowColToAddr(end_row, end_col)
                    if min_addr > max_addr:
                        min_addr, max_addr = max_addr, min_addr

                self.SetSelection(min_addr, max_addr - min_addr + 1, False)
        else:
            rows = self.grid.GetSelectedRows()
            if rows:
                min_row = min(rows)
                max_row = max(rows)
                self.grid.SetGridCursor(min_row, 0)
                self.grid.ClearSelection()
                min_addr = self.RowColToAddr(min_row, 0)
                max_addr = self.RowColToAddr(max_row, self.HexCols - 1)
                self.SetSelection(min_addr, max_addr - min_addr + 1, False)
            else:
                top_left = self.grid.GetSelectionBlockTopLeft()
                bottom_right = self.grid.GetSelectionBlockBottomRight()
                cells = self.grid.GetSelectedCells()

                addrs = [self.RowColToAddr(row, col) for (row, col) in top_left + bottom_right + cells]
                if addrs:
                    min_addr = min(addrs)
                    max_addr = max(addrs)
                    self.SetSelection(min_addr, max_addr - min_addr + 1, False)
                else:
                    self._update_status(sel=1)

        self._in_selecting = False
        if callable(callback):
            callback()
        #self.grid.Refresh()

    def _reset_grid_selecting(self):
        self._grid_selecting_start = None

    def _client_to_scroll_pos(self, x, y):
        ppunit = self.grid.GetScrollPixelsPerUnit()
        scroll_x = self.grid.GetScrollPos(wx.HORIZONTAL)
        scroll_y = self.grid.GetScrollPos(wx.VERTICAL)
        x += scroll_x * ppunit[0]
        y += scroll_y * ppunit[1]
        return x, y

    def OnGridColLeftDown(self, event):
        # disable col selection
        pass

    def OnGridLeftDown(self, event):
        start_pos = self._client_to_scroll_pos(event.X, event.Y)
        self._grid_selecting_start = self.grid.XYToCell(*start_pos)
        event.Skip()

    def OnGridLeftUp(self, event):
        event.Skip()
        wx.CallAfter(self._set_selection, callback=self._reset_grid_selecting)

    def OnGridLeftMotion(self, event):
        if not self._in_selecting and self._grid_selecting_start:
            end_pos = self._client_to_scroll_pos(event.X, event.Y)
            end_pos = self.grid.XYToCell(*end_pos)
            if end_pos != (-1, -1):
                wx.CallAfter(self._set_selection, end_pos=end_pos)

    def OnGridRowLeftUp(self, event):
        event.Skip()
        wx.CallAfter(self._set_selection, callback=self._reset_grid_selecting)

    def OnValueTextChar(self, event):
        key = event.GetKeyCode()
        if key in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            text_ctrl = event.EventObject
            val = text_ctrl.GetValue()
            if val and val.strip():
                if text_ctrl == self._value_hex:
                    val = int(val, 16)
                elif text_ctrl == self._value_dec:
                    val = int(val, 10)
                    if val > 0xFF:
                        return
                elif text_ctrl == self._value_bin:
                    val = int(val, 2)
                else:
                    raise Exception("unknown text ctrl")

                self._set_value_text(val)
                row, col = self.CurrentRowCol
                self.SetCellString(row, col, hex(val))

            text_ctrl.SetInsertionPointEnd()
            text_ctrl.SetSelection(0, -1)

        event.Skip()
        
    def OnValueTextChar(self, event):
        key = event.GetKeyCode()
        if key in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            text_ctrl = event.EventObject
            val = text_ctrl.GetValue()
            if val and val.strip():
                if text_ctrl == self._value_hex:
                    val = int(val, 16)
                elif text_ctrl == self._value_dec:
                    val = int(val, 10)
                    if val > 0xFF:
                        return
                elif text_ctrl == self._value_bin:
                    val = int(val, 2)
                else:
                    raise Exception("unknown text ctrl")

                self._set_value_text(val)
                row, col = self.CurrentRowCol
                self.SetCellString(row, col, hex(val))

            text_ctrl.SetInsertionPointEnd()
            text_ctrl.SetSelection(0, -1)

        event.Skip()

    def JumpTo(self, row, col):
        ppunit = self.grid.GetScrollPixelsPerUnit()
        cell_coords = self.grid.CellToRect(row, col)
        y = cell_coords.y / ppunit[1]  # convert pixels to scroll units
        scrollPageSize = self.grid.GetScrollPageSize(wx.VERTICAL)
        scroll_coords = (0, y - scrollPageSize / 2)
        self.grid.Scroll(*scroll_coords)

    def _get_data_from_clipboard(self):
        data = wx.TextDataObject()
        wx.TheClipboard.Open()
        success = wx.TheClipboard.GetData(data)
        wx.TheClipboard.Close()
        return data.GetText() if success else None

    def _cut(self):
        self._copy()
        self._delete()

    def _copy(self):
        selection = self.Selection
        if selection:
            start, length = selection
            self.SetSelection(start, length)
        else:
            start = self.CurrentAddr
            length = 1

        binary = self.grid.GetTable().GetText(start, length)
        wx.TheClipboard.Open()
        wx.TheClipboard.SetData(wx.TextDataObject(binary))
        wx.TheClipboard.Close()

    def _paste(self):
        self._delete(False)
        self._insert()

    def _delete(self, delete_cell=True):
        selection = self.Selection
        if selection:
            start, length = selection
            self.SetSelection(start, length)
        else:
            if not delete_cell:
                return
            start = self.CurrentAddr
            length = 1

        table = self.grid.GetTable()
        table.DeleteRange(start, length)
        self._set_grid_table(table)

    def _insert(self):
        data = self._get_data_from_clipboard()
        if data:
            start = self.CurrentAddr

            table = self.grid.GetTable()
            data = re.sub("[\n\r]\S{8} ", "", data)
            data = re.sub(r'\s+', '', data)
            if data:
                if len(data) % 2:
                    data = data[:-1]
                try:
                    table.InsertText(start, data)
                    self._set_grid_table(table)
                except Exception, e:
                    self.MessageBox(str(e), "Insert Data Error", wx.OK | wx.ICON_ERROR)

    def Undo(self):
        table = self.grid.GetTable()
        res = table.Undo()
        if res is True:
            self._set_grid_table(table)
        elif res is False:
            self.Refresh()

    def Redo(self):
        table = self.grid.GetTable()
        res = table.Redo()
        if res is True:
            self._set_grid_table(table)
        elif res is False:
            self.Refresh()


class BinFileDropTarget(wx.FileDropTarget):
    def __init__(self, editor):
        wx.FileDropTarget.__init__(self)
        self.editor = editor

    def OnDropFiles(self, x, y, filenames):
        filenames = [path for path in filenames if os.path.isfile(path)]
        self.editor.LoadFile(filenames[0])



if __name__ == '__main__':
    from wx.lib.embeddedimage import PyEmbeddedImage
    hex_icon = PyEmbeddedImage(
        "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"
        "KfRxzQAAAABJRU5ErkJggg==")

    class HexEditorFrame(wx.Frame):
        def __init__(self, parent):
            wx.Frame.__init__(self, id=-1, name='', parent=parent, title="HexEditor", size=(720, 700))
            sizer = wx.BoxSizer(wx.VERTICAL)

            self.editor = HexEditor(self)

            sizer.Add(self.editor, 1, wx.EXPAND)
            self.SetSizer(sizer)

            self.SetIcon(hex_icon.Icon)
            self.CenterOnScreen()

        def OpenFile(self, filename):
            self.editor.LoadFile(filename)

    class HexEditorApp(wx.App):
        def OnInit(self):
            self.mainFrame = HexEditorFrame(None)
            self.mainFrame.Show()
            self.SetTopWindow(self.mainFrame)
            return True

        def OpenFile(self, filename=''):
            if filename:
                self.mainFrame.OpenFile(filename)

    def main(*args):
        application = HexEditorApp(None)
        if len(args[0]) > 1 and os.path.isfile(args[0][1]):
            application.OpenFile(filename=args[0][1])
        application.MainLoop()

    import sys
    main(sys.argv)
