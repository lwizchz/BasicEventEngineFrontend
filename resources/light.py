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
from resources.enum import ELight

class BEEFLight(BEEFBaseResource):
	def __init__(self, top, name):
		BEEFBaseResource.__init__(self, top, name)
		self.path = "/resources/lights/"
		self.type = 7
		self.properties = {
			"type": ELight.AMBIENT,
			"position": (0, 0, 0),
			"direction": (0, 0, 0),
			"attenuation": (0, 0, 0),
			"color": (255, 255, 255, 255)
		}

	def getInit(self):
		init = ""
		if self.properties["type"] != ELight.AMBIENT:
			init += "\n\t\t\t{name}->set_type(bee::E_LIGHT::{type});".format(name=self.name, type=ELight.str(self.properties["type"]))
		if self.properties["position"] != (0, 0, 0):
			init += "\n\t\t\t{name}->set_position({{{x}, {y}, {z}, 0.0}});".format(name=self.name, x=self.properties["position"][0], y=self.properties["position"][1], z=self.properties["position"][2])
		if self.properties["direction"] != (0, 0, 0):
			init += "\n\t\t\t{name}->set_direction({{{x}, {y}, {z}, 0.0}});".format(name=self.name, x=self.properties["direction"][0], y=self.properties["direction"][1], z=self.properties["direction"][2])
		if self.properties["attenuation"] != (0, 0, 0):
			init += "\n\t\t\t{name}->set_attenuation({{{x}, {y}, {z}, 0.0}});".format(name=self.name, x=self.properties["attenuation"][0], y=self.properties["attenuation"][1], z=self.properties["attenuation"][2])
		if self.properties["color"] != (255, 255, 255, 255):
			init += "\n\t\t\t{name}->set_color({{{r}, {g}, {b}, {a}}});".format(name=self.name, r=self.properties["color"][0], g=self.properties["color"][1], b=self.properties["color"][2], a=self.properties["color"][3])
		return init

	def activateType(self, type):
		enable = []
		disable = []

		if type == ELight.AMBIENT:
			enable = ["sc_color_r", "sc_color_g", "sc_color_b", "sc_color_a"]
			disable = ["sc_position_x", "sc_position_y", "sc_position_z", "sc_direction_x", "sc_direction_y", "sc_direction_z", "sc_attenuation_x", "sc_attenuation_y", "sc_attenuation_z"]
		elif type == ELight.DIFFUSE:
			enable = ["sc_direction_x", "sc_direction_y", "sc_direction_z", "sc_color_r", "sc_color_g", "sc_color_b", "sc_color_a"]
			disable = ["sc_position_x", "sc_position_y", "sc_position_z", "sc_attenuation_x", "sc_attenuation_y", "sc_attenuation_z"]
		elif type == ELight.POINT:
			enable = ["sc_position_x", "sc_position_y", "sc_position_z", "sc_attenuation_x", "sc_attenuation_y", "sc_attenuation_z", "sc_color_r", "sc_color_g", "sc_color_b", "sc_color_a"]
			disable = ["sc_direction_x", "sc_direction_y", "sc_direction_z"]
		elif type == ELight.SPOT:
			enable = ["sc_position_x", "sc_position_y", "sc_position_z", "sc_direction_x", "sc_direction_y", "sc_direction_z", "sc_attenuation_x", "sc_attenuation_y", "sc_attenuation_z", "sc_color_r", "sc_color_g", "sc_color_b", "sc_color_a"]
			disable = []

		for e in enable:
			self.inputs[e].Enable(True)
		for e in disable:
			self.inputs[e].Enable(False)
	def getCurrentColor(self):
		sc_color_r = self.inputs["sc_color_r"]
		sc_color_g = self.inputs["sc_color_g"]
		sc_color_b = self.inputs["sc_color_b"]
		sc_color_a = self.inputs["sc_color_a"]
		return (sc_color_r.GetValue(), sc_color_g.GetValue(), sc_color_b.GetValue(), sc_color_a.GetValue())
	def updateColorButton(self):
		bt_color = self.inputs["bt_color"]
		bt_color.SetBackgroundColour(self.getCurrentColor())

	def initPageSpecific(self):
		self.gbs = wx.GridBagSizer(12, 2)

		self.pageAddStatictext("Name:", (0,0))
		self.pageAddTextctrl("tc_name", self.name, (1,0), (1,2))

		self.pageAddStatictext("Type:", (2,0))
		self.pageAddChoice("ch_type", ["Ambient", "Diffuse", "Point", "Spot"], self.properties["type"]-1, (2,1))

		self.pageAddStatictext("Position:", (3,0))
		self.pageAddSpinctrl("sc_position_x", None, None, self.properties["position"][0], (3,1))
		self.pageAddSpinctrl("sc_position_y", None, None, self.properties["position"][1], (3,2))
		self.pageAddSpinctrl("sc_position_z", None, None, self.properties["position"][2], (3,3))

		self.pageAddStatictext("Direction:", (4,0))
		self.pageAddSpinctrl("sc_direction_x", None, None, self.properties["direction"][0], (4,1))
		self.pageAddSpinctrl("sc_direction_y", None, None, self.properties["direction"][1], (4,2))
		self.pageAddSpinctrl("sc_direction_z", None, None, self.properties["direction"][2], (4,3))

		self.pageAddStatictext("Attenuation:", (5,0))
		self.pageAddSpinctrl("sc_attenuation_x", None, None, self.properties["attenuation"][0], (5,1))
		self.pageAddSpinctrl("sc_attenuation_y", None, None, self.properties["attenuation"][1], (5,2))
		self.pageAddSpinctrl("sc_attenuation_z", None, None, self.properties["attenuation"][2], (5,3))

		self.pageAddStatictext("Color (RGBA):", (6,0))
		self.pageAddSpinctrl("sc_color_r", 0, 255, self.properties["color"][0], (6,1))
		self.pageAddSpinctrl("sc_color_g", 0, 255, self.properties["color"][1], (6,2))
		self.pageAddSpinctrl("sc_color_b", 0, 255, self.properties["color"][2], (6,3))
		self.pageAddSpinctrl("sc_color_a", 0, 255, self.properties["color"][3], (6,4))
		bt_color = self.pageAddButton("bt_color", "Color Picker", (6,5))
		bt_color.SetBackgroundColour(self.properties["color"][0:3])

		self.pageAddButton("bt_ok", "OK", (7,0))

		self.sizer = wx.BoxSizer()
		self.sizer.Add(self.gbs, 1, wx.ALL | wx.EXPAND, 20)
		self.page.SetSizer(self.sizer)

		self.activateType(self.properties["type"])

	def onTextSpecific(self, event):
		return True
	def onButtonSpecific(self, event):
		bt = event.GetEventObject()
		if bt == self.inputs["bt_ok"]:
			self.destroyPage()
		elif bt == self.inputs["bt_color"]:
			dialog = wx.ColourDialog(self.page)
			dialog.GetColourData().SetColour(wx.Colour(self.getCurrentColor()))

			if dialog.ShowModal() == wx.ID_OK:
				color = dialog.GetColourData().GetColour().Get(True)
				self.inputs["sc_color_r"].SetValue(color[0])
				self.inputs["sc_color_g"].SetValue(color[1])
				self.inputs["sc_color_b"].SetValue(color[2])
				#self.inputs["sc_color_a"].SetValue(color[3])

				self.updateColorButton()
			else:
				dialog.Destroy()
				return False

			dialog.Destroy()

		return True
	def onSpinCtrlSpecific(self, event):
		sc = event.GetEventObject()
		if sc in [self.inputs["sc_color_"+c] for c in ["r", "g", "b", "a"]]: # For sc_color_r, _g, _b, and _a
			self.updateColorButton()

		return True
	def onChoiceSpecific(self, event):
		ch = event.GetEventObject()
		if ch == self.inputs["ch_type"]:
			self.properties["type"] = ch.GetSelection()+1
			self.activateType(self.properties["type"])

		return True

	def update(self):
		pass

	def commitPage(self):
		if self.page:
			tc_name = self.inputs["tc_name"]
			if tc_name.GetValue() != self.name:
				self.rename(tc_name.GetValue())

			ch_type = self.inputs["ch_type"]
			self.properties["type"] = ch_type.GetSelection()+1

			sc_position_x = self.inputs["sc_position_x"]
			sc_position_y = self.inputs["sc_position_y"]
			sc_position_z = self.inputs["sc_position_z"]
			self.properties["position"] = (sc_position_x.GetValue(), sc_position_y.GetValue(), sc_position_z.GetValue())

			sc_direction_x = self.inputs["sc_direction_x"]
			sc_direction_y = self.inputs["sc_direction_y"]
			sc_direction_z = self.inputs["sc_direction_z"]
			self.properties["direction"] = (sc_direction_x.GetValue(), sc_direction_y.GetValue(), sc_direction_z.GetValue())

			sc_attenuation_x = self.inputs["sc_attenuation_x"]
			sc_attenuation_y = self.inputs["sc_attenuation_y"]
			sc_attenuation_z = self.inputs["sc_attenuation_z"]
			self.properties["attenuation"] = (sc_attenuation_x.GetValue(), sc_attenuation_y.GetValue(), sc_attenuation_z.GetValue())

			sc_color_r = self.inputs["sc_color_r"]
			sc_color_g = self.inputs["sc_color_g"]
			sc_color_b = self.inputs["sc_color_b"]
			sc_color_a = self.inputs["sc_color_a"]
			self.properties["color"] = (sc_color_r.GetValue(), sc_color_g.GetValue(), sc_color_b.GetValue(), sc_color_a.GetValue())
	def moveTo(self, name, newfile):
		"""if self.properties["path"]:
			ext = os.path.splitext(self.properties["path"])[1]
			os.rename(self.top.tmpDir+self.properties["path"], newfile+ext)
			self.properties["path"] = self.path+name+ext
			self.inputs["st_path"].SetLabel("Path: {}".format(self.properties["path"]))"""

	def MenuDuplicate(self, event):
		r = BEEFLight(self.top, None)
		r.properties = copy.deepcopy(self.properties)
		self.top.addLight(self.name, r)
