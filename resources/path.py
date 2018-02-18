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

from ui.validators import BEEFValidatorFloat

class BEEFPath(BEEFBaseResource):
	def __init__(self, top, name):
		BEEFBaseResource.__init__(self, top, name)
		self.path = "/resources/paths/"
		self.type = EResource.PATH
		self.properties = {
			"coordinates": [],
			"is_curved": False,
			"is_closed": True
		}

	def getInit(self):
		init = ""
		if self.properties["coordinates"]:
			for c in self.properties["coordinates"]:
				init += "\n\t\t\t{name}->add_coordinate({x}, {y}, {z}, {speed});".format(name=self.name, x=c[0], y=c[1], z=c[2], speed=c[3])
		if self.properties["is_curved"]:
			init += "\n\t\t\t{name}->set_is_curved({curved});".format(name=self.name, curved=str(self.properties["is_curved"]).lower())
		if not self.properties["is_closed"]:
			init += "\n\t\t\t{name}->set_is_closed({closed});".format(name=self.name, closed=str(self.properties["is_closed"]).lower())
		return init

	def initPageSpecific(self):
		self.gbs = wx.GridBagSizer(12, 2)

		# Column 1
		self.pageAddStatictext("Name:", (0,0))
		self.pageAddTextctrl("tc_name", self.name, (1,0), (1,2))

		self.pageAddCheckbox("cb_is_curved", "Smooth Curve", (2,0), self.properties["is_curved"])
		self.pageAddCheckbox("cb_is_closed", "Closed Path", (3,0), self.properties["is_closed"])

		lst = self.pageAddListCtrl("lst_coordinates", ["X", "Y", "Z", "Speed"], (4,0), (1,2)) # Perhaps replace with a Grid
		lst.SetValidators(BEEFValidatorFloat())
		for c in self.properties["coordinates"]:
			self.addListRow("lst_coordinates", c)

		self.pageAddButton("bt_add_coord", "Add Coordinate", (5,0))
		self.pageAddButton("bt_remove_coord", "Remove Coordinate", (5,1))

		self.pageAddButton("bt_ok", "OK", (6,0))

		# Column 2
		pl = self.pageAddPlot("pl_coordinates", (0,3), (6,1))
		pl.SetCoords(self.properties["coordinates"])
		pl.Redraw()

		self.gbs.AddGrowableRow(4)
		self.gbs.AddGrowableCol(3)
		self.sizer = wx.BoxSizer()
		self.sizer.Add(self.gbs, 1, wx.ALL | wx.EXPAND, 20)
		self.page.SetSizer(self.sizer)

	def onTextSpecific(self, event):
		return True
	def onCheckBoxSpecific(self, event):
		cb = event.GetEventObject()
		if cb == self.inputs["cb_is_curved"]:
			# Draw curved path
			self.inputs["pl_coordinates"].Redraw()
		elif cb == self.inputs["cb_is_closed"]:
			# Draw closed path
			self.inputs["pl_coordinates"].Redraw()
	def onButtonSpecific(self, event):
		bt = event.GetEventObject()
		if bt == self.inputs["bt_ok"]:
			self.destroyPage()
		elif bt == self.inputs["bt_add_coord"]:
			self.addListRow("lst_coordinates", ["0", "0", "0", "1"])
			pl = self.inputs["pl_coordinates"]
			pl.SetCoords(self.inputs["lst_coordinates"].GetItemList())
			pl.Redraw()
		elif bt == self.inputs["bt_remove_coord"]:
			self.removeListRow("lst_coordinates", -1)
			pl = self.inputs["pl_coordinates"]
			pl.SetCoords(self.inputs["lst_coordinates"].GetItemList())
			pl.Redraw()

		return True
	def onListEditSpecific(self, event):
		pl = self.inputs["pl_coordinates"]

		# Update the coords with the new event data
		coords = self.inputs["lst_coordinates"].GetItemList()
		item = event.GetItem()
		c = list(coords[item.GetId()])
		c[item.GetColumn()] = item.GetText()
		coords[item.GetId()] = tuple(c)
		pl.SetCoords(coords)

		pl.Redraw()
		return True

	def update(self):
		pass

	def commitPage(self):
		if self.page:
			tc_name = self.inputs["tc_name"]
			if tc_name.GetValue() != self.name:
				self.rename(tc_name.GetValue())

			self.properties["is_curved"] = self.inputs["cb_is_curved"].GetValue()
			self.properties["is_closed"] = self.inputs["cb_is_closed"].GetValue()

			self.properties["coordinates"] = []
			for c in self.inputs["lst_coordinates"].GetItemList():
				self.properties["coordinates"].append(c)
	def moveTo(self, name, newfile):
		"""if self.properties["path"]:
			ext = os.path.splitext(self.properties["path"])[1]
			os.rename(self.top.rootDir+self.properties["path"], newfile+ext)
			self.properties["path"] = self.path+name+ext
			self.inputs["st_path"].SetLabel("Path: {}".format(self.properties["path"]))"""

	def MenuDuplicate(self, event):
		r = BEEFPath(self.top, None)
		r.properties = copy.deepcopy(self.properties)
		self.top.addPath(self.name, r)
