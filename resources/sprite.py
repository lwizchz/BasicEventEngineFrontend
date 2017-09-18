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

class BEEFSprite(BEEFBaseResource):
	def __init__(self, top, name):
		BEEFBaseResource.__init__(self, top, name)
		self.path = "/resources/sprites/"
		self.type = 0
		self.properties = {
			"path": "",
			"width": 0,
			"height": 0,
			"subimage_amount": 0,
			"subimage_width": 0,
			"speed": 1.0
		}

	def initPageSpecific(self):
		self.gbs = wx.GridBagSizer(12, 2)

		self.pageAddStatictext("Name:", (0,0))
		self.pageAddTextctrl("tc_name", self.name, (1,0), (1,2))
		self.pageAddButton("bt_edit", "Edit Image", (2,0))
		self.pageAddButton("bt_import", "Import", (2,1))

		self.pageAddStatictext("Image:", (3,0))

		path = self.properties["path"]
		imgpath = self.top.tmpDir+path

		w = self.properties["width"]
		h = self.properties["height"]
		self.pageAddBitmap("bmp_sprite", imgpath, (4,0), imgsize=self.getBmpSize((w, h), (128,128)))

		self.pageAddStatictext("Dimensions: {}px by {}px".format(w, h), (5,0), name="st_dimensions")

		self.pageAddStatictext("Path: {}".format(path), (6,0), name="st_path")

		self.pageAddButton("bt_ok", "OK", (7,0))

		self.sizer = wx.BoxSizer()
		self.sizer.Add(self.gbs, 1, wx.ALL | wx.EXPAND, 20)
		self.page.SetSizer(self.sizer)

	def getBmpSize(self, size, maxSize):
		width, height = size
		maxW, maxH = maxSize

		w = maxW
		h = maxW*max(height,1)/max(width,1)

		if h > maxH:
			h = maxH
			w = maxH*w/h

		return (w,h)

	def onTextSpecific(self, event):
		return True
	def onCheckBoxSpecific(self, event):
		pass
	def onButtonSpecific(self, event):
		bt = event.GetEventObject()
		if bt == self.inputs["bt_ok"]:
			self.destroyPage()
		elif bt == self.inputs["bt_edit"]:
			return self.top.editResource(self)
		elif bt == self.inputs["bt_import"]:
			wildcards = (
				"PNG Image (*.png)|*.png|"
				"All files (*)|*"
			)

			d = self.top.tmpDir+os.path.dirname(self.properties["path"])
			f = os.path.basename(self.properties["path"])
			if not self.properties["path"]:
				d = os.getcwd()
				f = ""

			dialog = wx.FileDialog(
				self.top, message="Import Sprite",
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
		pass
	def onListEditSpecific(self, event):
		pass

	def update(self):
		self.inputs["st_path"].SetLabel("Path: {}".format(self.properties["path"]))

		img = wx.Image(self.top.tmpDir+self.properties["path"])
		w = img.GetWidth()
		h = img.GetHeight()
		self.properties["width"] = w
		self.properties["height"] = h

		img.Rescale(*self.getBmpSize((w, h), (128,128)))
		self.inputs["bmp_sprite"].SetBitmap(wx.BitmapFromImage(img))

		self.inputs["st_dimensions"].SetLabel("Dimensions: {}px by {}px".format(w, h))

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
		r = BEEFSprite(self.top, None)
		r.properties = copy.deepcopy(self.properties)
		self.top.addSprite(self.name, r)
