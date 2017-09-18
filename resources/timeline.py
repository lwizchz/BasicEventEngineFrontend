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

from ui.validators import BEEFValidatorInt
from ui.validators import BEEFValidatorIdentifier

class BEEFTimeline(BEEFBaseResource):
	def __init__(self, top, name):
		BEEFBaseResource.__init__(self, top, name)
		self.path = "/resources/timelines/"
		self.type = 5
		self.properties = {
			"actions": [], # Each action is the following: (timestamp, "name", "code")
			"end_action": ""
		}
		self.tmpActions = []
		self.lastSelected = -1

	def initPageSpecific(self):
		self.gbs = wx.GridBagSizer(12, 2)

		# Column 1
		self.pageAddStatictext("Name:", (0,0))
		self.pageAddTextctrl("tc_name", self.name, (1,0), (1,2))

		lst = self.pageAddListCtrl("lst_actions", ["Time", "Name"], (2,0), (1,2)) # Perhaps replace with a Grid
		lst.SetValidator(0, BEEFValidatorInt())
		lst.SetValidator(1, BEEFValidatorIdentifier())

		self.tmpActions = []
		for time, name, code in self.properties["actions"]:
			self.addListRow("lst_actions", (time, name))
			self.tmpActions.append(code)

		self.pageAddButton("bt_add_action", "Add Action", (3,0))
		self.pageAddButton("bt_remove_action", "Remove Action", (3,1))

		self.pageAddButton("bt_ok", "OK", (4,0))

		# Column 2
		self.lastSelected = -1
		ed = self.pageAddEditor("ed_action", (0,3), (4,1))
		if len(self.tmpActions) > 0:
			ed.SetText(self.tmpActions[0])
			lst.Select(0)
			self.lastSelected = 0
		else:
			ed.Enable(False)

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
		elif bt == self.inputs["bt_add_action"]:
			self.inputs["ed_action"].Enable(True)

			if 0 <= self.lastSelected < len(self.tmpActions):
				self.tmpActions[self.lastSelected] = self.inputs["ed_action"].GetText()

			self.addListRow("lst_actions", ("0", "anonymous"))

			self.lastSelected = len(self.tmpActions)
			for i in range(self.lastSelected):
				self.inputs["lst_actions"].Select(i, False)
			self.inputs["lst_actions"].Select(self.lastSelected)
			self.tmpActions.append("")

			ed = self.inputs["ed_action"]
			ed.SetText("")
			ed.EmptyUndoBuffer()

			self.inputs["lst_actions"].SetColumnWidth(1, -1)
		elif bt == self.inputs["bt_remove_action"] and len(self.tmpActions):
			self.removeListRow("lst_actions", -1)
			index = self.inputs["lst_actions"].GetFirstSelected()
			self.tmpActions.pop(index)

			ed = self.inputs["ed_action"]
			index = max(index-1, 0)
			if len(self.tmpActions):
				self.lastSelected = index
				ed.SetText(self.tmpActions[index])
			else:
				self.lastSelected = -1
				ed.SetText("")
				ed.Enable(False)
			ed.EmptyUndoBuffer()

			self.inputs["lst_actions"].SetColumnWidth(1, -1)

		return True
	def onListEditSpecific(self, event):
		lst = self.inputs["lst_actions"]

		try:
			if event.GetItem().GetColumn() == 0 and 0 <= event.GetItem().GetId() < lst.GetItemCount():
				lst.SetItemData(event.GetItem().GetId(), int(lst.GetItemText(event.GetItem().GetId())))
		except ValueError:
			pass

		lst.SetColumnWidth(1, -1)
		lst.SortBy(0)

		return True
	def onListSelectSpecific(self, event):
		if event.GetIndex() < len(self.tmpActions):
			ed = self.inputs["ed_action"]
			if 0 <= self.lastSelected < len(self.tmpActions):
				self.tmpActions[self.lastSelected] = ed.GetText()
			self.lastSelected = event.GetIndex()
			ed.SetText(self.tmpActions[self.lastSelected])
			ed.EmptyUndoBuffer()

		return False

	def update(self):
		pass

	def commitPage(self):
		if self.page:
			tc_name = self.inputs["tc_name"]
			if tc_name.GetValue() != self.name:
				self.rename(tc_name.GetValue())

			if 0 <= self.lastSelected < len(self.tmpActions):
				self.tmpActions[self.lastSelected] = self.inputs["ed_action"].GetText()

			i = 0
			self.properties["actions"] = []
			for time, name in self.inputs["lst_actions"].GetItemList():
				self.properties["actions"].append((
					time,
					name,
					self.tmpActions[i]
				))
				i += 1
	def moveTo(self, name, newfile):
		"""if self.properties["path"]:
			ext = os.path.splitext(self.properties["path"])[1]
			os.rename(self.top.tmpDir+self.properties["path"], newfile+ext)
			self.properties["path"] = self.path+name+ext
			self.inputs["st_path"].SetLabel("Path: {}".format(self.properties["path"]))"""

	def MenuDuplicate(self, event):
		r = BEEFTimeline(self.top, None)
		r.properties = copy.deepcopy(self.properties)
		self.top.addTimeline(self.name, r)
