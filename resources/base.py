# Copyright (c) 2017 Luke Montalvo <lukemontalvo@gmail.com>
#
# This file is part of BEE.
# BEE is free software and comes with ABSOLUTELY NO WARANTY.
# See LICENSE for more details.

try:
	import wx
except ImportError:
	raise ImportError("The wxPython module is required to run this program")

import json
import os

from ui.listctrl import BEEFListCtrl
from ui.validators import BEEFValidatorGeneric
from ui.plot import BEEFPlot
from ui.editor import BEEFEditor

class BEEFBaseResource:
	def __init__(self, top, name):
		self.top = top
		self.gid = -1
		self.path = "/resources/"
		self.resourceList = None

		self.type = -1
		self.treeitem = None
		self.page = None
		self.pageIndex = -1
		self.inputs = {}

		self.id = -1
		self.name = name
		self.properties = {}

	def initPage(self):
		if self.page:
			if self.pageIndex < 0:
				self.pageIndex = self.top.notebook.GetPageCount()
				self.top.notebook.AddPage(self.page, self.name)
				self.top.gameCfg["open_resources"].append(self.name)

			self.top.notebook.SetSelection(self.pageIndex)
			return

		self.pageIndex = self.top.notebook.GetPageCount()

		self.page = wx.Panel(self.top.notebook)

		self.initPageSpecific()

		self.top.notebook.AddPage(self.page, self.name)
		self.top.notebook.SetSelection(self.pageIndex)
		if not self.name in self.top.gameCfg["open_resources"]:
			self.top.gameCfg["open_resources"].append(self.name)

		self.top.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CLOSED, self.destroyPage, self.top.notebook)
	def destroyPage(self, event=None, isClosing=False):
		if self.page:
			if isClosing:
				self.input = {}
				self.page = None
			else:
				self.commitPage()

				if self.name in self.top.gameCfg["open_resources"]:
					self.top.gameCfg["open_resources"].remove(self.name)
				self.top.notebook.DeletePage(self.pageIndex)

				self.top.adjustIndices(self.pageIndex)
				self.pageIndex = -1
				self.top.setUnsaved()

	def pageMakeStatictext(self, text, name=""):
		st = None
		if name:
			self.inputs[name] = wx.StaticText(self.page, -1, text)
			st = self.inputs[name]
		else:
			st = wx.StaticText(self.page, -1, text)

		return st
	def pageMakeTextctrl(self, name, text):
		self.inputs[name] = wx.TextCtrl(self.page, -1, text)
		tc = self.inputs[name]

		wx.CallAfter(tc.SetInsertionPoint, 0)

		self.page.Bind(wx.EVT_TEXT, self.onText, tc)

		return tc
	def pageMakeCheckbox(self, name, text, value):
		self.inputs[name] = wx.CheckBox(self.page, -1, text)
		cb = self.inputs[name]

		if value:
			cb.SetValue(True)

		self.page.Bind(wx.EVT_CHECKBOX, self.onCheckBox, cb)

		return cb
	def pageMakeButton(self, name, text):
		self.inputs[name] = wx.Button(self.page, -1, text)
		bt = self.inputs[name]

		self.page.Bind(wx.EVT_BUTTON, self.onButton, bt)

		return bt
	def pageMakeBitmap(self, name, filename, imgsize=(16,16)):
		self.inputs[name] = wx.StaticBitmap(self.page, size=imgsize)
		bmp = self.inputs[name]

		if os.path.isfile(filename):
			img = wx.Image(filename)
			img.Rescale(*imgsize)
			bmp.SetBitmap(wx.Bitmap(img))
		else:
			bmp.SetBitmap(wx.Bitmap(self.top.images["noimage"]))

		return bmp
	def pageMakeSlider(self, name, value, minvalue=0, maxvalue=100):
		self.inputs[name] = wx.Slider(self.page, -1, value, minvalue, maxvalue, size=(200, -1), style=wx.SL_HORIZONTAL | wx.SL_LABELS)
		sl = self.inputs[name]

		self.page.Bind(wx.EVT_SLIDER, self.onSlider, sl)

		return sl
	def pageMakeBmpbutton(self, name, filename, imgsize=(16,16), tooltip=""):
		bmp = None
		if os.path.isfile(filename):
			img = wx.Image(filename)
			img.Rescale(*imgsize)
			bmp = wx.Bitmap(img)
		else:
			bmp = wx.Bitmap(self.top.images["noimage"])

		self.inputs[name] = wx.BitmapButton(self.page, -1, bmp)
		bt = self.inputs[name]

		bt.SetToolTip(tooltip)
		self.page.Bind(wx.EVT_BUTTON, self.onButton, bt)

		return bt
	def pageMakeSpinctrl(self, name, min, max, value):
		self.inputs[name] = wx.SpinCtrl(self.page)
		sc = self.inputs[name]

		sc.SetRange(min, max)
		sc.SetValue(value)

		self.page.Bind(wx.EVT_SPINCTRL, self.onSpinCtrl, sc)
		self.page.Bind(wx.EVT_TEXT, self.onText, sc)

		return sc
	def pageMakeListCtrl(self, name, columns):
		self.inputs[name] = BEEFListCtrl(self.page, style=wx.LC_REPORT | wx.LC_EDIT_LABELS)
		lst = self.inputs[name]

		i = 0
		for c in columns:
			lst.InsertColumn(i, c)
			i += 1

		lst.SetValidators(BEEFValidatorGeneric())

		def _onListEdit(evt, source=lst):
			return self.onListEdit(evt, source)
		self.page.Bind(wx.EVT_LIST_END_LABEL_EDIT, _onListEdit)
		self.page.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onListSelect)

		return lst
	def pageMakePlot(self, name):
		self.inputs[name] = BEEFPlot(self.page)
		return self.inputs[name]
	def pageMakeEditor(self, name):
		self.inputs[name] = BEEFEditor(self.top, self.page)
		return self.inputs[name]

	def pageAddStatictext(self, text, pos, size=(1,1), name=""):
		st = self.pageMakeStatictext(text, name)
		self.gbs.Add(st, pos, size)
		return st
	def pageAddTextctrl(self, name, text, pos, size=(1,1)):
		tc = self.pageMakeTextctrl(name, text)
		self.gbs.Add(tc, pos, size, flag=wx.EXPAND)
		return tc
	def pageAddCheckbox(self, name, text, pos, value):
		cb = self.pageMakeCheckbox(name, text, value)
		self.gbs.Add(cb, pos)
		return cb
	def pageAddButton(self, name, text, pos, size=(1,1)):
		bt = self.pageMakeButton(name, text)
		self.gbs.Add(bt, pos, size)
		return bt
	def pageAddBitmap(self, name, filename, pos, size=(1,1), imgsize=(16,16)):
		bmp = self.pageMakeBitmap(name, filename, imgsize)
		self.gbs.Add(bmp, pos, size)
		return bmp
	def pageAddSlider(self, name, value, pos, size=(1,1), minvalue=0, maxvalue=100):
		sl = self.pageMakeSlider(name, value, minvalue, maxvalue)
		self.gbs.Add(sl, pos, size)
		return sl
	def pageAddBmpbutton(self, name, filename, pos, size=(1,1), imgsize=(16,16), tooltip=""):
		bt = self.pageMakeBmpbutton(name, file, imgsize, tooltip)
		self.gbs.Add(bt, pos, size)
		return bt
	def pageAddSpinctrl(self, name, min, max, value, pos, size=(1,1)):
		sc = self.pageMakeSpinctrl(name, min, max, value)
		self.gbs.Add(sc, pos, size)
		return sc
	def pageAddListCtrl(self, name, columns, pos, size=(1,1), flag=wx.EXPAND):
		lst = self.pageMakeListCtrl(name, columns)
		self.gbs.Add(lst, pos, size, flag=flag)
		return lst
	def pageAddPlot(self, name, pos, size=(1,1), flag=wx.EXPAND):
		pl = self.pageMakePlot(name)
		self.gbs.Add(pl, pos, size, flag=flag)
		return pl
	def pageAddEditor(self, name, pos, size=(1,1), flag=wx.EXPAND):
		ed = self.pageMakeEditor(name)
		self.gbs.Add(ed, pos, size, flag=flag)
		return ed

	def addListRow(self, name, rowData, isSortable=True):
		lst = self.inputs[name]

		pos = lst.InsertItem(lst.GetItemCount(), rowData[0])
		if isSortable:
			lst.SetItemData(pos, int(rowData[0]))

		for i in range(1, len(rowData)):
			lst.SetItem(pos, i, rowData[i])
	def removeListRow(self, name, rowIndex):
		lst = self.inputs[name]

		if rowIndex < 0:
			rowIndex = lst.GetFirstSelected()

		if rowIndex >= 0:
			lst.DeleteItem(rowIndex)

		if rowIndex < lst.GetItemCount():
			lst.Select(rowIndex)
		else:
			lst.Select(lst.GetItemCount()-1)

	def onText(self, event):
		if self.onTextSpecific(event):
			self.top.setUnsaved()
	def onCheckBox(self, event):
		if self.onCheckBoxSpecific(event):
			self.top.setUnsaved()
	def onButton(self, event):
		if self.onButtonSpecific(event):
			self.top.setUnsaved()
	def onSlider(self, event):
		if self.onSliderSpecific(event):
			self.top.setUnsaved()
	def onSpinCtrl(self, event):
		if self.onSpinCtrlSpecific(event):
			self.top.setUnsaved()
	def onListEdit(self, event, source):
		# Editable ListCtrls do not properly implement validators
		if not source.IsValid(event.GetItem().GetColumn(), event.GetItem().GetText()):
			event.Veto()
			return

		if self.onListEditSpecific(event):
			self.top.setUnsaved()
	def onListSelect(self, event):
		if self.onListSelectSpecific(event):
			self.top.setUnsaved()

	def onTextSpecific(self, event):
		return False
	def onCheckBoxSpecific(self, event):
		return False
	def onButtonSpecific(self, event):
		return False
	def onSliderSpecific(self, event):
		return False
	def onSpinCtrlSpecific(self, event):
		return False
	def onListEditSpecific(self, event):
		return False
	def onListSelectSpecific(self, event):
		return False

	def serialize(self):
		return json.dumps({
			"id": self.id,
			"name": self.name,
			"properties": self.properties
		}, indent=4)
	def deserialize(self, data):
		s = json.loads(data)

		self.id = s["id"]
		self.name = s["name"]
		self.properties = s["properties"]

	def checkName(self, name, shouldDelete=True):
		path = self.top.tmpDir+self.path+name+".json"
		for r in self.resourceList:
			if r and (not r == self) and (r.name == name):
				if shouldDelete:
					if not self.top.confirmOverwriteResource(path, name):
						return False

					r.MenuDelete(None)
					break
				else:
					return False

		return True
	def rename(self, name):
		if name == self.name:
			return True

		if not self.checkName(name):
			return False

		oldfile = self.top.tmpDir+self.path+self.name
		newfile = self.top.tmpDir+self.path+name
		if os.path.isfile(oldfile+".json"):
			os.remove(oldfile+".json")
		self.moveTo(name, newfile)

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

	def MenuOpen(self, event):
		self.initPage()
	def MenuRename(self, event):
		self.top.treectrl.EditLabel(self.treeitem)
	def MenuDelete(self, event):
		self.top.setUnsaved()

		self.destroyPage()

		self.resourceList[self.id] = None
		oldfile = self.top.tmpDir+self.path+self.name+".json"
		if os.path.isfile(oldfile):
			os.remove(oldfile)

		self.top.treectrl.Delete(self.treeitem)
	def MenuDuplicate(self, event):
		pass # See implementation in specific resource file
