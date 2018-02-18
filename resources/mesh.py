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

class BEEFMesh(BEEFBaseResource):
	def __init__(self, top, name):
		BEEFBaseResource.__init__(self, top, name)
		self.path = "/resources/meshes/"
		self.type = EResource.MESH
		self.properties = {
			"path": "",
			"has_material": False
		}

	def initPageSpecific(self):
		self.gbs = wx.GridBagSizer(12, 2)

		self.pageAddStatictext("Name:", (0,0))
		self.pageAddTextctrl("tc_name", self.name, (1,0), (1,2))
		self.pageAddButton("bt_edit", "Edit Mesh", (2,0))
		self.pageAddButton("bt_import", "Import", (2,1))

		self.pageAddStatictext("Path: {}".format(self.properties["path"]), (4,0), name="st_path")

		self.pageAddButton("bt_ok", "OK", (5,0))

		self.sizer = wx.BoxSizer()
		self.sizer.Add(self.gbs, 1, wx.ALL | wx.EXPAND, 20)
		self.page.SetSizer(self.sizer)

	def onTextSpecific(self, event):
		return True
	def onButtonSpecific(self, event):
		bt = event.GetEventObject()
		if bt == self.inputs["bt_ok"]:
			self.destroyPage()
		elif bt == self.inputs["bt_edit"]:
			return self.top.editResource(self)
		elif bt == self.inputs["bt_import"]:
			wildcards = (
				"Wavefront Meshes (*.obj,*.mtl)|*.obj;*.mtl|"
				"All files (*)|*"
			)

			d = self.top.rootDir+os.path.dirname(self.properties["path"])
			f = os.path.basename(self.properties["path"])
			if not self.properties["path"]:
				d = os.getcwd()
				f = ""

			dialog = wx.FileDialog(
				self.top, message="Import Mesh",
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
				shutil.copyfile(path, self.top.rootDir+self.properties["path"])

				mtl = os.path.splitext(path)[0]+".mtl"
				self.properties["has_material"] = os.path.isfile(mtl)
				if self.properties["has_material"]:
					shutil.copyfile(mtl, self.top.rootDir + self.path+self.name+".mtl")

				self.update()
			else:
				dialog.Destroy()
				return False

			dialog.Destroy()

		return True

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
			os.rename(self.top.rootDir+self.properties["path"], newfile+ext)
			self.properties["path"] = self.path+name+ext
			self.inputs["st_path"].SetLabel("Path: {}".format(self.properties["path"]))

	def MenuDuplicate(self, event):
		r = BEEFMesh(self.top, None)
		r.properties = copy.deepcopy(self.properties)
		self.top.addMesh(self.name, r)
