# Copyright (c) 2017 Luke Montalvo <lukemontalvo@gmail.com>
#
# This file is part of BEE.
# BEE is free software and comes with ABSOLUTELY NO WARANTY.
# See LICENSE for more details.

try:
	import wx
except ImportError:
	raise ImportError("The wxPython module is required to run this program")

class BEEFToolBar(wx.ToolBar):
	def __init__(self, parent):
		wx.ToolBar.__init__(self, parent)
		self.parent = parent

		tsize = (24,24)

		newProjectBmp =  wx.ArtProvider.GetBitmap(wx.ART_NEW, wx.ART_TOOLBAR, tsize)
		openProjectBmp = wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_TOOLBAR, tsize)
		saveProjectBmp = wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_TOOLBAR, tsize)

		runGameBmp =  wx.ArtProvider.GetBitmap(wx.ART_EXECUTABLE_FILE, wx.ART_TOOLBAR, tsize)
		debugGameBmp = wx.ArtProvider.GetBitmap(wx.ART_WARNING, wx.ART_TOOLBAR, tsize)
		packageGameBmp = wx.ArtProvider.GetBitmap(wx.ART_HARDDISK, wx.ART_TOOLBAR, tsize)

		self.SetToolBitmapSize(tsize)

		self.AddTool(10, "New Project", newProjectBmp, "Create a new game project")
		self.AddTool(20, "Open Project", openProjectBmp, "Open a game project")
		self.AddTool(30, "Save Project", saveProjectBmp, "Save the current game project")

		self.AddSeparator()
		self.AddTool(40, "Run", runGameBmp, "Run the game")
		self.AddTool(50, "Debug", debugGameBmp, "Debug the game")
		self.AddTool(60, "Package Executable", packageGameBmp, "Create a standalone executable for distribution")

	def Bind(self):
		self.parent.Bind(wx.EVT_TOOL, self.parent.menubar.MenuFileNew, id=10)
		self.parent.Bind(wx.EVT_TOOL, self.parent.menubar.MenuFileOpen, id=20)
		self.parent.Bind(wx.EVT_TOOL, self.parent.menubar.MenuFileSave, id=30)

		self.parent.Bind(wx.EVT_TOOL, self.parent.menubar.MenuBuildRun, id=40)
		self.parent.Bind(wx.EVT_TOOL, self.parent.menubar.MenuBuildDebug, id=50)
		self.parent.Bind(wx.EVT_TOOL, self.parent.menubar.MenuBuildPackage, id=60)
