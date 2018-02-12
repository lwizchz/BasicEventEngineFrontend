# Copyright (c) 2017-18 Luke Montalvo <lukemontalvo@gmail.com>
#
# This file is part of BEEF.
# BEEF is free software and comes with ABSOLUTELY NO WARANTY.
# See LICENSE for more details.

try:
	import wx
except ImportError:
	raise ImportError("The wxPython module is required to run this program")

import wx.aui

class BEEFNotebook(wx.aui.AuiNotebook):
	def __init__(self, top, parent):
		wx.aui.AuiNotebook.__init__(self, parent, style=wx.aui.AUI_NB_DEFAULT_STYLE | wx.aui.AUI_NB_CLOSE_ON_ALL_TABS)
		self.top = top
		self.parent = parent
