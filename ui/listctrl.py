# Copyright (c) 2017-18 Luke Montalvo <lukemontalvo@gmail.com>
#
# This file is part of BEEF.
# BEEF is free software and comes with ABSOLUTELY NO WARANTY.
# See LICENSE for more details.

try:
	import wx
except ImportError:
	raise ImportError("The wxPython module is required to run this program")

from ui.listeditmixin import TextEditMixin

from ui.validators import BEEFValidatorGeneric

class BEEFListCtrl(wx.ListCtrl, TextEditMixin):
	def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.LC_ICON, validator=BEEFValidatorGeneric(), name=wx.ListCtrlNameStr):
		wx.ListCtrl.__init__(self, parent, id, pos, size, style, validator, name)
		TextEditMixin.__init__(self)
		self._validators = []
		self._sortColumn = 0

	def SetValidators(self, validator):
		self._validators = []
		for _ in range(self.GetColumnCount()):
			self._validators.append(validator.Clone())
	def SetValidator(self, column, validator):
		self._validators[column] = validator.Clone()
	def IsValid(self, column, text):
		return self._validators[column].IsValid(text)

	def GetItemList(self):
		l = []
		for i in range(self.GetItemCount()):
			item = [self.GetItem(i).GetText()]
			for j in range(1, self.GetColumnCount()):
				item.append(self.GetItem(i, j).GetText())
			l.append(tuple(item))
		return l

	def SortBy(self, column):
		self._sortColumn = column
		self.SortItems(self._ListCompareFunction)
	def _ListCompareFunction(self, item1, item2):
		return item1 - item2
