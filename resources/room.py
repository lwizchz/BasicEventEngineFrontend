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

class BEEFRoom(BEEFBaseResource):
	def __init__(self, top, name):
		BEEFBaseResource.__init__(self, top, name)
		self.path = "/resources/rooms/"
		self.type = EResource.ROOM
		self.properties = {
			"width": 1920,
			"height": 1080,
			"is_persistent": False,

			"is_background_color_enabled": True,
			"background_color": [255, 255, 255, 255],
			"backgrounds": [], # Each background is as follows: {"texture": t, "is_visible": v, "is_foreground": f, "pos": (x, y), "tile": (h, v), "speed": (h, v), "is_stretched": s}
			"is_views_enabled": False,
			"views": {}, # Each view is as follows: (id: {"is_active": a, "view": (x, y, w, h), "port": (x, y, w, h)})

			"instances": [], # Each Instance is as follows: [object, x, y, z]
			"gravity": 0.0
		}

	def getEvents(self):
		return []
	def getEventHeaders(self):
		return []
	def getInstanceMap(self):
		return ["{}\t{}\t{}\t{}".format(*inst) for inst in self.properties["instances"]]
	def getInit(self):
		init = ""
		if self.properties["is_persistent"]:
			init += "\n\t\t\t{name}->set_is_persistent(true);".format(name=self.name)
		if not self.properties["is_background_color_enabled"]:
			init += "\n\t\t\t{name}->set_is_background_color_enabled(false);".format(name=self.name)
		if self.properties["background_color"]:
			init += "\n\t\t\t{name}->set_background_color({{{c[0]}, {c[1]}, {c[2]}, {c[3]}}});".format(name=self.name, c=self.properties["background_color"])
		for b in self.properties["backgrounds"]:
			init += "\n\t\t\t{name}->add_background({b[texture]}, {b[is_visible]}, {b[is_foreground]}, {b[pos][0]}, {b[pos][1]}, {b[tile][0]}, {b[tile][1]}, {b[speed][0]}, {b[speed][1]}, {b[is_stretched]});".format(name=self.name, b=b)
		if self.properties["is_views_enabled"]:
			init += "\n\t\t\t{name}->set_is_views_enabled(true);".format(name=self.name)
		for k, v in self.properties["views"].items():
			init += "\n\t\t\t{name}->set_view({id}, bee::ViewPort({v[is_active]}, {{{v[view][0]}, {v[view][1]}, {v[view][2]}, {v[view][3]}}}, {{{v[port][0]}, {v[port][1]}, {v[port][2]}, {v[port][3]}}}));".format(name=self.name, id=k, v=v)

		return init

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
