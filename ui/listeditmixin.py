#----------------------------------------------------------------------------
# Name:        wx.lib.mixins.listctrl
# Purpose:     Helpful mix-in classes for wxListCtrl
#
# Author:      Robin Dunn
#
# Created:     15-May-2001
# Copyright:   (c) 2001-2017 by Total Control Software
# Licence:     wxWindows license
# Tags:        phoenix-port, py3-port
#----------------------------------------------------------------------------
# 12/14/2003 - Jeff Grimmett (grimmtooth@softhome.net)
#
# o 2.5 compatibility update.
# o ListCtrlSelectionManagerMix untested.
#
# 12/21/2003 - Jeff Grimmett (grimmtooth@softhome.net)
#
# o wxColumnSorterMixin -> ColumnSorterMixin
# o wxListCtrlAutoWidthMixin -> ListCtrlAutoWidthMixin
# ...
# 13/10/2004 - Pim Van Heuven (pim@think-wize.com)
# o wxTextEditMixin: Support Horizontal scrolling when TAB is pressed on long
#       ListCtrls, support for WXK_DOWN, WXK_UP, performance improvements on
#       very long ListCtrls, Support for virtual ListCtrls
#
# 15-Oct-2004 - Robin Dunn
# o wxTextEditMixin: Added Shift-TAB support
#
# 2008-11-19 - raf <raf@raf.org>
# o ColumnSorterMixin: Added GetSortState()
#
# 2017-09-14 - Luke Montalvo <lukemontalvo@gmail.com>
# o wxTextEditMixin: Fixes for Python3 and basic Validator support

try:
	import wx
except ImportError:
	raise ImportError("The wxPython module is required to run this program")

from bisect import bisect

class TextEditMixin:
	"""
	A mixin class that enables any text in any column of a
	multi-column listctrl to be edited by clicking on the given row
	and column.  You close the text editor by hitting the ENTER key or
	clicking somewhere else on the listctrl. You switch to the next
	column by hiting TAB.

	To use the mixin you have to include it in the class definition
	and call the __init__ function::

		class TestListCtrl(wx.ListCtrl, TextEditMixin):
			def __init__(self, parent, ID, pos=wx.DefaultPosition,
						 size=wx.DefaultSize, style=0):
				wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
				TextEditMixin.__init__(self)


	Authors:     Steve Zatz, Pim Van Heuven (pim@think-wize.com)
	"""

	editorBgColour = wx.Colour(255,255,175) # Yellow
	editorFgColour = wx.Colour(0,0,0)       # black

	def __init__(self):
		#editor = wx.TextCtrl(self, -1, pos=(-1,-1), size=(-1,-1),
		#                     style=wx.TE_PROCESS_ENTER|wx.TE_PROCESS_TAB \
		#                     |wx.TE_RICH2)

		self.make_editor()
		self.Bind(wx.EVT_TEXT_ENTER, self.CloseEditor)
		self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
		self.Bind(wx.EVT_LEFT_DCLICK, self.OnLeftDown)
		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected, self)


	def make_editor(self, col_style=wx.LIST_FORMAT_LEFT):

		style =wx.TE_PROCESS_ENTER|wx.TE_PROCESS_TAB|wx.TE_RICH2
		style |= {wx.LIST_FORMAT_LEFT: wx.TE_LEFT,
				  wx.LIST_FORMAT_RIGHT: wx.TE_RIGHT,
				  wx.LIST_FORMAT_CENTRE : wx.TE_CENTRE
				  }[col_style]

		editor = wx.TextCtrl(self, -1, style=style)
		editor.SetBackgroundColour(self.editorBgColour)
		editor.SetForegroundColour(self.editorFgColour)
		font = self.GetFont()
		editor.SetFont(font)

		self.curRow = 0
		self.curCol = 0

		editor.Hide()
		if hasattr(self, 'editor'):
			self.editor.Destroy()
		self.editor = editor

		self.col_style = col_style
		self.editor.Bind(wx.EVT_CHAR, self.OnChar)
		self.editor.Bind(wx.EVT_KILL_FOCUS, self.CloseEditor)


	def OnItemSelected(self, evt):
		self.curRow = evt.GetIndex()
		evt.Skip()


	def OnChar(self, event):
		''' Catch the TAB, Shift-TAB, cursor DOWN/UP key code
			so we can open the editor at the next column (if any).'''

		keycode = event.GetKeyCode()
		if keycode == wx.WXK_TAB and event.ShiftDown():
			self.CloseEditor()
			if self.curCol-1 >= 0:
				self.OpenEditor(self.curCol-1, self.curRow)

		elif keycode == wx.WXK_TAB:
			self.CloseEditor()
			if self.curCol+1 < self.GetColumnCount():
				self.OpenEditor(self.curCol+1, self.curRow)

		elif keycode == wx.WXK_ESCAPE:
			self.CloseEditor()

		elif keycode == wx.WXK_DOWN:
			self.CloseEditor()
			if self.curRow+1 < self.GetItemCount():
				self._SelectIndex(self.curRow+1)
				self.OpenEditor(self.curCol, self.curRow)

		elif keycode == wx.WXK_UP:
			self.CloseEditor()
			if self.curRow > 0:
				self._SelectIndex(self.curRow-1)
				self.OpenEditor(self.curCol, self.curRow)

		elif keycode == wx.WXK_NUMPAD_ENTER:
			self.CloseEditor()

		else:
			event.Skip()


	def OnLeftDown(self, evt=None):
		''' Examine the click and double
		click events to see if a row has been click on twice. If so,
		determine the current row and columnn and open the editor.'''

		if self.editor.IsShown():
			self.CloseEditor()

		x,y = evt.GetPosition()
		row,flags = self.HitTest((x,y))

		if row != self.curRow: # self.curRow keeps track of the current row
			evt.Skip()
			return

		# the following should really be done in the mixin's init but
		# the wx.ListCtrl demo creates the columns after creating the
		# ListCtrl (generally not a good idea) on the other hand,
		# doing this here handles adjustable column widths

		self.col_locs = [0]
		loc = 0
		for n in range(self.GetColumnCount()):
			loc = loc + self.GetColumnWidth(n)
			self.col_locs.append(loc)


		col = bisect(self.col_locs, x+self.GetScrollPos(wx.HORIZONTAL)) - 1
		self.OpenEditor(col, row)


	def OpenEditor(self, col, row):
		''' Opens an editor at the current position. '''

		# give the derived class a chance to Allow/Veto this edit.
		evt = wx.ListEvent(wx.wxEVT_COMMAND_LIST_BEGIN_LABEL_EDIT, self.GetId())
		evt.Index = row
		evt.Column = col
		item = self.GetItem(row, col)
		evt.Item.SetId(item.GetId())
		evt.Item.SetColumn(item.GetColumn())
		evt.Item.SetData(item.GetData())
		evt.Item.SetText(item.GetText())
		ret = self.GetEventHandler().ProcessEvent(evt)
		if ret and not evt.IsAllowed():
			return   # user code doesn't allow the edit.

		if self.GetColumn(col).Align != self.col_style:
			self.make_editor(self.GetColumn(col).Align)

		x0 = self.col_locs[col]
		x1 = self.col_locs[col+1] - x0

		scrolloffset = self.GetScrollPos(wx.HORIZONTAL)

		# scroll forward
		if x0+x1-scrolloffset > self.GetSize()[0]:
			if wx.Platform == "__WXMSW__":
				# don't start scrolling unless we really need to
				offset = x0+x1-self.GetSize()[0]-scrolloffset
				# scroll a bit more than what is minimum required
				# so we don't have to scroll everytime the user presses TAB
				# which is very tireing to the eye
				addoffset = self.GetSize()[0]/4
				# but be careful at the end of the list
				if addoffset + scrolloffset < self.GetSize()[0]:
					offset += addoffset

				self.ScrollList(offset, 0)
				scrolloffset = self.GetScrollPos(wx.HORIZONTAL)
			else:
				# Since we can not programmatically scroll the ListCtrl
				# close the editor so the user can scroll and open the editor
				# again
				self.editor.SetValue(self.GetItem(row, col).GetText())
				self.curRow = row
				self.curCol = col
				self.CloseEditor()
				return

		y0 = self.GetItemRect(row)[1]

		editor = self.editor
		editor.SetSize(x0-scrolloffset,y0, x1,-1)

		editor.SetValue(self.GetItem(row, col).GetText())
		editor.Show()
		editor.Raise()
		editor.SetSelection(-1,-1)
		editor.SetFocus()

		self.curRow = row
		self.curCol = col


	# FIXME: this function is usually called twice - second time because
	# it is binded to wx.EVT_KILL_FOCUS. Can it be avoided? (MW)
	def CloseEditor(self, evt=None):
		''' Close the editor and save the new value to the ListCtrl. '''
		if not self.editor.IsShown():
			return
		text = self.editor.GetValue()
		self.editor.Hide()
		self.SetFocus()

		# post wxEVT_COMMAND_LIST_END_LABEL_EDIT
		# Event can be vetoed. It doesn't has SetEditCanceled(), what would
		# require passing extra argument to CloseEditor()
		evt = wx.ListEvent(wx.wxEVT_COMMAND_LIST_END_LABEL_EDIT, self.GetId())
		evt.Index = self.curRow
		evt.Column = self.curCol

		item = self.GetItem(self.curRow, self.curCol)
		"""evt.Item.SetId(item.GetId())
		evt.Item.SetColumn(item.GetColumn())
		evt.Item.SetData(item.GetData())
		evt.Item.SetText(text) #should be empty string if editor was canceled"""
		
		item.SetText(text) # The above code is broken in Python3
		evt.Item = item

		ret = self.GetEventHandler().ProcessEvent(evt)
		if not ret or evt.IsAllowed():
			if self.IsVirtual():
				# replace by whather you use to populate the virtual ListCtrl
				# data source
				self.SetVirtualData(self.curRow, self.curCol, text)
			else:
				self.SetItem(self.curRow, self.curCol, text)
		self.RefreshItem(self.curRow)

	def _SelectIndex(self, row):
		listlen = self.GetItemCount()
		if row < 0 and not listlen:
			return
		if row > (listlen-1):
			row = listlen -1

		self.SetItemState(self.curRow, ~wx.LIST_STATE_SELECTED,
						  wx.LIST_STATE_SELECTED)
		self.EnsureVisible(row)
		self.SetItemState(row, wx.LIST_STATE_SELECTED,
						  wx.LIST_STATE_SELECTED)
