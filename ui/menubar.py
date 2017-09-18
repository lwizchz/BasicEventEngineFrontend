# Copyright (c) 2017 Luke Montalvo <lukemontalvo@gmail.com>
#
# This file is part of BEE.
# BEE is free software and comes with ABSOLUTELY NO WARANTY.
# See LICENSE for more details.

try:
	import wx
except ImportError:
	raise ImportError("The wxPython module is required to run this program")

import os
import webbrowser

class BEEFMenuBar(wx.MenuBar):
	def __init__(self, parent):
		wx.MenuBar.__init__(self)
		self.parent = parent

		menu1 = wx.Menu()
		menu1.Append(101, "&New Project\tCtrl-N", "Create a new game project")
		menu1.Append(102, "&Open Project\tCtrl-O", "Open a game project")
		menu1.Append(103, "&Save Project\tCtrl-S", "Save the current game project")
		menu1.Append(104, "Save &As\tCtrl-Shift-S", "Save the current game project under a different name")
		menu1.Append(105, "&Close Project", "Close the current game project")
		menu1.Append(106, "&Preferences\tCtrl-,", "View and modify the BEEF Preferences")
		menu1.Append(107, "&Quit\tCtrl-Q", "Close BEEF")
		self.Append(menu1, "&File")

		menu2 = wx.Menu()
		menu2.Append(201, "&Undo\tCtrl-Z", "Undo the last action")
		menu2.Append(202, "&Redo\tCtrl-Y", "Redo the last undone action")
		menu2.AppendSeparator()
		menu2.Append(203, "Edit &Config", "Edit the game config options")
		self.Append(menu2, "&Edit")

		menu3 = wx.Menu()
		menu3.Append(301, "&Run\tF5", "Run the game")
		menu3.Append(302, "&Debug\tF6", "Debug the game")
		menu3.Append(303, "&Clean", "Clean the build directory")
		menu3.Append(304, "&Package Executable\tF7", "Create a standalone executable for distribution")
		self.Append(menu3, "&Build")

		menu4 = wx.Menu()
		menu4.Append(401, "&Report a Bug", "Open the Github Issue tracker")
		menu4.Append(402, "&Github", "Open the Github")
		menu4.Append(403, "&About", "Read information about BEEF")
		self.Append(menu4, "&Help")

		self.wildcards = (
			"BEE Project File (*.bpf)|*.bpf|"
			"All files (*)|*"
		)

	def Bind(self):
		self.parent.Bind(wx.EVT_MENU, self.MenuFileNew, id=101)
		self.parent.Bind(wx.EVT_MENU, self.MenuFileOpen, id=102)
		self.parent.Bind(wx.EVT_MENU, self.MenuFileSave, id=103)
		self.parent.Bind(wx.EVT_MENU, self.MenuFileSaveAs, id=104)
		self.parent.Bind(wx.EVT_MENU, self.MenuFileClose, id=105)
		self.parent.Bind(wx.EVT_MENU, self.MenuFilePreferences, id=106)
		self.parent.Bind(wx.EVT_MENU, self.MenuFileQuit, id=107)

		self.parent.Bind(wx.EVT_MENU, self.MenuEditUndo, id=201)
		self.parent.Bind(wx.EVT_MENU, self.MenuEditRedo, id=202)
		self.parent.Bind(wx.EVT_MENU, self.MenuEditConfig, id=203)

		self.parent.Bind(wx.EVT_MENU, self.MenuBuildRun, id=301)
		self.parent.Bind(wx.EVT_MENU, self.MenuBuildDebug, id=302)
		self.parent.Bind(wx.EVT_MENU, self.MenuBuildClean, id=303)
		self.parent.Bind(wx.EVT_MENU, self.MenuBuildPackage, id=304)

		self.parent.Bind(wx.EVT_MENU, self.MenuHelpBug, id=401)
		self.parent.Bind(wx.EVT_MENU, self.MenuHelpGithub, id=402)
		self.parent.Bind(wx.EVT_MENU, self.MenuHelpAbout, id=403)

	def MenuFileNew(self, event):
		if self.parent.confirmClose():
			self.parent.new()
	def MenuFileOpen(self, event):
		dialog = wx.FileDialog(
			self, message="Open Project",
			defaultDir=os.getcwd(),
			defaultFile="",
			wildcard=self.wildcards,
			style=wx.FD_OPEN | wx.FD_CHANGE_DIR
		)

		if dialog.ShowModal() == wx.ID_OK:
			path = dialog.GetPath()
			self.parent.load(path)

		dialog.Destroy()
	def MenuFileSave(self, event):
		if self.parent.projectFilename != "":
			self.parent.save()
		else:
			self.MenuFileSaveAs(None)
	def MenuFileSaveAs(self, event):
		fn = self.parent.projectFilename
		fn = os.path.basename(fn)

		dialog = wx.FileDialog(
			self, message="Save Project",
			defaultDir=os.getcwd(),
			defaultFile=fn,
			wildcard=self.wildcards,
			style=wx.FD_SAVE | wx.FD_CHANGE_DIR
		)

		if dialog.ShowModal() == wx.ID_OK:
			path = dialog.GetPath()

			e = os.path.splitext(path)[1].strip()
			if e == "":
				path += ".bpf"

			self.parent.save(path)

		dialog.Destroy()
	def MenuFileClose(self, event):
		if self.parent.confirmClose():
			self.parent.new()
	def MenuFilePreferences(self, event):
		pass
	def MenuFileQuit(self, event):
		self.parent.quit(event)

	def MenuEditUndo(self, event):
		pass
	def MenuEditRedo(self, event):
		pass
	def MenuEditConfig(self, event):
		pass

	def MenuBuildRun(self, event):
		pass
	def MenuBuildDebug(self, event):
		pass
	def MenuBuildClean(self, event):
		pass
	def MenuBuildPackage(self, event):
		pass

	def MenuHelpBug(self, event):
		webbrowser.open_new_tab("https://github.com/piluke/BasicEventEngineFrontend/issues/new")
	def MenuHelpGithub(self, event):
		webbrowser.open_new_tab("https://github.com/piluke/BasicEventEngineFrontend")
	def MenuHelpAbout(self, event):
		self.parent.ShowAbout()
