# Copyright (c) 2017 Luke Montalvo <lukemontalvo@gmail.com>
#
# This file is part of BEE.
# BEE is free software and comes with ABSOLUTELY NO WARANTY.
# See LICENSE for more details.

try:
	import wx
except ImportError:
	raise ImportError("The wxPython module is required to run this program")

class BEEFPlot(wx.Panel):
	def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.LC_ICON, scale=2):
		wx.Panel.__init__(self, parent, id, pos, size, style)
		self.SetBackgroundColour(wx.WHITE)

		size = self.GetSize()
		size = (size.GetWidth(), size.GetHeight())
		self.ox = size[0]/2
		self.oy = size[1]/2
		self.scale = scale
		self.coords = []

		self.Bind(wx.EVT_SIZE, self.OnSize)
		self.Bind(wx.EVT_PAINT, self.Redraw)

	def SetCoords(self, coords):
		self.coords = []
		for c in coords:
			self.coords.append(c)

	def OnSize(self, event):
		size = self.GetSize()
		size = (size.GetWidth(), size.GetHeight())
		self.ox = size[0]/2
		self.oy = size[1]/2

		self.Redraw()
	def GetInt(self, s):
		return int(round(float(s)))
	def Redraw(self, event=None):
		if not event:
			self.Refresh()
			self.Update()
			return

		# Create lists for drawing
		w = 2/self.scale
		points = []
		lines = []

		for i in range(len(self.coords)):
			c1 = self.coords[i]
			points.append((
				self.GetInt(c1[0])-w/2, self.GetInt(c1[1])-w/2,
				w, w
			))

		lines.append((-self.ox, 0, self.ox, 0)) # Axis lines
		lines.append((0, -self.oy, 0, self.oy))
		for i in range(len(self.coords)):
			if i+1 >= len(self.coords):
				break

			c1 = self.coords[i]
			c2 = self.coords[i+1]

			lines.append((
				self.GetInt(c1[0]), self.GetInt(c1[1]),
				self.GetInt(c2[0]), self.GetInt(c2[1]),
			))

		# Draw the lists
		dc = wx.PaintDC(self)
		dc.Clear()

		dc.SetLogicalScale(self.scale, self.scale)
		dc.SetLogicalOrigin(-self.ox/self.scale, -self.oy/self.scale)

		dc.SetPen(wx.Pen(wx.BLACK, w))
		dc.DrawLineList(lines)
		dc.SetPen(wx.Pen(wx.RED, w))
		dc.DrawRectangleList(points)
