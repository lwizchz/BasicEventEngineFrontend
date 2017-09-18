# Copyright (c) 2017 Luke Montalvo <lukemontalvo@gmail.com>
#
# This file is part of BEE.
# BEE is free software and comes with ABSOLUTELY NO WARANTY.
# See LICENSE for more details.

try:
	import wx
except ImportError:
	raise ImportError("The wxPython module is required to run this program")

class BEEFValidatorGeneric(wx.Validator):
	def __init__(self):
		wx.Validator.__init__(self)
	def Clone(self):
		return BEEFValidatorGeneric()
	def Validate(self, win):
		textCtrl = self.GetWindow()
		text = textCtrl.GetValue()
		return IsValid(text)
	def IsValid(self, text):
		return True

	def TransferToWindow(self):
		return True
	def TransferFromWindow(self):
		return True

class BEEFValidatorInt(BEEFValidatorGeneric):
	def __init__(self):
		BEEFValidatorGeneric.__init__(self)
	def Clone(self):
		return BEEFValidatorInt()
	def IsValid(self, text):
		try:
			int(text)
		except ValueError:
			if len(text):
				return False
		return True
class BEEFValidatorFloat(BEEFValidatorGeneric):
	def __init__(self):
		BEEFValidatorGeneric.__init__(self)
	def Clone(self):
		return BEEFValidatorFloat()
	def IsValid(self, text):
		try:
			float(text)
		except ValueError:
			if len(text):
				return False
		return True

class BEEFValidatorAlpha(BEEFValidatorGeneric):
	def __init__(self):
		BEEFValidatorGeneric.__init__(self)
	def Clone(self):
		return BEEFValidatorAlpha()
	def isValid(self, text):
		if not text.isalpha() and len(text):
			return False
		return True
class BEEFValidatorAlphanumeric(BEEFValidatorGeneric):
	def __init__(self):
		BEEFValidatorGeneric.__init__(self)
	def Clone(self):
		return BEEFValidatorAlphanumeric()
	def isValid(self, text):
		if not text.isalnum() and len(text):
			return False
		return True
class BEEFValidatorIdentifier(BEEFValidatorGeneric):
	def __init__(self):
		BEEFValidatorGeneric.__init__(self)
	def Clone(self):
		return BEEFValidatorIdentifier()
	def isValid(self, text):
		if not text.isidentifier() and len(text):
			return False
		return True
