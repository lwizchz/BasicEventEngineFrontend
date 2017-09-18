# Copyright (c) 2017 Luke Montalvo <lukemontalvo@gmail.com>
#
# This file is part of BEE.
# BEE is free software and comes with ABSOLUTELY NO WARANTY.
# See LICENSE for more details.

try:
	import wx
except ImportError:
	raise ImportError("The wxPython module is required to run this program")

import copy
import os
import shutil

from resources.base import BEEFBaseResource

class BEEFFont(BEEFBaseResource):
	def __init__(self, top, name):
		BEEFBaseResource.__init__(self, top, name)
		self.path = "/resources/fonts/"
		self.type = 3
		self.properties = {
			"path": "",
			"style": "regular",
			"size": 24,
			"lineskip": 0
		}

	def getTestString(self):
		s = ""

		for i in range(26):
			s += chr(ord("A")+i)
		s += "\n"
		for i in range(26):
			s += chr(ord("a")+i)
		s += "\n"
		for i in range(10):
			s += chr(ord("0")+i)

		return s

	def initPageSpecific(self):
		self.gbs = wx.GridBagSizer(12, 2)

		# Column 1
		self.pageAddStatictext("Name:", (0,0))
		self.pageAddTextctrl("tc_name", self.name, (1,0), (1,2))
		self.pageAddButton("bt_import", "Import", (2,0))

		self.pageAddStatictext("Size:", (3,0))
		self.pageAddSpinctrl("sc_size", 1, 1000, self.properties["size"], (4,0))

		self.pageAddStatictext("Lineskip: (0 for font default)", (5,0))
		self.pageAddSpinctrl("sc_lineskip", 0, 100, self.properties["lineskip"], (6,0))

		self.pageAddStatictext("Path: {}".format(self.properties["path"]), (7,0), name="st_path")

		self.pageAddButton("bt_ok", "OK", (8,0))

		# Column 2
		self.pageAddStatictext(self.getTestString(), (0,2), (8,1), name="st_test")
		font = wx.Font(self.properties["size"], wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Courier")
		self.inputs["st_test"].SetFont(font)

		self.sizer = wx.BoxSizer()
		self.sizer.Add(self.gbs, 1, wx.ALL | wx.EXPAND, 20)
		self.page.SetSizer(self.sizer)

	def onTextSpecific(self, event):
		return True
	def onCheckBoxSpecific(self, event):
		pass
	def onButtonSpecific(self, event):
		bt = event.GetEventObject()
		if bt == self.inputs["bt_ok"]:
			self.destroyPage()
		elif bt == self.inputs["bt_import"]:
			wildcards = (
				"TTF font file (*.ttf)|*.ttf|"
				"All files (*)|*"
			)

			d = self.top.tmpDir+os.path.dirname(self.properties["path"])
			f = os.path.basename(self.properties["path"])
			if not self.properties["path"]:
				d = os.getcwd()
				f = ""

			dialog = wx.FileDialog(
				self.top, message="Import Font",
				defaultDir=d,
				defaultFile=f,
				wildcard=wildcards,
				style=wx.FD_OPEN
			)

			if dialog.ShowModal() == wx.ID_OK:
				path = dialog.GetPath()
				ext = os.path.splitext(path)[1]

				if self.properties["path"] == self.path+self.name+ext:
					dialog.Destroy()
					return False

				self.properties["path"] = self.path+self.name+ext
				shutil.copyfile(path, self.top.tmpDir+self.properties["path"])

				self.update()
			else:
				dialog.Destroy()
				return False

			dialog.Destroy()

		return True
	def onSliderSpecific(self, event):
		pass
	def onSpinCtrlSpecific(self, event):
		sc = event.GetEventObject()
		if sc == self.inputs["sc_size"]:
			self.properties["size"] = sc.GetValue()
			font = wx.Font(self.properties["size"], wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Courier")
			self.inputs["st_test"].SetFont(font)
	def onListEditSpecific(self, event):
		pass

	def update(self):
		self.inputs["st_path"].SetLabel("Path: {}".format(self.properties["path"]))

	def commitPage(self):
		if self.page:
			tc_name = self.inputs["tc_name"]
			if tc_name.GetValue() != self.name:
				self.rename(tc_name.GetValue())
	def moveTo(self, name, newfile):
		if self.properties["path"]:
			ext = os.path.splitext(self.properties["path"])[1]
			os.rename(self.top.tmpDir+self.properties["path"], newfile+ext)
			self.properties["path"] = self.path+name+ext
			self.inputs["st_path"].SetLabel("Path: {}".format(self.properties["path"]))

	def MenuDuplicate(self, event):
		r = BEEFFont(self.top, None)
		r.properties = copy.deepcopy(self.properties)
		self.top.addFont(self.name, r)
