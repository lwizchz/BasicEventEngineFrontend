# Copyright (c) 2017-18 Luke Montalvo <lukemontalvo@gmail.com>
#
# This file is part of BEEF.
# BEEF is free software and comes with ABSOLUTELY NO WARANTY.
# See LICENSE for more details.

try:
	import wx
except ImportError:
	raise ImportError("The wxPython module is required to run this program")

from resources.enum import EEvent

class BEEFEventDialog(wx.Dialog):
	def __init__(self, parent):
		wx.Dialog.__init__(self)
		self.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
		self.Create(parent, -1, "New Event", wx.DefaultPosition, wx.DefaultSize, wx.DEFAULT_DIALOG_STYLE)

		sizer = wx.BoxSizer(wx.VERTICAL)

		label = wx.StaticText(self, -1, "Event Type:")
		sizer.Add(label, 0, wx.ALL, 5)

		self.list = wx.ListBox(self, -1, wx.DefaultPosition, wx.DefaultSize, EEvent._events)
		self.list.SetSelection(1)
		self.Bind(wx.EVT_LISTBOX_DCLICK, self.doubleClick, self.list)
		sizer.Add(self.list, 0, wx.ALL, 5)

		line = wx.StaticLine(self, -1, style=wx.LI_HORIZONTAL)
		sizer.Add(line, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.TOP, 5)

		buttons = wx.StdDialogButtonSizer()
		btn = wx.Button(self, wx.ID_OK)
		btn.SetDefault()
		buttons.Add(btn)

		btn = wx.Button(self, wx.ID_CANCEL)
		buttons.Add(btn)
		buttons.Realize()
		sizer.Add(buttons, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

		self.SetSizer(sizer)
		sizer.Fit(self)

		self.CenterOnScreen()

	def doubleClick(self, event):
		self.EndModal(wx.ID_OK)

	def getEvent(self):
		return self.list.GetSelection()
	def getEventStr(self):
		return EEvent.get(self.getEvent())
