# Copyright (c) 2017-18 Luke Montalvo <lukemontalvo@gmail.com>
#
# This file is part of BEEF.
# BEEF is free software and comes with ABSOLUTELY NO WARANTY.
# See LICENSE for more details.

try:
	import wx
except ImportError:
	raise ImportError("The wxPython module is required to run this program")

import os
import sys

class BEEFEditDialog(wx.Dialog):
	def __init__(self, parent, title, default):
		wx.Dialog.__init__(self)
		self.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
		self.Create(parent, -1, "Edit {}".format(title), wx.DefaultPosition, wx.DefaultSize, wx.DEFAULT_DIALOG_STYLE)

		sizer = wx.BoxSizer(wx.VERTICAL)

		label = wx.StaticText(self, -1, "Edit Program:")
		label.SetHelpText("The program that will be used to edit {} resources".format(title.lower()))
		sizer.Add(label, 0, wx.ALL, 5)

		self.text = wx.TextCtrl(self, -1, "", size=(180,-1))
		self.setProgram(default)
		sizer.Add(self.text, 0, wx.ALL, 5)

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

	def getDefault(self):
		if sys.platform.startswith("linux"):
			return "xdg-open"
		elif sys.platform.startswith("win32"):
			return "start"
		elif sys.platform.startswith("darwin"):
			return "open"
	def setProgram(self, program):
		if program:
			self.text.SetValue(program)
		else:
			self.text.SetValue(self.getDefault())

	def show(self):
		self.text.SetFocus()
		val = self.ShowModal()
		if val == wx.ID_OK:
			if self.text.GetValue():
				return self.text.GetValue()
			return self.getDefault()
		return None
