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

class BEEFRoom(BEEFBaseResource):
	def __init__(self, top, name):
		BEEFBaseResource.__init__(self, top, name)
		self.path = "/resources/rooms/"
		self.type = 9
		self.properties = {
			"width": 1920,
			"height": 1080,
			"is_persistent": False,

			"background_color": [255, 255, 255, 255],
			"is_background_color_enabled": True,
			"backgrounds": [],
			"is_views_enabled": False,
			"views": [],

			"instances": [], # Each instance is as follows: [object, x, y, z]
			"gravity": 0.0
		}

	def getEvents(self):
		return []
	def getEventHeaders(self):
		return []
	def getInstanceMap(self):
		return ["{}\t{}\t{}\t{}".format(*inst) for inst in self.properties["instances"]]

	def initPageSpecific(self):
		self.gbs = wx.GridBagSizer(12, 2)

		# Column 1
		self.pageAddStatictext("Name:", (0,0))
		self.pageAddTextctrl("tc_name", self.name, (1,0), (1,2))

		instanceSizer = wx.StaticBoxSizer(wx.VERTICAL, self.page, "Instances")
		st_instance = self.pageMakeStatictext("Creating instances for:")
		objects = [obj.name for obj in self.top.objects]
		ch_instance = self.pageMakeChoice("ch_instance", objects, 0)
		instanceSizer.AddMany([(st_instance), (ch_instance)])
		self.gbs.Add(instanceSizer, (2,0), (1,2))

		settingsSizer = wx.StaticBoxSizer(wx.VERTICAL, self.page, "Settings")
		cb_is_persistent = self.pageMakeCheckbox("cb_is_persistent", "Persistent Instances", self.properties["is_persistent"])
		st_width = self.pageMakeStatictext("Width:")
		tc_width = self.pageMakeTextctrl("tc_width", str(self.properties["width"]))
		st_height = self.pageMakeStatictext("Height:")
		tc_height = self.pageMakeTextctrl("tc_height", str(self.properties["height"]))
		settingsSizer.AddMany([(cb_is_persistent), (st_width), (tc_width), (st_height), (tc_height)])
		self.gbs.Add(settingsSizer, (3,0), (1,2))

		backgroundSizer = wx.StaticBoxSizer(wx.VERTICAL, self.page, "Backgrounds")
		self.gbs.Add(backgroundSizer, (4,0), (1,2))

		viewSizer = wx.StaticBoxSizer(wx.VERTICAL, self.page, "Views")
		self.gbs.Add(viewSizer, (5,0), (1,2))

		self.pageAddButton("bt_ok", "OK", (7,0))

		# Column 2
		gr = self.pageAddGrid("gr_instances", (0,3), (7,1))
		for inst in self.properties["instances"]:
			gr.AddInstance(inst)
		if self.top.objects:
			gr.SetObject(self.top.objects[0].name)
		gr.SetDimensions(self.properties["width"], self.properties["height"])
		gr.Redraw()

		self.gbs.AddGrowableRow(6)
		self.gbs.AddGrowableCol(3)
		self.sizer = wx.BoxSizer()
		self.sizer.Add(self.gbs, 1, wx.ALL | wx.EXPAND, 20)
		self.page.SetSizer(self.sizer)

	def onTextSpecific(self, event):
		tc = event.GetEventObject()
		if tc == self.inputs["tc_width"] or tc == self.inputs["tc_height"]:
			gr.SetDimensions(self.inputs["tc_width"].GetValue(), self.inputs["tc_height"].GetValue())

		return True
	def onCheckBoxSpecific(self, event):
		return True
	def onButtonSpecific(self, event):
		bt = event.GetEventObject()
		if bt == self.inputs["bt_ok"]:
			self.destroyPage()

		return True
	def onChoiceSpecific(self, event):
		ch = event.GetEventObject()
		if ch == self.inputs["ch_instance"]:
			self.inputs["gr_instances"].SetObject(ch.GetString(ch.GetSelection()))

		return False

	def update(self):
		pass

	def commitPage(self):
		if self.page:
			tc_name = self.inputs["tc_name"]
			if tc_name.GetValue() != self.name:
				self.rename(tc_name.GetValue())

			self.properties["is_persistent"] = self.inputs["cb_is_persistent"].GetValue()

			self.properties["width"] = int(self.inputs["tc_width"].GetValue())
			self.properties["height"] = int(self.inputs["tc_height"].GetValue())

			self.properties["instances"] = [inst for inst in self.inputs["gr_instances"].instances]
	def moveTo(self, name, newfile):
		"""if self.properties["path"]:
			ext = os.path.splitext(self.properties["path"])[1]
			os.rename(self.top.rootDir+self.properties["path"], newfile+ext)
			self.properties["path"] = self.path+name+ext
			self.inputs["st_path"].SetLabel("Path: {}".format(self.properties["path"]))"""

	def MenuDuplicate(self, event):
		r = BEEFRoom(self.top, None)
		r.properties = copy.deepcopy(self.properties)
		self.top.addRoom(self.name, r)
