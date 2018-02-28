# Copyright (c) 2017-18 Luke Montalvo <lukemontalvo@gmail.com>
#
# This file is part of BEEF.
# BEEF is free software and comes with ABSOLUTELY NO WARANTY.
# See LICENSE for more details.

try:
	import wx
except ImportError:
	raise ImportError("The wxPython module is required to run this program")

import copy
import os
import shutil

from resources.base import BEEFBaseResource
from resources.enum import EResource

class BEEFExtra(BEEFBaseResource):
	def __init__(self, top, name):
		BEEFBaseResource.__init__(self, top, name)
		self.path = "/resources/extras/"
		self.type = EResource.EXTRA
		self.content = ""

	def initPageSpecific(self):
		self.gbs = wx.GridBagSizer(12, 2)

		# Column 1
		self.pageAddStatictext("Name:", (0,0))
		self.pageAddTextctrl("tc_name", self.name, (1,0), (1,2))
		self.pageAddButton("bt_import", "Import", (2,0))

		self.pageAddButton("bt_ok", "OK", (3,0))

		# Column 2
		ed = self.pageAddEditor("ed_content", (0,3), (6,1))
		if self.content is None:
			ed.SetText("# This Extra File is not a text file.")
			ed.Enable(False)
		else:
			ed.SetText(self.content)
		ed.EmptyUndoBuffer()

		self.gbs.AddGrowableRow(2)
		self.gbs.AddGrowableCol(3)
		self.sizer = wx.BoxSizer()
		self.sizer.Add(self.gbs, 1, wx.ALL | wx.EXPAND, 20)
		self.page.SetSizer(self.sizer)

	def onTextSpecific(self, event):
		return True
	def onButtonSpecific(self, event):
		bt = event.GetEventObject()
		if bt == self.inputs["bt_ok"]:
			self.destroyPage()
		elif bt == self.inputs["bt_import"]:
			wildcards = (
				"All files (*)|*"
			)

			d = self.top.rootDir+os.path.dirname(self.path+self.name)
			f = os.path.basename(self.path+self.name)

			dialog = wx.FileDialog(
				self.top, message="Import Extra File",
				defaultDir=d,
				defaultFile=f,
				wildcard=wildcards,
				style=wx.FD_OPEN
			)

			if dialog.ShowModal() == wx.ID_OK:
				path = dialog.GetPath()
				ext = os.path.splitext(path)[1]

				if path != self.top.rootDir+self.path+self.name:
					shutil.copyfile(path, self.top.rootDir+self.path+self.name)

				self.update()
			else:
				dialog.Destroy()
				return False

			dialog.Destroy()

		return True
	def onEditorSpecific(self, event):
		return True

	def serialize(self):
		return self.content
	def deserialize(self, data):
		self.content = data

	def update(self):
		try:
			with open(self.top.rootDir+self.path+self.name, "r") as f:
				self.content = f.read()
			if "ed_content" in self.inputs:
				self.inputs["ed_content"].SetText(self.content)
		except UnicodeDecodeError:
			self.content = None
			if "ed_content" in self.inputs:
				self.inputs["ed_content"].SetText("")

		if "ed_content" in self.inputs:
			self.inputs["ed_content"].Enable(not self.content is None)

	def commitPage(self):
		if self.page:
			tc_name = self.inputs["tc_name"]
			if tc_name.GetValue() != self.name:
				self.rename(tc_name.GetValue())

			if not self.content is None:
				self.content = self.inputs["ed_content"].GetText()
	def rename(self, name):
		if name == self.name:
			return True

		if not self.checkName(name):
			return False

		oldfile = self.top.rootDir+self.path+self.name
		newfile = self.top.rootDir+self.path+name
		if os.path.isfile(oldfile):
			os.rename(oldfile, newfile)

		if self.name in self.top.gameCfg["open_resources"]:
			self.top.gameCfg["open_resources"].remove(self.name)
			self.top.gameCfg["open_resources"].append(name)

		self.name = name

		if self.treeitem:
			self.top.treectrl.SetItemText(self.treeitem, self.name)

		if self.page:
			self.top.notebook.SetPageText(self.pageIndex, self.name)

		self.top.setUnsaved()
		return True

	def MenuDuplicate(self, event):
		r = BEEFExtra(self.top, None)
		r.content = self.content
		self.top.addExtra(self.name, r)
