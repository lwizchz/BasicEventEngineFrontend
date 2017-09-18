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

class BEEFRoom(BEEFBaseResource):
	def __init__(self, top, name):
		BEEFBaseResource.__init__(self, top, name)
		self.path = "/resources/rooms/"
		self.type = 9

	def MenuDuplicate(self, event):
		r = BEEFRoom(self.top, None)
		r.properties = copy.deepcopy(self.properties)
		self.top.addRoom(self.name, r)
