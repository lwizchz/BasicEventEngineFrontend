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
from resources.enum import EEvent

from ui.eventdialog import BEEFEventDialog

class BEEFObject(BEEFBaseResource):
	def __init__(self, top, name):
		BEEFBaseResource.__init__(self, top, name)
		self.path = "/resources/objects/"
		self.type = 8
		self.properties = {
			"sprite": "",
			"is_solid": False,
			"is_visible": True,
			"is_persistent": False,
			"depth": 0,
			"parent": "",
			"mask": "",
			"xoffset": 0,
			"yoffset": 0,
			"is_pausable": True,
			"events": {} # Each event is as follows: (eventType: "code")
		}
		self.tmpEvents = {} # Each tmpEvent is as follows: (eventType: [listIndex, "code", lastPosition])
		self.lastSelected = -1
		self.initialEventCode = "void {objname}::{event}({params}) {const}{{\n\t\n}}\n"

	def getNewEvent(self):
		newEvent = ""

		dialog = BEEFEventDialog(self.page)
		if dialog.ShowModal() == wx.ID_OK:
			newEvent = dialog.getEventStr()

		dialog.Destroy()
		return newEvent
	def getSelectedEvent(self, index):
		for event, data in self.tmpEvents.items():
			if data[0] == index:
				return event
		else:
			return -1
	def changeSelection(self, index):
		ed = self.inputs["ed_event"]
		if 0 <= self.lastSelected < len(self.tmpEvents):
			self.tmpEvents[self.getSelectedEvent(self.lastSelected)][1] = ed.GetText()
		self.lastSelected = index
		ed.SetText(self.tmpEvents[self.getSelectedEvent(self.lastSelected)][1])
		ed.EmptyUndoBuffer()

	def getImplementedEvents(self):
		return ["bee::E_EVENT::{}".format(EEvent.get(event).upper().replace(" ", "_")) for event, data in self.tmpEvents.items()]
	def getEvents(self):
		return [data[1] for event, data in self.tmpEvents.items()]
	def getEventHeaders(self):
		def getConst(event):
			if event == EEvent.getIndex("Check Collision Filter"):
				return " const"
			return ""

		return ["void {event}({params}){const};".format(event=EEvent.get(event).lower().replace(" ", "_"), params=EEvent.getParamTypes(EEvent.get(event)), const=getConst(event)) for event, data in self.tmpEvents.items()]
	def getInit(self):
		init = ""
		#if self.properties["is_solid"]:
		#	init += "\n\t\t\t{name}->set_is_solid(true);".format(name=self.name)
		if self.properties["is_persistent"]:
			init += "\n\t\t\t{name}->set_is_persistent(true);".format(name=self.name)
		if self.properties["sprite"]:
			init += "\n\t\t\t{name}->set_sprite({sprite});".format(name=self.name, sprite=self.properties["sprite"])
		#if self.properties["mask"]:
		#	init += "\n\t\t\t{name}->set_mask({mask});".format(name=self.name, mask=self.properties["mask"])
		return init

	def initPageSpecific(self):
		self.gbs = wx.GridBagSizer(12, 2)

		# Column 1
		self.pageAddStatictext("Name:", (0,0))
		self.pageAddTextctrl("tc_name", self.name, (1,0), (1,2))

		self.pageAddStatictext("Sprite:", (2,0))
		spriteList = [""] + [s.name for s in self.top.sprites]
		spriteIndex = -1
		try:
			spriteIndex = spriteList.index(self.properties["sprite"])
		except ValueError:
			pass
		self.pageAddChoice("ch_sprite", spriteList, spriteIndex, (2,1))

		self.pageAddCheckbox("cb_is_persistent", "Persistent", (3,0), self.properties["is_persistent"])

		lst = self.pageAddListCtrl("lst_events", ["Events"], (4,0), (1,2)) # Perhaps replace with a Grid
		lst.SetColumnWidth(0, lst.GetSize()[0]/2)

		self.tmpEvents = {}
		firstEventCode = ""
		index = 0
		for event, code in self.properties["events"].items():
			event = int(event)
			self.addListRow("lst_events", [EEvent.get(event)], isSortable=False)
			self.tmpEvents[event] = [index, code, 0]

			if index == 0:
				firstEventCode = code

			index += 1

		self.pageAddButton("bt_add_event", "Add Event", (5,0))
		self.pageAddButton("bt_remove_event", "Remove Event", (5,1))

		self.pageAddButton("bt_ok", "OK", (6,0))

		# Column 2
		self.lastSelected = -1
		ed = self.pageAddEditor("ed_event", (0,3), (6,1))
		if len(self.tmpEvents) > 0:
			ed.SetText(firstEventCode)
			lst.Select(0)
			self.lastSelected = 0
		else:
			ed.Enable(False)

		self.gbs.AddGrowableRow(4)
		self.gbs.AddGrowableCol(3)
		self.sizer = wx.BoxSizer()
		self.sizer.Add(self.gbs, 1, wx.ALL | wx.EXPAND, 20)
		self.page.SetSizer(self.sizer)

	def onTextSpecific(self, event):
		tc = event.GetEventObject()
		if tc == self.inputs["tc_name"]:
			pass # TODO: Handle name changes within the user's code
		return True
	def onCheckBoxSpecific(self, event):
		return True
	def onButtonSpecific(self, event):
		bt = event.GetEventObject()
		if bt == self.inputs["bt_ok"]:
			self.destroyPage()
		elif bt == self.inputs["bt_add_event"]:
			newEvent = self.getNewEvent()
			if not newEvent:
				return False
			if EEvent.getIndex(newEvent) in self.tmpEvents:
				self.inputs["lst_events"].Select(self.lastSelected, False)
				self.changeSelection(self.tmpEvents[EEvent.getIndex(newEvent)][0])
				self.inputs["lst_events"].Select(self.lastSelected, True)

				return False

			self.inputs["ed_event"].Enable(True)

			if 0 <= self.lastSelected < len(self.tmpEvents):
				for event, data in self.tmpEvents.items():
					if data[0] == self.lastSelected:
						data[1] = self.inputs["ed_event"].GetText()
						break

			self.addListRow("lst_events", [newEvent], isSortable=False)

			c = ""
			if newEvent in ["Check Collision Filter"]:
				c = "const "
			initialCode = self.initialEventCode.format(objname=self.name.replace("_", " ").title().replace(" ", ""), event=newEvent.lower().replace(" ", "_"), params=EEvent.getParams(newEvent), const=c)

			self.lastSelected = len(self.tmpEvents)
			for i in range(self.lastSelected):
				self.inputs["lst_events"].Select(i, False)
			self.inputs["lst_events"].Select(self.lastSelected)
			self.tmpEvents[EEvent.getIndex(newEvent)] = [self.lastSelected, initialCode, len(initialCode) - 3]

			ed = self.inputs["ed_event"]
			ed.SetText(initialCode)
			ed.EmptyUndoBuffer()
			ed.SetFocus()
			ed.GotoPos(self.tmpEvents[self.getSelectedEvent(self.lastSelected)][2])
		elif bt == self.inputs["bt_remove_event"] and len(self.tmpEvents):
			index = self.inputs["lst_events"].GetFirstSelected()
			if index == -1:
				index = self.inputs["lst_events"].GetItemCount()-1

			self.removeListRow("lst_events", index)
			if self.getSelectedEvent(index) >= 0:
				del self.tmpEvents[self.getSelectedEvent(index)]

			for event, data in self.tmpEvents.items():
				if data[0] > index:
					data[0] -= 1

			ed = self.inputs["ed_event"]
			index = max(index-1, 0)
			if len(self.tmpEvents):
				self.lastSelected = index
				ed.SetText(self.tmpEvents[self.getSelectedEvent(index)][1])
			else:
				self.lastSelected = -1
				ed.SetText("")
				ed.Enable(False)
			ed.EmptyUndoBuffer()

		return True
	def onChoiceSpecific(self, event):
		return True
	def onListEditSpecific(self, event):
		event.Veto()
		return False
	def onListSelectSpecific(self, event):
		if event.GetIndex() < len(self.tmpEvents):
			self.changeSelection(event.GetIndex())
			ed = self.inputs["ed_event"]
			ed.SetFocus()
			ed.GotoPos(self.tmpEvents[self.getSelectedEvent(self.lastSelected)][2])
		return False
	def onEditorSpecific(self, event):
		if self.lastSelected >= 0:
			ed = self.inputs["ed_event"]
			self.tmpEvents[self.getSelectedEvent(self.lastSelected)][2] = ed.GetCurrentPos()
		return True

	def update(self):
		pass

	def commitPage(self):
		if self.page:
			tc_name = self.inputs["tc_name"]
			if tc_name.GetValue() != self.name:
				self.rename(tc_name.GetValue())

			ch = self.inputs["ch_sprite"]
			self.properties["sprite"] = ch.GetString(ch.GetSelection())
			self.properties["is_persistent"] = self.inputs["cb_is_persistent"].GetValue()

			if 0 <= self.lastSelected < len(self.tmpEvents):
				self.tmpEvents[self.getSelectedEvent(self.lastSelected)][1] = self.inputs["ed_event"].GetText()

			self.properties["events"] = {}
			for event, data in self.tmpEvents.items():
				self.properties["events"][event] = data[1]
	def moveTo(self, name, newfile):
		"""if self.properties["path"]:
			ext = os.path.splitext(self.properties["path"])[1]
			os.rename(self.top.tmpDir+self.properties["path"], newfile+ext)
			self.properties["path"] = self.path+name+ext
			self.inputs["st_path"].SetLabel("Path: {}".format(self.properties["path"]))"""

	def MenuDuplicate(self, event):
		r = BEEFObject(self.top, None)
		r.properties = copy.deepcopy(self.properties)
		self.top.addObject(self.name, r)
